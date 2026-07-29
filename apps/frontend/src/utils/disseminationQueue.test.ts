/**
 * T2.1 / T2.3 — Interleaved dissemination queue tests (E18-10/11/15).
 */

import { describe, expect, it, vi } from 'vitest';

import type { ExportCandidate } from './exportSelection';
import {
  runDisseminationQueue,
  type DisseminationFileResult,
  type QueueSinkContext,
} from './disseminationQueue';
import type { PreflightResponse, SendResponse } from './dissemination';

function cand(id: string): ExportCandidate {
  return {
    id,
    name: `${id}.xml`,
    source: 'session',
    product: 'metar',
    iwxxmXml: `<${id}/>`,
  };
}

const sink: QueueSinkContext = {
  sinkType: 'postgres',
  uri: 'postgresql://u:p@db.example/iwxxm',
  ddl: false,
  product: 'metar',
};

function greenPre(handle: string): PreflightResponse {
  return {
    ok: true,
    connectivity_ok: true,
    diffs: [],
    handle,
  };
}

describe('runDisseminationQueue (interleaved E18-10)', () => {
  it('runs preflight then send per file before moving to the next', async () => {
    const order: string[] = [];
    const preflight = vi.fn(async (c: ExportCandidate) => {
      order.push(`pre:${c.id}`);
      return greenPre(`h-${c.id}`);
    });
    const send = vi.fn(async (c: ExportCandidate, handle: string) => {
      order.push(`send:${c.id}:${handle}`);
      const res: SendResponse = { ok: true, kv_upload_key: `kv:${c.id}` };
      return res;
    });

    const results: DisseminationFileResult[] = [];
    for await (const event of runDisseminationQueue({
      candidates: [cand('a'), cand('b')],
      mode: 'disseminate',
      sink,
      preflight,
      send,
    })) {
      if (event.type === 'file_done') results.push(event.result);
    }

    expect(order).toEqual(['pre:a', 'send:a:h-a', 'pre:b', 'send:b:h-b']);
    expect(results.map((r) => r.status)).toEqual(['success', 'success']);
  });

  it('continues remaining files after a preflight failure (E18-11)', async () => {
    const preflight = vi.fn(async (c: ExportCandidate) => {
      if (c.id === 'a') {
        return {
          ok: false,
          connectivity_ok: false,
          diffs: [],
          detail: 'deny',
        } satisfies PreflightResponse;
      }
      return greenPre(`h-${c.id}`);
    });
    const send = vi.fn(async () => ({ ok: true, kv_upload_key: 'kv' }));

    const results: DisseminationFileResult[] = [];
    for await (const event of runDisseminationQueue({
      candidates: [cand('a'), cand('b')],
      mode: 'disseminate',
      sink,
      preflight,
      send,
    })) {
      if (event.type === 'file_done') results.push(event.result);
    }

    expect(results).toHaveLength(2);
    expect(results[0]).toMatchObject({
      candidateId: 'a',
      status: 'failed',
      phase: 'preflight',
    });
    expect(results[1]).toMatchObject({
      candidateId: 'b',
      status: 'success',
    });
    expect(send).toHaveBeenCalledTimes(1);
  });

  it('continues after a send failure and reports red fail for that file', async () => {
    const preflight = vi.fn(async (c: ExportCandidate) => greenPre(`h-${c.id}`));
    const send = vi.fn(async (c: ExportCandidate) => {
      if (c.id === 'a') {
        throw new Error('upload failed');
      }
      return { ok: true, kv_upload_key: 'kv:b' };
    });

    const results: DisseminationFileResult[] = [];
    for await (const event of runDisseminationQueue({
      candidates: [cand('a'), cand('b')],
      mode: 'disseminate',
      sink,
      preflight,
      send,
    })) {
      if (event.type === 'file_done') results.push(event.result);
    }

    expect(results[0]).toMatchObject({
      candidateId: 'a',
      status: 'failed',
      phase: 'send',
      detail: 'upload failed',
    });
    expect(results[1]?.status).toBe('success');
  });

  it('emits progress events: pending → preflight → send → done', async () => {
    const phases: string[] = [];
    const preflight = vi.fn(async () => greenPre('h1'));
    const send = vi.fn(async () => ({ ok: true }));

    for await (const event of runDisseminationQueue({
      candidates: [cand('a')],
      mode: 'disseminate',
      sink,
      preflight,
      send,
    })) {
      if (event.type === 'progress') {
        phases.push(`${event.candidateId}:${event.phase}`);
      }
    }

    expect(phases).toEqual(['a:preflight', 'a:send']);
  });
});

describe('runDisseminationQueue modes (E18-15)', () => {
  it('preflight_only never calls send', async () => {
    const preflight = vi.fn(async () => greenPre('h1'));
    const send = vi.fn(async () => ({ ok: true }));

    const results: DisseminationFileResult[] = [];
    for await (const event of runDisseminationQueue({
      candidates: [cand('a'), cand('b')],
      mode: 'preflight_only',
      sink,
      preflight,
      send,
    })) {
      if (event.type === 'file_done') results.push(event.result);
    }

    expect(send).not.toHaveBeenCalled();
    expect(preflight).toHaveBeenCalledTimes(2);
    expect(
      results.every((r) => r.status === 'success' && r.phase === 'preflight'),
    ).toBe(true);
  });

  it('disseminate mode calls send after each green preflight', async () => {
    const preflight = vi.fn(async (c: ExportCandidate) => greenPre(`h-${c.id}`));
    const send = vi.fn(async () => ({ ok: true, kv_upload_key: 'k' }));

    for await (const _ of runDisseminationQueue({
      candidates: [cand('a')],
      mode: 'disseminate',
      sink,
      preflight,
      send,
    })) {
      // drain
    }

    expect(preflight).toHaveBeenCalledTimes(1);
    expect(send).toHaveBeenCalledTimes(1);
  });
});

describe('runDisseminationQueue edge failures', () => {
  it('treats preflight throw as failed and continues', async () => {
    const preflight = vi.fn(async (c: ExportCandidate) => {
      if (c.id === 'a') throw new Error('network down');
      return greenPre(`h-${c.id}`);
    });
    const send = vi.fn(async () => ({ ok: true, kv_upload_key: 'kv' }));

    const results: DisseminationFileResult[] = [];
    for await (const event of runDisseminationQueue({
      candidates: [cand('a'), cand('b')],
      mode: 'disseminate',
      sink,
      preflight,
      send,
    })) {
      if (event.type === 'file_done') results.push(event.result);
    }

    expect(results[0]).toMatchObject({
      candidateId: 'a',
      status: 'failed',
      phase: 'preflight',
      detail: 'network down',
    });
    expect(results[1]?.status).toBe('success');
    expect(send).toHaveBeenCalledTimes(1);
  });

  it('stringifies non-Error preflight rejections', async () => {
    const preflight = vi.fn(async () => {
      throw 'boom';
    });
    const send = vi.fn(async () => ({ ok: true }));

    const results: DisseminationFileResult[] = [];
    for await (const event of runDisseminationQueue({
      candidates: [cand('a')],
      mode: 'disseminate',
      sink,
      preflight,
      send,
    })) {
      if (event.type === 'file_done') results.push(event.result);
    }

    expect(results[0]).toMatchObject({
      status: 'failed',
      phase: 'preflight',
      detail: 'boom',
    });
    expect(send).not.toHaveBeenCalled();
  });

  it('treats missing handle as not-green (isPreflightGreen)', async () => {
    const preflight = vi.fn(async () => ({
      ok: true,
      connectivity_ok: true,
      diffs: [],
    }));
    const send = vi.fn(async () => ({ ok: true }));

    const results: DisseminationFileResult[] = [];
    for await (const event of runDisseminationQueue({
      candidates: [cand('a')],
      mode: 'disseminate',
      sink,
      preflight,
      send,
    })) {
      if (event.type === 'file_done') results.push(event.result);
    }

    expect(results[0]).toMatchObject({
      status: 'failed',
      phase: 'preflight',
      detail: 'Preflight not green',
    });
    expect(send).not.toHaveBeenCalled();
  });

  it('treats send ok:false as failed and continues', async () => {
    const preflight = vi.fn(async (c: ExportCandidate) => greenPre(`h-${c.id}`));
    const send = vi.fn(async (c: ExportCandidate) => {
      if (c.id === 'a') {
        return { ok: false, detail: 'quota exceeded' } satisfies SendResponse;
      }
      return { ok: true, kv_upload_key: 'kv:b' };
    });

    const results: DisseminationFileResult[] = [];
    for await (const event of runDisseminationQueue({
      candidates: [cand('a'), cand('b')],
      mode: 'disseminate',
      sink,
      preflight,
      send,
    })) {
      if (event.type === 'file_done') results.push(event.result);
    }

    expect(results[0]).toMatchObject({
      candidateId: 'a',
      status: 'failed',
      phase: 'send',
      detail: 'quota exceeded',
    });
    expect(results[1]?.status).toBe('success');
  });

  it('uses default detail when send ok:false has none', async () => {
    const preflight = vi.fn(async () => greenPre('h1'));
    const send = vi.fn(async () => ({ ok: false }) satisfies SendResponse);

    const results: DisseminationFileResult[] = [];
    for await (const event of runDisseminationQueue({
      candidates: [cand('a')],
      mode: 'disseminate',
      sink,
      preflight,
      send,
    })) {
      if (event.type === 'file_done') results.push(event.result);
    }

    expect(results[0]?.detail).toBe('Send failed');
  });

  it('stringifies non-Error send rejections', async () => {
    const preflight = vi.fn(async () => greenPre('h1'));
    const send = vi.fn(async () => {
      throw 42;
    });

    const results: DisseminationFileResult[] = [];
    for await (const event of runDisseminationQueue({
      candidates: [cand('a')],
      mode: 'disseminate',
      sink,
      preflight,
      send,
    })) {
      if (event.type === 'file_done') results.push(event.result);
    }

    expect(results[0]).toMatchObject({
      status: 'failed',
      phase: 'send',
      detail: '42',
    });
  });
});

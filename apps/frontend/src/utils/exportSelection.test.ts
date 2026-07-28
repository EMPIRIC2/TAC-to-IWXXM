/**
 * T1.1 — Export selection model tests (TC-F16-005 / E18-4/6/9).
 *
 * Covers candidate build (session+drops only), ≤20 cap, empty disable,
 * and sole-candidate auto-select.
 */

import { describe, expect, it } from 'vitest';

import {
  MAX_EXPORT_SELECTION,
  buildExportCandidates,
  canActOnSelection,
  clearSelection,
  initialSelectedIds,
  selectAll,
  toggleSelection,
  type ExportCandidateInput,
} from './exportSelection';

function candidate(
  partial: Partial<ExportCandidateInput> &
    Pick<ExportCandidateInput, 'id' | 'name' | 'source'>,
): ExportCandidateInput {
  return {
    product: 'metar',
    iwxxmXml: '<xml/>',
    ...partial,
  };
}

describe('buildExportCandidates', () => {
  it('includes current-session outputs and dropped files only', () => {
    const list = buildExportCandidates({
      sessionOutputs: [
        candidate({ id: 's1', name: 'KJFK.metar.xml', source: 'session' }),
      ],
      droppedFiles: [candidate({ id: 'd1', name: 'drop.xml', source: 'drop' })],
      finishedHistory: [candidate({ id: 'h1', name: 'old.xml', source: 'session' })],
    });
    expect(list.map((c) => c.id)).toEqual(['s1', 'd1']);
    expect(list.every((c) => c.source === 'session' || c.source === 'drop')).toBe(true);
  });

  it('never lists Finished IndexedDB history as candidates (E18-4)', () => {
    const list = buildExportCandidates({
      sessionOutputs: [],
      droppedFiles: [],
      finishedHistory: [
        candidate({ id: 'h1', name: 'finished.xml', source: 'session' }),
      ],
    });
    expect(list).toEqual([]);
  });

  it('skips entries with no payload body', () => {
    const list = buildExportCandidates({
      sessionOutputs: [
        candidate({
          id: 'empty',
          name: 'empty.xml',
          source: 'session',
          iwxxmXml: '',
          tacText: '',
        }),
        candidate({
          id: 'ok',
          name: 'ok.xml',
          source: 'session',
          iwxxmXml: '<x/>',
        }),
      ],
    });
    expect(list.map((c) => c.id)).toEqual(['ok']);
  });
});

describe('initialSelectedIds (E18-9)', () => {
  it('auto-selects the sole candidate', () => {
    const candidates = buildExportCandidates({
      sessionOutputs: [candidate({ id: 'only', name: 'one.xml', source: 'session' })],
    });
    expect(initialSelectedIds(candidates)).toEqual(['only']);
  });

  it('starts empty when multiple candidates exist', () => {
    const candidates = buildExportCandidates({
      sessionOutputs: [
        candidate({ id: 'a', name: 'a.xml', source: 'session' }),
        candidate({ id: 'b', name: 'b.xml', source: 'session' }),
      ],
    });
    expect(initialSelectedIds(candidates)).toEqual([]);
  });

  it('starts empty when there are no candidates', () => {
    expect(initialSelectedIds([])).toEqual([]);
  });
});

describe('selection helpers (E18-6)', () => {
  const many = Array.from({ length: 22 }, (_, i) =>
    candidate({
      id: `c${i}`,
      name: `f${i}.xml`,
      source: i % 2 === 0 ? 'session' : 'drop',
    }),
  );
  const candidates = buildExportCandidates({
    sessionOutputs: many.filter((c) => c.source === 'session'),
    droppedFiles: many.filter((c) => c.source === 'drop'),
  });

  it('toggle adds and removes ids', () => {
    let selected = toggleSelection([], 'c0').selected;
    expect(selected).toEqual(['c0']);
    selected = toggleSelection(selected, 'c0').selected;
    expect(selected).toEqual([]);
  });

  it('rejects toggle that would exceed ≤20 with clear error', () => {
    const first20 = candidates.slice(0, MAX_EXPORT_SELECTION).map((c) => c.id);
    const result = toggleSelection(first20, candidates[20]!.id);
    expect(result.selected).toEqual(first20);
    expect(result.error).toMatch(/20/i);
  });

  it('selectAll caps at ≤20 and reports error when more candidates exist', () => {
    const result = selectAll(candidates);
    expect(result.selected).toHaveLength(MAX_EXPORT_SELECTION);
    expect(result.error).toMatch(/20/i);
  });

  it('selectAll selects all when count ≤20', () => {
    const small = candidates.slice(0, 3);
    const result = selectAll(small);
    expect(result.selected).toEqual(small.map((c) => c.id));
    expect(result.error).toBeUndefined();
  });

  it('clearSelection empties the selection', () => {
    expect(clearSelection(['a', 'b'])).toEqual([]);
  });

  it('canActOnSelection is false when empty and true when 1..20 selected', () => {
    expect(canActOnSelection([])).toBe(false);
    expect(canActOnSelection(['a'])).toBe(true);
    expect(
      canActOnSelection(
        Array.from({ length: MAX_EXPORT_SELECTION }, (_, i) => `id${i}`),
      ),
    ).toBe(true);
    expect(
      canActOnSelection(
        Array.from({ length: MAX_EXPORT_SELECTION + 1 }, (_, i) => `id${i}`),
      ),
    ).toBe(false);
  });
});

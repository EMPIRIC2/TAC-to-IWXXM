/**
 * TC-004 — Local IndexedDB work session lifecycle (F7.h / F21 / ADR-031).
 *
 * Red until T2.3 implements the store with `idb`.
 */

import { beforeEach, describe, expect, it } from 'vitest';
import type { WorkSessionUpsertPayload } from '@metar/shared';
import {
  EXPORT_SCHEMA_ID,
  MY_METARS_PRODUCTS,
  clearLocalWorkSessions,
  createLocalWorkSession,
  deleteLocalWorkSession,
  exportLocalWorkSessions,
  getLocalWorkSession,
  importLocalWorkSessions,
  listLocalWorkSessions,
  listMyMetars,
  restoreLocalWorkSession,
  updateLocalWorkSession,
} from './localWorkSessionStore';

function draftPayload(
  overrides: Partial<WorkSessionUpsertPayload> = {},
): WorkSessionUpsertPayload {
  return {
    title: 'KJFK · draft',
    product: 'metar',
    status: 'draft',
    manual_tac: 'METAR KJFK 121755Z 18004KT 10SM FEW250 24/18 A2992',
    pending_files: [],
    converted_results: [],
    errors: [],
    issues: [],
    conversion_params: { product: 'metar' },
    ...overrides,
  };
}

describe('localWorkSessionStore (TC-004)', () => {
  beforeEach(async () => {
    await clearLocalWorkSessions().catch(() => {
      // Stub throws until T2.3 — ignore so individual assertions surface.
    });
  });

  it('creates and reads a draft session without JWT', async () => {
    const created = await createLocalWorkSession(draftPayload());
    expect(created.id).toBeTruthy();
    expect(created.status).toBe('draft');
    expect(created.product).toBe('metar');
    expect(created.deleted_at).toBeNull();
    expect(created.manual_tac).toContain('KJFK');

    const fetched = await getLocalWorkSession(created.id);
    expect(fetched.id).toBe(created.id);
    expect(fetched.manual_tac).toBe(created.manual_tac);
  });

  it('lists sessions and updates status through WIP / Finished', async () => {
    const draft = await createLocalWorkSession(draftPayload());
    const wip = await updateLocalWorkSession(draft.id, {
      status: 'wip',
      converted_results: [
        { name: 'kjfk.xml', tac_input: draft.manual_tac, iwxxm_xml: '<xml/>' },
      ],
    });
    expect(wip.status).toBe('wip');

    const finished = await updateLocalWorkSession(draft.id, {
      status: 'finished',
      kv_upload_key: 'local-kv-key',
    });
    expect(finished.status).toBe('finished');
    expect(finished.kv_upload_key).toBe('local-kv-key');

    const listed = await listLocalWorkSessions({ status: 'finished' });
    expect(listed.total).toBe(1);
    expect(listed.items[0]?.id).toBe(draft.id);
  });

  it('rejects a second WIP when one already exists', async () => {
    const first = await createLocalWorkSession(draftPayload({ status: 'wip' }));
    expect(first.status).toBe('wip');

    await expect(
      createLocalWorkSession(
        draftPayload({
          title: 'second WIP',
          status: 'wip',
          manual_tac: 'METAR KLAX 121755Z 00000KT 10SM SKC 20/10 A3000',
        }),
      ),
    ).rejects.toThrow(/one WIP/i);

    await expect(
      updateLocalWorkSession(
        (
          await createLocalWorkSession(
            draftPayload({
              title: 'draft for promote',
              status: 'draft',
              manual_tac: 'SPECI KJFK 121800Z 18004KT 10SM FEW250 24/18 A2992',
              product: 'speci',
            }),
          )
        ).id,
        { status: 'wip' },
      ),
    ).rejects.toThrow(/one WIP/i);
  });

  it('soft-deletes and restores sessions', async () => {
    const row = await createLocalWorkSession(draftPayload());
    const deleted = await deleteLocalWorkSession(row.id);
    expect(deleted.deleted_at).toBeTruthy();

    const active = await listLocalWorkSessions();
    expect(active.items.find((s) => s.id === row.id)).toBeUndefined();

    const withDeleted = await listLocalWorkSessions({ include_deleted: true });
    expect(withDeleted.items.find((s) => s.id === row.id)?.deleted_at).toBeTruthy();

    const restored = await restoreLocalWorkSession(row.id);
    expect(restored.deleted_at).toBeNull();
    expect((await getLocalWorkSession(row.id)).deleted_at).toBeNull();
  });

  it('My METARs filters to metar/speci only', async () => {
    expect(MY_METARS_PRODUCTS).toEqual(['metar', 'speci']);

    await createLocalWorkSession(draftPayload({ product: 'metar', title: 'metar' }));
    await createLocalWorkSession(
      draftPayload({
        product: 'speci',
        title: 'speci',
        manual_tac: 'SPECI KJFK 121800Z 18004KT 10SM FEW250 24/18 A2992',
      }),
    );
    await createLocalWorkSession(
      draftPayload({
        product: 'taf',
        title: 'taf',
        manual_tac: 'TAF KJFK 121720Z 1218/1324 18010KT P6SM FEW250',
      }),
    );

    const mine = await listMyMetars();
    expect(mine.total).toBe(2);
    expect(mine.items.every((s) => MY_METARS_PRODUCTS.includes(s.product))).toBe(true);
    expect(mine.items.some((s) => s.product === 'taf')).toBe(false);

    const all = await listLocalWorkSessions();
    expect(all.total).toBe(3);
  });

  it('export/import round-trips as tac-work-sessions-export-v1', async () => {
    const a = await createLocalWorkSession(draftPayload({ title: 'A' }));
    const b = await createLocalWorkSession(
      draftPayload({
        title: 'B',
        product: 'taf',
        manual_tac: 'TAF KJFK 121720Z 1218/1324 18010KT P6SM FEW250',
      }),
    );

    const exported = await exportLocalWorkSessions();
    expect(exported.schema).toBe(EXPORT_SCHEMA_ID);
    expect(exported.exported_at).toBeTruthy();
    expect(exported.sessions).toHaveLength(2);
    expect(exported.sessions.map((s) => s.id).sort()).toEqual([a.id, b.id].sort());

    await clearLocalWorkSessions();
    expect((await listLocalWorkSessions()).total).toBe(0);

    const result = await importLocalWorkSessions(exported);
    expect(result.imported).toBe(2);
    const restored = await listLocalWorkSessions();
    expect(restored.total).toBe(2);
    expect(restored.items.map((s) => s.title).sort()).toEqual(['A', 'B']);
  });
});

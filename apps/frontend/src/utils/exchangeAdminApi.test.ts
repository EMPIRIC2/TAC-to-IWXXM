import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  fetchExchangeAllowlist,
  fetchInvitationGroups,
  selectInvitationGroup,
  setNationalRemarks,
} from './exchangeAdminApi';

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('exchangeAdminApi', () => {
  it('success: loads read-only allowlist', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => ({
        ok: true,
        json: async () => ({
          source: 'DISSEMINATION_EGRESS_ALLOWLIST',
          read_only: true,
          fail_closed: false,
          entries: ['wis2box'],
          admin_replay: false,
          sink_scope: 'wis2',
        }),
      })),
    );
    const view = await fetchExchangeAllowlist('tok');
    expect(view.read_only).toBe(true);
    expect(view.entries).toEqual(['wis2box']);
    expect(view.admin_replay).toBe(false);
  });

  it('failure: surfaces HTTP errors', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => ({
        ok: false,
        status: 403,
        text: async () => 'exchange-admin role required',
      })),
    );
    await expect(fetchExchangeAllowlist('tok')).rejects.toThrow(/exchange-admin/);
  });

  it('validation: invitation group select posts group_id', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        groups: [{ id: 'group-demo-a', name: 'Demo', centre_id: 'demo-a' }],
      }),
    });
    const listed = await fetchInvitationGroups('tok');
    expect(listed[0]?.id).toBe('group-demo-a');

    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        invitation_group_id: 'group-demo-a',
        include_national_remarks: false,
      }),
    });
    const prefs = await selectInvitationGroup('tok', 'group-demo-a');
    expect(prefs.invitation_group_id).toBe('group-demo-a');
    const body = JSON.parse(
      (fetchMock.mock.calls.at(-1)?.[1] as { body: string }).body,
    );
    expect(body.group_id).toBe('group-demo-a');

    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        include_national_remarks: true,
        invitation_group_id: 'group-demo-a',
      }),
    });
    const remarks = await setNationalRemarks('tok', true);
    expect(remarks.include_national_remarks).toBe(true);
  });
});

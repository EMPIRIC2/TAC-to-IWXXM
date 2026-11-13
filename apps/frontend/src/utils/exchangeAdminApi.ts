/**
 * Client helpers for `/api/v1/exchange-admin/*` (WIS2-only admin).
 */

import { apiUrl } from './apiBase';

export type AllowlistView = {
  source: string;
  read_only: boolean;
  fail_closed: boolean;
  entries: string[];
  admin_replay: boolean;
  sink_scope: string;
};

export type InvitationGroup = {
  id: string;
  name: string;
  centre_id: string;
};

export type ExchangePrefs = {
  include_national_remarks: boolean;
  invitation_group_id: string | null;
  admin_replay: boolean;
  sink_scope: string;
};

/**
 * Parse a JSON response body or raise with the response text.
 *
 * @param response - Fetch response
 * @returns Parsed JSON body
 */
async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }
  return (await response.json()) as T;
}

/**
 * Fetch the read-only egress allowlist.
 */
export async function fetchExchangeAllowlist(token: string): Promise<AllowlistView> {
  const response = await fetch(apiUrl('/exchange-admin/allowlist'), {
    headers: { Authorization: `Bearer ${token}` },
  });
  return readJson(response);
}

/**
 * Fetch invitation groups offered at login.
 */
export async function fetchInvitationGroups(token: string): Promise<InvitationGroup[]> {
  const response = await fetch(apiUrl('/exchange-admin/invitation-groups'), {
    headers: { Authorization: `Bearer ${token}` },
  });
  const body = await readJson<{ groups: InvitationGroup[] }>(response);
  return body.groups;
}

/**
 * Select an invitation group at login.
 */
export async function selectInvitationGroup(
  token: string,
  groupId: string,
): Promise<ExchangePrefs> {
  const response = await fetch(apiUrl('/exchange-admin/invitation-group'), {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ group_id: groupId }),
  });
  return readJson(response);
}

/**
 * Load operator exchange preferences.
 */
export async function fetchExchangePrefs(token: string): Promise<ExchangePrefs> {
  const response = await fetch(apiUrl('/exchange-admin/prefs'), {
    headers: { Authorization: `Bearer ${token}` },
  });
  return readJson(response);
}

/**
 * Toggle national remarks on WIS2 publish.
 */
export async function setNationalRemarks(
  token: string,
  include: boolean,
): Promise<ExchangePrefs> {
  const response = await fetch(apiUrl('/exchange-admin/prefs/national-remarks'), {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ include }),
  });
  return readJson(response);
}

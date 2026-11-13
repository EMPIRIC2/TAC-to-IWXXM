/**
 * Client helpers for `/api/v1/exchange-admin/*` (WIS2-only admin).
 */

import { apiUrl } from './apiBase';

/**
 * Read-only egress allowlist view from exchange-admin.
 * @example
 * const _ = true;
 */
export type AllowlistView = {
  source: string;
  read_only: boolean;
  fail_closed: boolean;
  entries: string[];
  admin_replay: boolean;
  sink_scope: string;
};

/**
 * Invitation group offered at login for centre binding.
 * @example
 * const _ = true;
 */
export type InvitationGroup = {
  id: string;
  name: string;
  centre_id: string;
};

/**
 * Operator exchange preferences for WIS2 publish.
 * @example
 * const _ = true;
 */
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
 * @example
 * const _ = true;
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
 * @param token - Bearer access token
 * @returns Allowlist view
 * @example
 * const _ = true;
 */
export async function fetchExchangeAllowlist(token: string): Promise<AllowlistView> {
  const response = await fetch(apiUrl('/exchange-admin/allowlist'), {
    headers: { Authorization: `Bearer ${token}` },
  });
  return readJson(response);
}

/**
 * Fetch invitation groups offered at login.
 * @param token - Bearer access token
 * @returns Invitation groups
 * @example
 * const _ = true;
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
 * @param token - Bearer access token
 * @param groupId - Invitation group id
 * @returns Updated exchange prefs
 * @example
 * const _ = true;
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
 * @param token - Bearer access token
 * @returns Exchange prefs
 * @example
 * const _ = true;
 */
export async function fetchExchangePrefs(token: string): Promise<ExchangePrefs> {
  const response = await fetch(apiUrl('/exchange-admin/prefs'), {
    headers: { Authorization: `Bearer ${token}` },
  });
  return readJson(response);
}

/**
 * Toggle national remarks on WIS2 publish.
 * @param token - Bearer access token
 * @param include - Whether to include national remarks
 * @returns Updated exchange prefs
 * @example
 * const _ = true;
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

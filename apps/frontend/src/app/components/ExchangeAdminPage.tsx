/**
 * WIS2-only exchange admin page: read-only allowlist, remarks toggle, groups.
 */

import { useEffect, useState } from 'react';
import {
  EXCHANGE_ADMIN_ALLOWLIST,
  EXCHANGE_ADMIN_ALLOWLIST_EMPTY,
  EXCHANGE_ADMIN_GROUPS,
  EXCHANGE_ADMIN_INTRO,
  EXCHANGE_ADMIN_NO_REPLAY,
  EXCHANGE_ADMIN_REMARKS,
  EXCHANGE_ADMIN_TITLE,
} from '@/utils/exchangeAdminCopy';
import {
  fetchExchangeAllowlist,
  fetchExchangePrefs,
  fetchInvitationGroups,
  selectInvitationGroup,
  setNationalRemarks,
  type AllowlistView,
  type InvitationGroup,
} from '@/utils/exchangeAdminApi';

type Props = {
  /** Bearer token for exchange-admin APIs. */
  token: string;
};

/**
 * Render the WIS2 exchange admin surface.
 *
 * @param props.token - Signed-in bearer token
 * @example
 * const _ = true;
 */
export function ExchangeAdminPage({ token }: Props) {
  const [allowlist, setAllowlist] = useState<AllowlistView | null>(null);
  const [groups, setGroups] = useState<InvitationGroup[]>([]);
  const [groupId, setGroupId] = useState<string>('');
  const [includeRemarks, setIncludeRemarks] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [view, invitationGroups, prefs] = await Promise.all([
          fetchExchangeAllowlist(token),
          fetchInvitationGroups(token),
          fetchExchangePrefs(token),
        ]);
        if (cancelled) return;
        setAllowlist(view);
        setGroups(invitationGroups);
        setGroupId(prefs.invitation_group_id ?? invitationGroups[0]?.id ?? '');
        setIncludeRemarks(prefs.include_national_remarks);
        setError('');
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : 'Could not load exchange admin',
          );
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <section
      className="mx-auto max-w-3xl space-y-6 px-4 py-6"
      data-testid="exchange-admin-page"
    >
      <header>
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-50">
          {EXCHANGE_ADMIN_TITLE}
        </h1>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
          {EXCHANGE_ADMIN_INTRO}
        </p>
        <p className="mt-1 text-xs text-gray-500">{EXCHANGE_ADMIN_NO_REPLAY}</p>
      </header>

      {error ? (
        <p className="text-sm text-red-700" data-testid="exchange-admin-error">
          {error}
        </p>
      ) : null}

      <div>
        <h2 className="text-sm font-semibold tracking-wide text-gray-500 uppercase">
          {EXCHANGE_ADMIN_ALLOWLIST}
        </h2>
        {allowlist && allowlist.entries.length === 0 ? (
          <p
            className="mt-2 text-sm text-gray-600"
            data-testid="exchange-admin-allowlist-empty"
          >
            {EXCHANGE_ADMIN_ALLOWLIST_EMPTY}
          </p>
        ) : (
          <ul
            className="mt-2 list-inside list-disc text-sm text-gray-800 dark:text-gray-200"
            data-testid="exchange-admin-allowlist"
          >
            {(allowlist?.entries ?? []).map((entry) => (
              <li key={entry}>{entry}</li>
            ))}
          </ul>
        )}
      </div>

      <label className="block text-sm">
        <span className="font-semibold tracking-wide text-gray-500 uppercase">
          {EXCHANGE_ADMIN_GROUPS}
        </span>
        <select
          className="mt-2 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 dark:border-gray-600 dark:bg-gray-900"
          data-testid="exchange-admin-group"
          value={groupId}
          disabled={busy || groups.length === 0}
          onChange={async (event) => {
            const next = event.target.value;
            setGroupId(next);
            setBusy(true);
            try {
              await selectInvitationGroup(token, next);
              setError('');
            } catch (err) {
              setError(err instanceof Error ? err.message : 'Could not save group');
            } finally {
              setBusy(false);
            }
          }}
        >
          {groups.map((group) => (
            <option key={group.id} value={group.id}>
              {group.name}
            </option>
          ))}
        </select>
      </label>

      <label className="flex items-center gap-2 text-sm text-gray-800 dark:text-gray-200">
        <input
          type="checkbox"
          data-testid="exchange-admin-remarks"
          checked={includeRemarks}
          disabled={busy}
          onChange={async (event) => {
            const next = event.target.checked;
            setIncludeRemarks(next);
            setBusy(true);
            try {
              await setNationalRemarks(token, next);
              setError('');
            } catch (err) {
              setIncludeRemarks(!next);
              setError(
                err instanceof Error ? err.message : 'Could not save preference',
              );
            } finally {
              setBusy(false);
            }
          }}
        />
        {EXCHANGE_ADMIN_REMARKS}
      </label>
    </section>
  );
}

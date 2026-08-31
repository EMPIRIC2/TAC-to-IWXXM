import { useEffect, useState } from 'react';
import type { WorkSession, WorkSessionStatus } from '@metar/shared';
import { Loader2, FileText } from 'lucide-react';
import { listAdminWorkSessions } from '/utils/workSessionApi';
import { Card } from '../ui/card';

interface AdminWorkSessionsPanelProps {
  accessToken: string;
}

const STATUS_LABEL: Record<WorkSessionStatus, string> = {
  draft: 'Draft',
  wip: 'WIP',
  finished: 'Finished',
  failed: 'Failed',
};

/**
 * Admin read-only view of all users' work sessions.
 */
export function AdminWorkSessionsPanel({ accessToken }: AdminWorkSessionsPanelProps) {
  const [sessions, setSessions] = useState<WorkSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<WorkSessionStatus | ''>('');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await listAdminWorkSessions(accessToken, {
          limit: 50,
          status: statusFilter || undefined,
        });
        if (!cancelled) {
          setSessions(response.items);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load work sessions');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [accessToken, statusFilter]);

  return (
    <Card className="p-6" aria-label="All users METAR work sessions">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="flex items-center gap-2 text-xl font-semibold text-gray-900 dark:text-white">
          <FileText className="h-5 w-5" aria-hidden="true" />
          Work Sessions
        </h2>
        <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          Status
          <select
            className="rounded-md border border-gray-300 bg-white px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800"
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(event.target.value as WorkSessionStatus | '')
            }
            aria-label="Filter work sessions by status"
          >
            <option value="">All</option>
            <option value="draft">Draft</option>
            <option value="wip">WIP</option>
            <option value="finished">Finished</option>
            <option value="failed">Failed</option>
          </select>
        </label>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          Loading work sessions…
        </div>
      )}

      {!loading && error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      )}

      {!loading && !error && sessions.length === 0 && (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No work sessions found.
        </p>
      )}

      {!loading && !error && sessions.length > 0 && (
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="px-2 py-2 font-medium">Title</th>
                <th className="px-2 py-2 font-medium">Status</th>
                <th className="px-2 py-2 font-medium">User</th>
                <th className="px-2 py-2 font-medium">Updated</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((session) => (
                <tr
                  key={session.id}
                  className="border-b border-gray-100 dark:border-gray-800"
                >
                  <td className="px-2 py-2">{session.title}</td>
                  <td className="px-2 py-2">
                    {STATUS_LABEL[session.status] ?? session.status}
                  </td>
                  <td className="px-2 py-2 font-mono text-xs">{session.user_id}</td>
                  <td className="px-2 py-2">
                    {new Date(session.updated_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}

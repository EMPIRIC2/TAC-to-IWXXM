import { useCallback, useEffect, useState } from 'react';
import type { WorkSession, WorkSessionStatus } from '@metar/shared';
import { ArrowLeft, Loader2, Trash2, RotateCcw } from 'lucide-react';
import {
  deleteWorkSession,
  listWorkSessions,
  restoreWorkSession,
} from '/utils/workSessionApi';
import { Button } from './ui/button';
import { Card } from './ui/card';

interface MyMetarsPageProps {
  accessToken: string;
  userEmail: string;
  onBack: () => void;
  onOpenSession: (session: WorkSession) => void;
}

const STATUS_OPTIONS: Array<WorkSessionStatus | 'all'> = [
  'all',
  'draft',
  'wip',
  'finished',
  'failed',
];

export function MyMetarsPage({
  accessToken,
  userEmail,
  onBack,
  onOpenSession,
}: MyMetarsPageProps) {
  const [statusFilter, setStatusFilter] = useState<WorkSessionStatus | 'all'>('all');
  const [includeDeleted, setIncludeDeleted] = useState(false);
  const [sessions, setSessions] = useState<WorkSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadSessions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listWorkSessions(accessToken, {
        status: statusFilter === 'all' ? undefined : statusFilter,
        include_deleted: includeDeleted,
        limit: 50,
      });
      setSessions(response.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  }, [accessToken, includeDeleted, statusFilter]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch list when filters change */
  useEffect(() => {
    void loadSessions();
  }, [loadSessions]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const handleDelete = async (sessionId: string) => {
    await deleteWorkSession(accessToken, sessionId);
    await loadSessions();
  };

  const handleRestore = async (sessionId: string) => {
    await restoreWorkSession(accessToken, sessionId);
    await loadSessions();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 dark:bg-gray-900">
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              My METARs
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">{userEmail}</p>
          </div>
          <Button variant="outline" onClick={onBack}>
            <ArrowLeft className="mr-2 h-4 w-4" aria-hidden="true" />
            Back to converter
          </Button>
        </div>

        <Card className="p-4">
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <label className="text-sm text-gray-700 dark:text-gray-300">
              Status
              <select
                className="ml-2 rounded border px-2 py-1 text-sm dark:bg-gray-800"
                value={statusFilter}
                onChange={(e) =>
                  setStatusFilter(e.target.value as WorkSessionStatus | 'all')
                }
              >
                {STATUS_OPTIONS.map((value) => (
                  <option key={value} value={value}>
                    {value === 'all' ? 'All' : value}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
              <input
                type="checkbox"
                checked={includeDeleted}
                onChange={(e) => setIncludeDeleted(e.target.checked)}
              />
              Show trash
            </label>
          </div>

          {loading && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
              Loading sessions…
            </div>
          )}
          {error && <p className="text-sm text-red-600">{error}</p>}

          {!loading && !error && (
            <ul className="divide-y divide-gray-200 dark:divide-gray-700">
              {sessions.map((session) => (
                <li
                  key={session.id}
                  className="flex items-center justify-between gap-3 py-3"
                >
                  <button
                    type="button"
                    className="flex-1 text-left"
                    onClick={() => onOpenSession(session)}
                  >
                    <div className="font-medium text-gray-900 dark:text-gray-100">
                      {session.title}
                    </div>
                    <div className="text-xs text-gray-500">
                      {session.status} · updated{' '}
                      {new Date(session.updated_at).toLocaleString()}
                    </div>
                  </button>
                  <div className="flex gap-2">
                    {session.deleted_at ? (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => void handleRestore(session.id)}
                      >
                        <RotateCcw className="h-4 w-4" aria-hidden="true" />
                      </Button>
                    ) : (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => void handleDelete(session.id)}
                      >
                        <Trash2 className="h-4 w-4" aria-hidden="true" />
                      </Button>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}

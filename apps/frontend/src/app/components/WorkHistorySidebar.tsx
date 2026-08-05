import { useEffect, useState } from 'react';
import type { WorkSession } from '@metar/shared';
import { Loader2, History } from 'lucide-react';
import { listLocalWorkSessions } from '/utils/localWorkSessionStore';
import { listWorkSessions } from '/utils/workSessionApi';
import { Button } from './ui/button';
import { Card } from './ui/card';

interface WorkHistorySidebarProps {
  /** When set, list DO Postgres sessions via JWT (F31 logged-in path). */
  accessToken?: string;
  activeSessionId?: string | null;
  onSelectSession: (session: WorkSession) => void;
  onOpenHistory?: () => void;
}

const STATUS_LABEL: Record<string, string> = {
  draft: 'Draft',
  wip: 'WIP',
  finished: 'Finished',
  failed: 'Failed',
};

/**
 * Recent work list — IndexedDB for guests; `/work-sessions` when authenticated.
 */
export function WorkHistorySidebar({
  accessToken,
  activeSessionId,
  onSelectSession,
  onOpenHistory,
}: WorkHistorySidebarProps) {
  const [sessions, setSessions] = useState<WorkSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const response = accessToken
          ? await listWorkSessions(accessToken, { limit: 5 })
          : await listLocalWorkSessions({ limit: 5 });
        if (!cancelled) {
          setSessions(response.items);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load history');
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
  }, [accessToken, activeSessionId]);

  return (
    <Card className="p-4" aria-label="Recent work sessions">
      <div className="mb-3 flex items-center justify-between gap-2">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-gray-900 dark:text-gray-100">
          <History className="h-4 w-4" aria-hidden="true" />
          Recent work
        </h2>
        {onOpenHistory && (
          <Button type="button" variant="ghost" size="sm" onClick={onOpenHistory}>
            My METARs
          </Button>
        )}
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          Loading…
        </div>
      )}

      {!loading && error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      )}

      {!loading && !error && sessions.length === 0 && (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No saved sessions yet.
        </p>
      )}

      {!loading && !error && sessions.length > 0 && (
        <ul className="space-y-2">
          {sessions.map((session) => (
            <li key={session.id}>
              <button
                type="button"
                className={`w-full rounded-md border px-3 py-2 text-left text-sm transition-colors ${
                  activeSessionId === session.id
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/40'
                    : 'border-gray-200 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800'
                }`}
                onClick={() => onSelectSession(session)}
              >
                <div className="font-medium text-gray-900 dark:text-gray-100">
                  {session.title}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {STATUS_LABEL[session.status] ?? session.status}
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}

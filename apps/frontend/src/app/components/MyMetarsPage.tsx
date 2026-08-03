import { useCallback, useEffect, useRef, useState } from 'react';
import type { WorkSession, WorkSessionStatus } from '@metar/shared';
import { ArrowLeft, Download, Loader2, RotateCcw, Trash2, Upload } from 'lucide-react';
import {
  EXPORT_SCHEMA_ID,
  deleteLocalWorkSession,
  exportLocalWorkSessions,
  importLocalWorkSessions,
  listMyMetars,
  restoreLocalWorkSession,
  type LocalWorkSessionExportV1,
} from '/utils/localWorkSessionStore';
import {
  MY_METARS_PRODUCTS,
  deleteWorkSession,
  listWorkSessions,
  restoreWorkSession,
} from '/utils/workSessionApi';
import { Button } from './ui/button';
import { Card } from './ui/card';

interface MyMetarsPageProps {
  /** JWT — when set, list/mutate DO Postgres sessions (F31). */
  accessToken?: string;
  /** Optional subtitle (local history — no account required). */
  userEmail?: string;
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
  userEmail = 'Local history',
  onBack,
  onOpenSession,
}: MyMetarsPageProps) {
  const [statusFilter, setStatusFilter] = useState<WorkSessionStatus | 'all'>('all');
  const [includeDeleted, setIncludeDeleted] = useState(false);
  const [sessions, setSessions] = useState<WorkSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [importMessage, setImportMessage] = useState<string | null>(null);
  const importInputRef = useRef<HTMLInputElement>(null);
  const isServerBacked = Boolean(accessToken);

  const loadSessions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      if (accessToken) {
        const response = await listWorkSessions(accessToken, {
          status: statusFilter === 'all' ? undefined : statusFilter,
          product: MY_METARS_PRODUCTS,
          include_deleted: includeDeleted,
          limit: 50,
        });
        setSessions(response.items);
      } else {
        const response = await listMyMetars({
          status: statusFilter === 'all' ? undefined : statusFilter,
          include_deleted: includeDeleted,
          limit: 50,
        });
        setSessions(response.items);
      }
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
    if (accessToken) {
      await deleteWorkSession(accessToken, sessionId);
    } else {
      await deleteLocalWorkSession(sessionId);
    }
    await loadSessions();
  };

  const handleRestore = async (sessionId: string) => {
    if (accessToken) {
      await restoreWorkSession(accessToken, sessionId);
    } else {
      await restoreLocalWorkSession(sessionId);
    }
    await loadSessions();
  };

  const handleExport = async () => {
    setError(null);
    setImportMessage(null);
    try {
      const doc = await exportLocalWorkSessions();
      const blob = new Blob([JSON.stringify(doc, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${EXPORT_SCHEMA_ID}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setImportMessage(`Exported ${doc.sessions.length} session(s)`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    }
  };

  const handleImportFile = async (file: File | undefined) => {
    if (!file) {
      return;
    }
    setError(null);
    setImportMessage(null);
    try {
      const text = await file.text();
      const parsed = JSON.parse(text) as LocalWorkSessionExportV1;
      const result = await importLocalWorkSessions(parsed);
      setImportMessage(`Imported ${result.imported} session(s)`);
      await loadSessions();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Import failed');
    }
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
            {!isServerBacked && (
              <div className="ml-auto flex flex-wrap gap-2">
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => void handleExport()}
                  data-testid="export-sessions"
                >
                  <Download className="mr-1 h-4 w-4" aria-hidden="true" />
                  Export
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => importInputRef.current?.click()}
                  data-testid="import-sessions"
                >
                  <Upload className="mr-1 h-4 w-4" aria-hidden="true" />
                  Import
                </Button>
                <input
                  ref={importInputRef}
                  type="file"
                  accept="application/json,.json"
                  className="hidden"
                  data-testid="import-sessions-input"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    void handleImportFile(file);
                    e.target.value = '';
                  }}
                />
              </div>
            )}
          </div>

          {importMessage && (
            <p
              className="mb-3 text-sm text-green-700 dark:text-green-400"
              role="status"
            >
              {importMessage}
            </p>
          )}

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

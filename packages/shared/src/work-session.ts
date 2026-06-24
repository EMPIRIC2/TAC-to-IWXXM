/** F5 METAR work session types — parity with apps/backend work_session schemas */

export type WorkSessionStatus = 'draft' | 'wip' | 'finished' | 'failed';

export interface PendingFilePayload {
  name: string;
  content: string;
}

export interface WorkSession {
  id: string;
  user_id: string;
  status: WorkSessionStatus;
  title: string;
  manual_tac: string;
  pending_files: PendingFilePayload[];
  converted_results: Record<string, unknown>[];
  errors: string[];
  issues: Record<string, unknown>[];
  conversion_params: Record<string, unknown>;
  kv_upload_key: string | null;
  deleted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface WorkSessionListResponse {
  items: WorkSession[];
  total: number;
  page: number;
  limit: number;
}

export interface WorkSessionUpsertPayload {
  title?: string;
  manual_tac?: string;
  pending_files?: PendingFilePayload[];
  converted_results?: Record<string, unknown>[];
  errors?: string[];
  issues?: Record<string, unknown>[];
  conversion_params?: Record<string, unknown>;
  status?: WorkSessionStatus;
  kv_upload_key?: string;
}

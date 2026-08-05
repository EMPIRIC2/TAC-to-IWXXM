/**
 * Auto-upload eligible guest local drafts on login (F31 / UJ-046 / TC-F31-004).
 *
 * ``D-S038-guest-merge``=2 — upload all eligible drafts; no merge prompt.
 */

import type { WorkSession, WorkSessionUpsertPayload } from '@metar/shared';
import { createWorkSession } from './workSessionApi';
import { deleteLocalWorkSession, listLocalWorkSessions } from './localWorkSessionStore';

export interface AutoUploadResult {
  uploaded: number;
  errors: Array<{ sessionId: string; message: string }>;
}

function isEligibleLocalDraft(session: WorkSession): boolean {
  if (session.deleted_at != null) {
    return false;
  }
  return session.status === 'draft' || session.status === 'wip';
}

function toUpsertPayload(session: WorkSession): WorkSessionUpsertPayload {
  return {
    product: session.product,
    status: session.status === 'finished' ? 'draft' : session.status,
    title: session.title,
    manual_tac: session.manual_tac,
    pending_files: session.pending_files,
    converted_results: session.converted_results,
    errors: session.errors,
    issues: session.issues,
    conversion_params: session.conversion_params,
    kv_upload_key: session.kv_upload_key ?? undefined,
  };
}

/**
 * Upload all eligible local drafts to DO Postgres via work-sessions API.
 *
 * Parameters
 * ----------
 * accessToken :
 *     Bearer JWT from Auth login.
 *
 * Returns
 * -------
 * Promise<AutoUploadResult>
 *     Counts + per-item errors (does not throw on individual failures).
 */
export async function autoUploadEligibleLocalDrafts(
  accessToken: string,
): Promise<AutoUploadResult> {
  const listed = await listLocalWorkSessions({
    include_deleted: false,
    limit: 100,
  });
  const eligible = listed.items.filter(isEligibleLocalDraft);
  const errors: AutoUploadResult['errors'] = [];
  let uploaded = 0;

  for (const session of eligible) {
    try {
      await createWorkSession(accessToken, toUpsertPayload(session));
      await deleteLocalWorkSession(session.id);
      uploaded += 1;
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      errors.push({ sessionId: session.id, message });
    }
  }

  return { uploaded, errors };
}

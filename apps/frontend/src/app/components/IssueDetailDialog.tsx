/**
 * Fuller description for one lint or validation issue (F7 / F10 / F15).
 */

import { useEffect, type ReactNode } from 'react';
import type { IssueDetailModel } from '@/utils/issueDetail';
import {
  ISSUE_DETAIL_CLOSE,
  ISSUE_DETAIL_CODE,
  ISSUE_DETAIL_HINT,
  ISSUE_DETAIL_LOCATION,
  ISSUE_DETAIL_MESSAGE,
  ISSUE_DETAIL_PRODUCT,
  ISSUE_DETAIL_RULE,
  ISSUE_DETAIL_SEVERITY,
  ISSUE_DETAIL_SOURCE,
  ISSUE_DETAIL_TAGS,
  ISSUE_DETAIL_TITLE,
} from '@/utils/issueDetailCopy';

/**
 * Type `IssueDetailDialogProps`.
 * @example
 * const _ = true;
 */
type IssueDetailDialogProps = {
  detail: IssueDetailModel | null;
  onClose: () => void;
};

/**
 * One labeled row in the issue dialog.
 *
 * @param props.label - Field name
 * @param props.value - Field text
 * @returns A definition row
 * @example
 * const _ = true;
 */
function DetailRow({ label, value }: { label: string; value: string }): ReactNode {
  return (
    <div className="grid grid-cols-[7rem_1fr] gap-2 text-sm">
      <dt className="text-gray-500 dark:text-gray-400">{label}</dt>
      <dd className="text-gray-900 dark:text-gray-100">{value}</dd>
    </div>
  );
}

/**
 * Dialog for one issue. Renders nothing until a row is opened.
 *
 * @param props.detail - Fields to show, or null when closed
 * @param props.onClose - Dismiss the dialog
 * @example
 * const _ = true;
 */
export function IssueDetailDialog({ detail, onClose }: IssueDetailDialogProps) {
  useEffect(() => {
    if (!detail) {
      return;
    }
    /**
     * Close on Escape.
     */
    function onKey(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        onClose();
      }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [detail, onClose]);

  if (!detail) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      data-testid="issue-detail-backdrop"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="issue-detail-title"
        data-testid="issue-detail-dialog"
        className="max-h-[80vh] w-full max-w-lg overflow-y-auto rounded-md border border-gray-200 bg-white p-4 shadow-lg dark:border-gray-700 dark:bg-gray-900"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-3 flex items-center justify-between gap-3">
          <h2
            id="issue-detail-title"
            className="text-base font-semibold text-gray-900 dark:text-gray-100"
          >
            {ISSUE_DETAIL_TITLE}
          </h2>
          <button
            type="button"
            className="text-sm text-gray-700 underline dark:text-gray-200"
            data-testid="issue-detail-close"
            onClick={onClose}
          >
            {ISSUE_DETAIL_CLOSE}
          </button>
        </div>
        <dl className="space-y-2">
          <DetailRow label={ISSUE_DETAIL_CODE} value={detail.code} />
          <DetailRow label={ISSUE_DETAIL_SEVERITY} value={detail.severity} />
          <DetailRow label={ISSUE_DETAIL_MESSAGE} value={detail.message} />
          <DetailRow label={ISSUE_DETAIL_RULE} value={detail.rule} />
          <DetailRow label={ISSUE_DETAIL_HINT} value={detail.hint} />
          <DetailRow label={ISSUE_DETAIL_SOURCE} value={detail.source} />
          <DetailRow label={ISSUE_DETAIL_PRODUCT} value={detail.product} />
          <DetailRow label={ISSUE_DETAIL_TAGS} value={detail.tags} />
          <DetailRow label={ISSUE_DETAIL_LOCATION} value={detail.location} />
        </dl>
      </div>
    </div>
  );
}

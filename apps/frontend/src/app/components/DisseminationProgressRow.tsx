/**
 * Per-file dissemination progress row (EV-018 / E18-10/13/14).
 *
 * Mail travels along an arrow toward the sink; green check / red X on settle.
 * When prefers-reduced-motion, graphic is hidden (text-only).
 */

import { Check, Mail, Server, X } from 'lucide-react';
import { motion, useReducedMotion } from 'motion/react';

import type { SinkType } from '/utils/dissemination';

/** Visual / logical status for one candidate in the queue. */
export type ProgressRowStatus = 'pending' | 'preflight' | 'send' | 'success' | 'failed';

export interface DisseminationProgressRowProps {
  candidateId: string;
  name: string;
  status: ProgressRowStatus;
  detail?: string;
  sinkType?: SinkType;
  /** Override reduced-motion detection (tests). */
  forceReducedMotion?: boolean;
}

/**
 * Interactive progress row for one export candidate during Disseminate.
 *
 * @param props - Candidate identity, status, optional detail and sink
 */
export function DisseminationProgressRow({
  candidateId,
  name,
  status,
  detail,
  forceReducedMotion,
}: DisseminationProgressRowProps) {
  const systemReduced = useReducedMotion();
  const reducedMotion = forceReducedMotion ?? systemReduced ?? false;
  const inFlight = status === 'preflight' || status === 'send';
  const failed = status === 'failed';
  const success = status === 'success';

  const statusLabel =
    status === 'pending'
      ? 'Pending'
      : status === 'preflight'
        ? 'Preflight…'
        : status === 'send'
          ? 'Sending…'
          : status === 'success'
            ? 'Sent'
            : 'Failed';

  return (
    <div
      className="rounded border border-gray-200 p-2 dark:border-gray-700"
      data-testid={`dissemination-progress-row-${candidateId}`}
      data-status={status}
    >
      <div className="flex items-center justify-between gap-2 text-sm">
        <span className="truncate font-medium text-gray-900 dark:text-white">
          {name}
        </span>
        <span
          className={
            failed
              ? 'text-red-600 dark:text-red-400'
              : success
                ? 'text-green-700 dark:text-green-400'
                : 'text-gray-600 dark:text-gray-300'
          }
          data-testid={`dissemination-progress-status-${candidateId}`}
        >
          {statusLabel}
        </span>
      </div>

      {detail && (
        <p
          className="mt-1 text-xs text-red-600 dark:text-red-400"
          data-testid={`dissemination-progress-detail-${candidateId}`}
        >
          {detail}
        </p>
      )}

      {reducedMotion ? (
        <p
          className="mt-1 text-xs text-gray-500 dark:text-gray-400"
          data-testid={`dissemination-progress-text-${candidateId}`}
        >
          {statusLabel}
          {detail ? ` — ${detail}` : ''}
        </p>
      ) : (
        <div
          className="relative mt-2 flex h-8 items-center gap-2"
          data-testid={`dissemination-progress-graphic-${candidateId}`}
          aria-hidden="true"
        >
          <Mail
            className="h-4 w-4 shrink-0 text-gray-500"
            data-testid={`dissemination-progress-mail-src-${candidateId}`}
          />
          <div className="relative h-1 flex-1 rounded bg-gray-200 dark:bg-gray-700">
            <div
              className="absolute inset-y-0 left-0 right-0 border-t border-dashed border-gray-400 dark:border-gray-500"
              style={{ top: '50%' }}
            />
            {inFlight && (
              <motion.div
                className="absolute top-1/2 -translate-y-1/2"
                initial={{ left: '0%' }}
                animate={{ left: '100%' }}
                transition={{
                  duration: 1.2,
                  repeat: Infinity,
                  ease: 'linear',
                }}
                data-testid={`dissemination-progress-mail-anim-${candidateId}`}
              >
                <Mail className="h-4 w-4 -translate-x-1/2 text-blue-600 dark:text-blue-400" />
              </motion.div>
            )}
          </div>
          <Server
            className="h-4 w-4 shrink-0 text-gray-500"
            data-testid={`dissemination-progress-dest-${candidateId}`}
          />
          {success && (
            <Check
              className="h-4 w-4 shrink-0 text-green-600 dark:text-green-400"
              data-testid={`dissemination-progress-ok-${candidateId}`}
              aria-label="Success"
            />
          )}
          {failed && (
            <X
              className="h-4 w-4 shrink-0 text-red-600 dark:text-red-400"
              data-testid={`dissemination-progress-fail-${candidateId}`}
              aria-label="Failed"
            />
          )}
        </div>
      )}
    </div>
  );
}

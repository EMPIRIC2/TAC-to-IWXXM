/**
 * Public converter footer: privacy, feedback, and terms.
 * Full-bleed bottom bar; collapses to a right-edge reveal handle.
 * @example
 * const _ = true;
 */

import { useState } from 'react';
import { ChevronRight } from 'lucide-react';

import { BetaBadge } from './BetaBadge';
import { FeedbackDialog } from './FeedbackDialog';
import { FEEDBACK_BUTTON_LABEL, FEEDBACK_OPEN_LABEL } from '@/utils/betaFeedback';

/**
 * Type `OperatorFooterProps`.
 * @example
 * const _ = true;
 */
export interface OperatorFooterProps {
  onOpenPrivacy: () => void;
  onOpenTerms: () => void;
}

/**
 * Footer chrome on the public convert page. Feedback opens a dialog.
 * @param props.onOpenPrivacy - Open privacy settings
 * @param props.onOpenTerms - Open terms of service
 * @example
 * const _ = true;
 */
export function OperatorFooter({ onOpenPrivacy, onOpenTerms }: OperatorFooterProps) {
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  if (collapsed) {
    return (
      <button
        type="button"
        data-testid="operator-footer-reveal"
        aria-label="Show site footer"
        title="Show site footer"
        className="fixed bottom-4 right-0 z-10 flex h-16 w-4 items-center justify-center rounded-l-md border border-r-0 border-gray-200 bg-white text-gray-600 shadow-md hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 dark:hover:bg-gray-800"
        onClick={() => setCollapsed(false)}
      >
        <ChevronRight className="h-3.5 w-3.5 rotate-180" aria-hidden="true" />
      </button>
    );
  }

  return (
    <div
      className="fixed inset-x-0 bottom-0 z-10 w-full border-t border-gray-200 bg-gray-50/95 px-4 py-3 text-center text-sm text-gray-500 shadow-[0_-4px_12px_rgba(0,0,0,0.04)] backdrop-blur-sm dark:border-gray-700 dark:bg-gray-900/95 dark:text-gray-400"
      data-testid="operator-footer"
    >
      <div className="relative mx-auto max-w-6xl">
        <button
          type="button"
          data-testid="operator-footer-collapse"
          aria-label="Hide site footer"
          className="absolute right-0 top-0 inline-flex h-8 w-8 items-center justify-center rounded-md text-gray-500 hover:bg-gray-100 hover:text-gray-800 dark:hover:bg-gray-800 dark:hover:text-gray-200"
          onClick={() => setCollapsed(true)}
        >
          <ChevronRight className="h-4 w-4" aria-hidden="true" />
        </button>
        <p className="pr-10">
          TAC → IWXXM conversion powered by <code className="text-xs">tac2iwxxm</code>,
          with <code className="text-xs">tac-validate</code> and{' '}
          <code className="text-xs">iwxxm-validate</code>. Downloads are IWXXM{' '}
          <code className="text-xs">.xml</code> files.
        </p>
        <div
          role="group"
          aria-label="Site links"
          className="mt-2 flex flex-row flex-wrap items-center justify-center gap-x-3 gap-y-1"
          data-testid="operator-footer-links"
        >
          <button
            type="button"
            className="underline underline-offset-2 hover:text-gray-700 dark:hover:text-gray-200"
            onClick={onOpenPrivacy}
            aria-label="Open privacy settings"
          >
            Privacy settings
          </button>
          <span aria-hidden="true" className="text-gray-300 dark:text-gray-600">
            ·
          </span>
          <span className="inline-flex items-center gap-1.5">
            <button
              type="button"
              className="underline underline-offset-2 hover:text-gray-700 dark:hover:text-gray-200"
              onClick={() => setFeedbackOpen(true)}
              aria-label={FEEDBACK_OPEN_LABEL}
              data-testid="footer-feedback"
            >
              {FEEDBACK_BUTTON_LABEL}
            </button>
            <BetaBadge />
          </span>
          <span aria-hidden="true" className="text-gray-300 dark:text-gray-600">
            ·
          </span>
          <button
            type="button"
            className="underline underline-offset-2 hover:text-gray-700 dark:hover:text-gray-200"
            onClick={onOpenTerms}
            aria-label="Open terms of service"
          >
            Terms of service
          </button>
        </div>
      </div>
      <FeedbackDialog isOpen={feedbackOpen} onClose={() => setFeedbackOpen(false)} />
    </div>
  );
}

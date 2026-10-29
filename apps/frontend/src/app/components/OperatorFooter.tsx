/**
 * Public converter footer: privacy, feedback, and terms.
 * @example
 * const _ = true;
 */

import { useState } from 'react';

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

  return (
    <div
      className="mt-12 text-center text-sm text-gray-500 dark:text-gray-400"
      data-testid="operator-footer"
    >
      <p>
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
      <FeedbackDialog isOpen={feedbackOpen} onClose={() => setFeedbackOpen(false)} />
    </div>
  );
}

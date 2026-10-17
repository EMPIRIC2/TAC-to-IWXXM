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
      <p className="mt-2">
        <button
          type="button"
          className="underline underline-offset-2 hover:text-gray-700 dark:hover:text-gray-200"
          onClick={onOpenPrivacy}
          aria-label="Open privacy settings"
        >
          Privacy settings
        </button>
      </p>
      <p className="mt-2">
        <button
          type="button"
          className="underline underline-offset-2 hover:text-gray-700 dark:hover:text-gray-200"
          onClick={() => setFeedbackOpen(true)}
          aria-label={FEEDBACK_OPEN_LABEL}
          data-testid="footer-feedback"
        >
          {FEEDBACK_BUTTON_LABEL}
        </button>{' '}
        <BetaBadge />
      </p>
      <p className="mt-2">
        <button
          type="button"
          className="underline underline-offset-2 hover:text-gray-700 dark:hover:text-gray-200"
          onClick={onOpenTerms}
          aria-label="Open terms of service"
        >
          Terms of service
        </button>
      </p>
      <FeedbackDialog isOpen={feedbackOpen} onClose={() => setFeedbackOpen(false)} />
    </div>
  );
}

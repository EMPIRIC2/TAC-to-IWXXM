/**
 * Compact Beta badge (+ optional GitHub feedback link) for operator surfaces.
 */

import { Badge } from './ui/badge';
import {
  BETA_BADGE_LABEL,
  BETA_FEEDBACK_HELP,
  BETA_FEEDBACK_ISSUES_URL,
  BETA_FEEDBACK_LINK_LABEL,
} from '@/utils/betaFeedback';

export interface BetaBadgeProps {
  /** When true, render a short help line + Issues link under/beside the badge. */
  showHelp?: boolean;
  /** Extra class names on the outer wrapper. */
  className?: string;
}

/**
 * Render a Beta badge and optional feedback help link.
 *
 * @param props.showHelp - Include help sentence + Issues link
 * @param props.className - Wrapper className
 */
export function BetaBadge({ showHelp = false, className }: BetaBadgeProps) {
  return (
    <span
      className={className ?? 'inline-flex flex-wrap items-center gap-2'}
      data-testid="beta-badge-root"
    >
      <Badge
        variant="outline"
        data-testid="beta-badge"
        className="border-amber-600/40 text-amber-800 dark:text-amber-200"
      >
        {BETA_BADGE_LABEL}
      </Badge>
      {showHelp ? (
        <span
          className="text-xs text-gray-600 dark:text-gray-300"
          data-testid="beta-feedback-help"
        >
          {BETA_FEEDBACK_HELP}{' '}
          <a
            href={BETA_FEEDBACK_ISSUES_URL}
            target="_blank"
            rel="noopener noreferrer"
            data-testid="beta-feedback-link"
            className="underline underline-offset-2 hover:text-gray-900 dark:hover:text-white"
          >
            {BETA_FEEDBACK_LINK_LABEL}
          </a>
        </span>
      ) : null}
    </span>
  );
}

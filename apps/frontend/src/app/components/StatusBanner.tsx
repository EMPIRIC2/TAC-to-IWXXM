/**
 * Shared operator status / notice banner (staging UX evolve).
 *
 * Tones distinguish account risk (warning) from demo/non-operational (info)
 * and other soft notices (caution). Keep copy free of internal doc refs.
 */

import type { ReactNode } from 'react';

import { cn } from '@/app/components/ui/utils';

export type StatusBannerTone = 'warning' | 'info' | 'caution' | 'neutral';

const TONE_CLASS: Record<StatusBannerTone, string> = {
  warning:
    'border-amber-300 bg-amber-50 text-amber-950 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-100',
  info: 'border-sky-300 bg-sky-50 text-sky-950 dark:border-sky-800 dark:bg-sky-950/40 dark:text-sky-100',
  caution:
    'border-amber-200 bg-amber-50/80 text-amber-900 dark:border-amber-800 dark:bg-amber-950/30 dark:text-amber-100',
  neutral:
    'border-gray-200 bg-gray-50 text-gray-800 dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-100',
};

const ACCENT_CLASS: Record<StatusBannerTone, string> = {
  warning: 'bg-amber-500',
  info: 'bg-sky-500',
  caution: 'bg-amber-400',
  neutral: 'bg-gray-400',
};

export interface StatusBannerProps {
  tone: StatusBannerTone;
  children: ReactNode;
  /** Optional trailing action (e.g. Sign in link button). */
  action?: ReactNode;
  className?: string;
  role?: 'status' | 'alert';
  'data-testid'?: string;
}

/**
 * Compact status banner with left accent bar and consistent padding.
 *
 * @param props.tone - Visual severity / category
 * @param props.children - Banner body copy
 * @param props.action - Optional inline action control
 */
export function StatusBanner({
  tone,
  children,
  action,
  className,
  role = 'status',
  'data-testid': testId,
}: StatusBannerProps) {
  return (
    <div
      role={role}
      data-testid={testId}
      className={cn(
        'relative flex gap-3 overflow-hidden rounded-md border px-3 py-2 text-sm',
        TONE_CLASS[tone],
        className,
      )}
    >
      <span
        aria-hidden="true"
        className={cn('absolute inset-y-0 left-0 w-1', ACCENT_CLASS[tone])}
      />
      <div className="min-w-0 flex-1 pl-1">{children}</div>
      {action ? <div className="shrink-0 self-center">{action}</div> : null}
    </div>
  );
}

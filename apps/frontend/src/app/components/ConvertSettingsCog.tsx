/**
 * Convert Settings cog — advanced / manual options (UJ-089).
 *
 * Uses native details so controls stay in the document when collapsed
 * (testids + progressive disclosure).
 *
 * [Corpus: product §F7] [Corpus: journeys §UJ-089]
 */

import type { ReactNode } from 'react';
import { Settings } from 'lucide-react';

/**
 * Props for {@link ConvertSettingsCog}.
 * @example
 * const _ = true;
 */
export interface ConvertSettingsCogProps {
  children: ReactNode;
}

/**
 * Settings disclosure opened from a cog with accessible name “Settings”.
 *
 * @param props.children - Settings form controls
 * @returns Cog summary + details body
 * @example
 * const _ = true;
 */
export function ConvertSettingsCog({ children }: ConvertSettingsCogProps) {
  return (
    <details className="relative" data-testid="convert-settings">
      <summary
        className="group relative inline-flex h-9 w-9 cursor-pointer list-none items-center justify-center rounded-md text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800 [&::-webkit-details-marker]:hidden"
        data-testid="convert-settings-cog"
        aria-label="Settings"
      >
        <Settings className="h-4 w-4" aria-hidden="true" />
        <span
          role="tooltip"
          data-testid="icon-hover-card"
          className="pointer-events-none absolute left-1/2 top-full z-30 mt-2 w-max max-w-[14rem] -translate-x-1/2 rounded-md border border-gray-200 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-800 opacity-0 shadow-md transition-opacity duration-500 group-hover:opacity-100 group-focus-visible:opacity-100 dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100"
        >
          Settings
        </span>
      </summary>
      <div
        className="absolute right-0 z-20 mt-2 max-h-[min(70vh,36rem)] w-96 space-y-4 overflow-y-auto rounded-md border border-gray-200 bg-white p-4 shadow-lg dark:border-gray-700 dark:bg-gray-900"
        data-testid="convert-settings-dialog"
      >
        <p className="text-sm font-semibold text-gray-900 dark:text-white">Settings</p>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Product, profile, input mode, conversion parameters, layout, preview controls,
          and conversion metadata.
        </p>
        {children}
      </div>
    </details>
  );
}

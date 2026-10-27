/**
 * Conversion profile panel (Calmer Convert screen 3 / TC-UX-CALM-005).
 *
 * Uses Dialog (not vaul Drawer) so jsdom unit coverage stays deterministic.
 *
 * [Corpus: product §F7]
 */

import type { ReactNode } from 'react';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Button } from './ui/button';

export interface ConvertProfileDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  nationalSection: ReactNode;
  customizeSection: ReactNode;
  outputSection: ReactNode;
  onApply: () => void;
  onReset?: () => void;
}

/**
 * Profile dialog with progressive disclosure for output options.
 */
export function ConvertProfileDrawer({
  open,
  onOpenChange,
  nationalSection,
  customizeSection,
  outputSection,
  onApply,
  onReset,
}: ConvertProfileDrawerProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="flex max-h-[90vh] max-w-md flex-col gap-0 overflow-hidden p-0"
        data-testid="convert-profile-drawer"
      >
        <DialogHeader className="space-y-1 px-6 pt-6">
          <DialogTitle>Conversion profile</DialogTitle>
          <DialogDescription>
            Choose national rules first. Customize steps and output options only when
            you need them.
          </DialogDescription>
        </DialogHeader>
        <div className="flex-1 space-y-4 overflow-y-auto px-6 py-4">
          <section className="space-y-2" data-testid="convert-profile-national">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
              National rules
            </h3>
            {nationalSection}
          </section>
          <details
            open
            className="rounded-md border border-gray-200 p-3 dark:border-gray-700"
          >
            <summary className="cursor-pointer text-sm font-semibold text-gray-900 dark:text-white">
              Customize each step
            </summary>
            <div className="mt-3 space-y-3" data-testid="convert-profile-customize">
              {customizeSection}
            </div>
          </details>
          <details className="rounded-md border border-gray-200 p-3 dark:border-gray-700">
            <summary className="cursor-pointer text-sm font-semibold text-gray-900 dark:text-white">
              Output options
            </summary>
            <div className="mt-3 space-y-3" data-testid="convert-profile-output">
              {outputSection}
            </div>
          </details>
        </div>
        <DialogFooter className="flex flex-row justify-between gap-2 border-t border-gray-200 px-6 py-4 dark:border-gray-700 sm:justify-between">
          {onReset ? (
            <Button type="button" variant="ghost" onClick={onReset}>
              Reset to WMO defaults
            </Button>
          ) : (
            <span />
          )}
          <Button
            type="button"
            data-testid="convert-profile-apply"
            onClick={() => {
              onApply();
              onOpenChange(false);
            }}
          >
            Apply
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

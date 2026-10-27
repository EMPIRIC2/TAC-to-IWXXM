/**
 * Conversion profile drawer (Calmer Convert screen 3 / TC-UX-CALM-005).
 *
 * [Corpus: product §F7]
 */

import type { ReactNode } from 'react';

import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from './ui/drawer';
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
 * Right-side profile drawer with progressive disclosure for output options.
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
    <Drawer open={open} onOpenChange={onOpenChange} direction="right">
      <DrawerContent
        className="ml-auto flex h-full w-full max-w-md flex-col"
        data-testid="convert-profile-drawer"
      >
        <DrawerHeader>
          <DrawerTitle>Conversion profile</DrawerTitle>
          <DrawerDescription>
            Choose national rules first. Customize steps and output options only when
            you need them.
          </DrawerDescription>
        </DrawerHeader>
        <div className="flex-1 space-y-4 overflow-y-auto px-4 pb-4">
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
        <DrawerFooter className="flex flex-row justify-between gap-2 border-t border-gray-200 dark:border-gray-700">
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
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
}

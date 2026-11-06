/**
 * In-app Convert Help checklist (UJ-088 / TC-UX-CALM-008).
 *
 * [Corpus: product §F7] [Corpus: journeys §UJ-088]
 */

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Button } from './ui/button';
import { OPERATOR_ONE_PAGER_URL } from '/utils/operatorHelp';

const STEPS = [
  'Paste a TAC report (or drop a file).',
  'Optional: try an example chip for METAR, TAF, SIGMET, or volcanic ash.',
  'Select Convert when the preview looks right.',
  'Download latest when the bulletin is valid.',
] as const;

/**
 * Props for the Convert Help checklist dialog.
 * @example
 * const _ = true;
 */
export interface ConvertHelpChecklistProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

/**
 * Short operator checklist dialog; depth link to the one-pager.
 *
 * @param props.open - Whether the dialog is visible
 * @param props.onOpenChange - Open-state setter
 * @example
 * const _ = true;
 */
export function ConvertHelpChecklist({
  open,
  onOpenChange,
}: ConvertHelpChecklistProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="max-w-md"
        data-testid="convert-help-checklist"
        aria-describedby="convert-help-checklist-desc"
      >
        <DialogHeader>
          <DialogTitle>Convert checklist</DialogTitle>
          <DialogDescription id="convert-help-checklist-desc">
            A short path from TAC to downloadable IWXXM. Open Help anytime to replay
            this list.
          </DialogDescription>
        </DialogHeader>
        <ol className="list-decimal space-y-2 pl-5 text-sm text-gray-800 dark:text-gray-200">
          {STEPS.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
        <DialogFooter className="flex flex-col gap-2 sm:flex-row sm:justify-between">
          <a
            href={OPERATOR_ONE_PAGER_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-700 underline underline-offset-2 dark:text-blue-300"
            data-testid="operator-help-link"
          >
            Open full one-pager
          </a>
          <Button type="button" onClick={() => onOpenChange(false)}>
            Got it
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

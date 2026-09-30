/**
 * Read-only terms dialog opened from the converter footer.
 * @example
 * const _ = true;
 */

import { Button } from './ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { SITE_TERMS_BODY } from '@/utils/siteTermsCopy';
import { dismissSiteTerms } from './dismissSiteTerms';

/**
 * Type `SiteTermsDialogProps`.
 * @example
 * const _ = true;
 */
export interface SiteTermsDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * Show the same quality terms the first-visit gate uses.
 * @example
 * const _ = true;
 */
export function SiteTermsDialog({ isOpen, onClose }: SiteTermsDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={(open) => dismissSiteTerms(open, onClose)}>
      <DialogContent className="sm:max-w-lg" data-testid="site-terms-dialog">
        <DialogHeader>
          <DialogTitle>Terms of service</DialogTitle>
          <DialogDescription>{SITE_TERMS_BODY}</DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button type="button" onClick={onClose} aria-label="Close terms of service">
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

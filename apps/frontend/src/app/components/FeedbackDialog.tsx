/**
 * Footer feedback dialog. Submit opens the shared GitHub beta-feedback issue.
 * @example
 * const _ = true;
 */

import { useState, type FormEvent, type MouseEvent } from 'react';
import { toast } from 'sonner';

import { BetaBadge } from './BetaBadge';
import { Button } from './ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import {
  BETA_FEEDBACK_ISSUES_URL,
  buildBetaFeedbackIssueUrl,
  FEEDBACK_CATEGORY_LABEL,
  FEEDBACK_CATEGORY_LABELS,
  FEEDBACK_CONTACT_LABEL,
  FEEDBACK_DIALOG_INTRO,
  FEEDBACK_MESSAGE_LABEL,
  FEEDBACK_MESSAGE_REQUIRED,
  FEEDBACK_PAGE_HINT,
  FEEDBACK_PAGE_LABEL,
  FEEDBACK_POPUP_BLOCKED,
  FEEDBACK_SUBMIT_LABEL,
  isFeedbackCategory,
  openBetaFeedbackIssue,
  type FeedbackCategory,
} from '@/utils/betaFeedback';

/**
 * Type `FeedbackDialogProps`.
 * @example
 * const _ = true;
 */
export interface FeedbackDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * Collect feedback and open the beta-feedback issue. Does not post to this app.
 * @param props.isOpen - Dialog visibility
 * @param props.onClose - Called after dismiss or a successful open
 * @example
 * const _ = true;
 */
export function FeedbackDialog({ isOpen, onClose }: FeedbackDialogProps) {
  return (
    <Dialog
      open={isOpen}
      onOpenChange={() => {
        onClose();
      }}
    >
      <DialogContent className="sm:max-w-lg" data-testid="feedback-dialog">
        <FeedbackForm onClose={onClose} />
      </DialogContent>
    </Dialog>
  );
}

/**
 * Form body. Remounts with the dialog so fields start clean.
 * @param props.onClose - Close after the issue tab opens
 * @example
 * const _ = true;
 */
function FeedbackForm({ onClose }: { onClose: () => void }) {
  const [category, setCategory] = useState<FeedbackCategory>('bug');
  const [message, setMessage] = useState('');
  const [contact, setContact] = useState('');
  const [page, setPage] = useState(() => window.location.href);
  const [messageError, setMessageError] = useState<string | null>(null);
  const trimmedMessage = message.trim();
  const href =
    trimmedMessage.length > 0
      ? buildBetaFeedbackIssueUrl({
          category,
          message: trimmedMessage,
          contact,
          page,
        })
      : BETA_FEEDBACK_ISSUES_URL;

  const submitFeedback = () => {
    if (!trimmedMessage) {
      setMessageError(FEEDBACK_MESSAGE_REQUIRED);
      return;
    }
    const opened = openBetaFeedbackIssue(href);
    if (!opened) {
      toast.error(FEEDBACK_POPUP_BLOCKED);
      return;
    }
    onClose();
  };

  const handleSubmit = (event: MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault();
    submitFeedback();
  };

  return (
    <form
      onSubmit={(event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        submitFeedback();
      }}
    >
      <DialogHeader>
        <DialogTitle className="flex items-center gap-2">
          Feedback
          <BetaBadge />
        </DialogTitle>
        <DialogDescription>{FEEDBACK_DIALOG_INTRO}</DialogDescription>
      </DialogHeader>

      <div className="space-y-4 py-2 text-left text-sm">
        <div className="space-y-2">
          <Label htmlFor="feedback-category">{FEEDBACK_CATEGORY_LABEL}</Label>
          <select
            id="feedback-category"
            className="border-input bg-input-background flex h-9 w-full rounded-md border px-3 text-sm"
            value={category}
            onChange={(event) => {
              const next = event.target.value;
              if (isFeedbackCategory(next)) setCategory(next);
            }}
          >
            {(Object.keys(FEEDBACK_CATEGORY_LABELS) as FeedbackCategory[]).map(
              (key) => (
                <option key={key} value={key}>
                  {FEEDBACK_CATEGORY_LABELS[key]}
                </option>
              ),
            )}
          </select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="feedback-message">{FEEDBACK_MESSAGE_LABEL}</Label>
          <Textarea
            id="feedback-message"
            value={message}
            aria-invalid={messageError ? true : undefined}
            aria-describedby={messageError ? 'feedback-message-error' : undefined}
            onChange={(event) => {
              setMessage(event.target.value);
              if (messageError) setMessageError(null);
            }}
          />
          {messageError ? (
            <p
              id="feedback-message-error"
              className="text-sm text-red-700 dark:text-red-300"
            >
              {messageError}
            </p>
          ) : null}
        </div>

        <div className="space-y-2">
          <Label htmlFor="feedback-contact">{FEEDBACK_CONTACT_LABEL}</Label>
          <Input
            id="feedback-contact"
            type="text"
            autoComplete="email"
            value={contact}
            onChange={(event) => setContact(event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="feedback-page">{FEEDBACK_PAGE_LABEL}</Label>
          <Input
            id="feedback-page"
            type="text"
            value={page}
            onChange={(event) => setPage(event.target.value)}
          />
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {FEEDBACK_PAGE_HINT}
          </p>
        </div>
      </div>

      <DialogFooter>
        <Button asChild>
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            data-testid="feedback-submit"
            onClick={handleSubmit}
          >
            {FEEDBACK_SUBMIT_LABEL}
          </a>
        </Button>
      </DialogFooter>
    </form>
  );
}

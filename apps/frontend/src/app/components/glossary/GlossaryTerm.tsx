/**
 * Focusable Annex 3 glossary term mark with delayed HoverCard (F38).
 */

import { useId, useState } from 'react';
import type { Annex3GlossaryEntry } from '@/data/annex3Glossary';
import { ANNEX3_GLOSSARY_CITATION } from '@/data/annex3Glossary';
import { HoverCard, HoverCardContent, HoverCardTrigger } from '../ui/hover-card';
import { useGlossaryScope } from './GlossaryScope';

const OPEN_DELAY_MS = 2000;

/**
 * Underlined glossary term with 2s hover tip and keyboard twin.
 *
 * @param props.entry - Glossary entry
 * @param props.children - Matched surface text
 * @example
 * const _ = true;
 */
export function GlossaryTerm({
  entry,
  children,
}: {
  entry: Annex3GlossaryEntry;
  children: string;
}) {
  const { hoverEnabled, openGlossaryEntry } = useGlossaryScope();
  const [open, setOpen] = useState(false);
  const tipId = useId();

  if (!hoverEnabled) {
    return <>{children}</>;
  }

  return (
    <HoverCard
      open={open}
      onOpenChange={setOpen}
      openDelay={OPEN_DELAY_MS}
      closeDelay={100}
    >
      <HoverCardTrigger asChild>
        <button
          type="button"
          data-testid={`glossary-term-${entry.id}`}
          data-glossary-term={entry.id}
          className="inline underline decoration-dotted decoration-gray-500 underline-offset-2 text-inherit bg-transparent border-0 p-0 m-0 cursor-help font-inherit"
          aria-describedby={open ? tipId : undefined}
          onKeyDown={(event) => {
            if (event.key === 'Enter' || event.key === ' ') {
              event.preventDefault();
              setOpen(true);
            }
            if (event.key === 'Escape') {
              setOpen(false);
            }
          }}
        >
          {children}
        </button>
      </HoverCardTrigger>
      <HoverCardContent
        id={tipId}
        role="dialog"
        aria-label={`${entry.term} glossary tip`}
        className="w-72 text-sm"
        data-testid={`glossary-tip-${entry.id}`}
      >
        <p className="font-medium text-gray-900 dark:text-gray-100">{entry.term}</p>
        <p className="mt-1 text-gray-700 dark:text-gray-300">{entry.shortBlurb}</p>
        <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          Source: {ANNEX3_GLOSSARY_CITATION}
        </p>
        <button
          type="button"
          className="mt-3 text-sm font-medium text-blue-700 underline dark:text-blue-300"
          data-testid={`glossary-open-${entry.id}`}
          onClick={() => {
            setOpen(false);
            openGlossaryEntry(entry.id);
          }}
        >
          Open in Glossary
        </button>
      </HoverCardContent>
    </HoverCard>
  );
}

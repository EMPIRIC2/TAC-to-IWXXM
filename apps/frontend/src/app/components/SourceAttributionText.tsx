/**
 * Operator-facing Source attribution: wrap long text and link http(s) URLs.
 *
 * Shared by Issue details (and any other surface that renders Source strings).
 * [Corpus: ui-style]
 */

import type { ReactNode } from 'react';
import { scrubInternalDocRefs } from '@/utils/internalDocRefGuard';
import { splitSourceSegments } from '@/utils/issueDetailSource';

/**
 * Render a Source attribution line with optional URL links.
 *
 * @param props.value - Attribution text (label and/or URL)
 * @returns Plain text spans and external links
 * @example
 * const _ = true;
 */
export function SourceAttributionText({ value }: { value: string }): ReactNode {
  const segments = splitSourceSegments(scrubInternalDocRefs(value));
  return (
    <>
      {segments.map((segment, index) => {
        if (segment.kind === 'text') {
          return <span key={`t-${index}`}>{segment.text}</span>;
        }
        return (
          <a
            key={`u-${index}`}
            href={segment.href}
            target="_blank"
            rel="noopener noreferrer"
            className="break-all text-blue-700 underline hover:text-blue-900 dark:text-blue-400"
          >
            {segment.href}
          </a>
        );
      })}
    </>
  );
}

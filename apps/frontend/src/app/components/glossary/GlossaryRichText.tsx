/**
 * Split a string and wrap glossary matches (F38).
 *
 * Do not use inside TAC/IWXXM editors or XML panes.
 */

import { segmentGlossaryText } from '@/utils/annex3GlossaryMatch';
import { GlossaryTerm } from './GlossaryTerm';
import { useGlossaryScope } from './GlossaryScope';

/**
 * Render plain text with optional glossary term marks.
 *
 * @param props.text - Safe chrome/content string (not editor contents)
 * @param props.as - Optional wrapper element (default span)
 * @example
 * const _ = true;
 */
export function GlossaryRichText({
  text,
  className,
  as: Tag = 'span',
}: {
  text: string;
  className?: string;
  as?: 'span' | 'p' | 'div';
}) {
  const { hoverEnabled } = useGlossaryScope();
  if (!hoverEnabled) {
    return <Tag className={className}>{text}</Tag>;
  }

  const segments = segmentGlossaryText(text);
  return (
    <Tag className={className} data-glossary-rich-text="">
      {segments.map((segment, index) => {
        if (segment.kind === 'text') {
          return <span key={`t-${index}`}>{segment.value}</span>;
        }
        return (
          <GlossaryTerm key={`g-${segment.entry.id}-${index}`} entry={segment.entry}>
            {segment.value}
          </GlossaryTerm>
        );
      })}
    </Tag>
  );
}

/**
 * Top-level Annex 3 Glossary page (F38) — paraphrases + citation only.
 */

import { useEffect, useMemo, useState } from 'react';
import {
  ANNEX3_GLOSSARY_CITATION,
  ANNEX3_GLOSSARY_ENTRIES,
  ANNEX3_LIMITED_MEANING_NOTES,
} from '@/data/annex3Glossary';
import { shellFrameClass, useLiveConvertLayout } from '@/utils/liveConvertLayout';
import { GlossaryRichText } from './glossary/GlossaryRichText';

/**
 * Props for {@link Annex3GlossaryPage}.
 * @example
 * const _ = true;
 */
export interface Annex3GlossaryPageProps {
  /** Optional entry id to scroll into view. */
  focusTermId?: string | null;
  /** Clears focus after scroll. */
  onFocusHandled?: () => void;
}

/**
 * Operator Glossary shell page (sibling of Convert / Decode visuals / History / Catalog).
 *
 * @example
 * const _ = true;
 */
export function Annex3GlossaryPage({
  focusTermId = null,
  onFocusHandled,
}: Annex3GlossaryPageProps) {
  const { layout } = useLiveConvertLayout();
  const [query, setQuery] = useState('');

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) {
      return [...ANNEX3_GLOSSARY_ENTRIES].sort((a, b) => a.term.localeCompare(b.term));
    }
    return ANNEX3_GLOSSARY_ENTRIES.filter((entry) => {
      const hay = [entry.term, ...(entry.aliases ?? []), entry.pageBody]
        .join(' ')
        .toLowerCase();
      return hay.includes(q);
    }).sort((a, b) => a.term.localeCompare(b.term));
  }, [query]);

  useEffect(() => {
    if (!focusTermId) {
      return;
    }
    const el = document.getElementById(`glossary-entry-${focusTermId}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      el.focus({ preventScroll: true });
    }
    onFocusHandled?.();
  }, [focusTermId, onFocusHandled]);

  return (
    <div
      className="min-h-screen bg-gray-50 dark:bg-gray-900"
      data-testid="annex3-glossary-page"
    >
      <div
        className={`mx-auto w-full space-y-6 px-4 py-6 ${shellFrameClass(layout.span)}`}
      >
        <header className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Glossary
            </h1>
            <span
              className="rounded-md border border-amber-300 bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-900 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-100"
              data-testid="glossary-beta-badge"
            >
              Beta
            </span>
          </div>
          <GlossaryRichText
            as="p"
            className="text-sm text-gray-600 dark:text-gray-400"
            text="Short paraphrases of selected aviation weather terms. These texts are not official ICAO definitions."
          />
          <p
            className="text-xs text-gray-500 dark:text-gray-400"
            data-testid="glossary-citation"
          >
            Source: {ANNEX3_GLOSSARY_CITATION}. Get the official Annex 3 manual from
            ICAO for the authoritative wording.
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Feedback welcome via GitHub Issues (beta-feedback label).
          </p>
        </header>

        <div>
          <label htmlFor="glossary-search" className="sr-only">
            Search glossary
          </label>
          <input
            id="glossary-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search terms"
            className="w-full max-w-md rounded-md border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-950 dark:text-gray-100"
            data-testid="glossary-search"
          />
        </div>

        <ul className="space-y-4" data-testid="glossary-entry-list">
          {filtered.map((entry) => (
            <li
              key={entry.id}
              id={`glossary-entry-${entry.id}`}
              tabIndex={-1}
              className="rounded-md border border-gray-200 bg-white p-4 outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-950"
              data-testid={`glossary-entry-${entry.id}`}
            >
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {entry.term}
                {entry.aliases && entry.aliases.length > 0 ? (
                  <span className="ml-2 text-sm font-normal text-gray-500">
                    ({entry.aliases.join(', ')})
                  </span>
                ) : null}
              </h2>
              <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
                {entry.pageBody}
              </p>
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                {entry.citation}
              </p>
            </li>
          ))}
          {filtered.length === 0 ? (
            <li className="text-sm text-gray-600 dark:text-gray-400">
              No terms match that search.
            </li>
          ) : null}
        </ul>

        <section
          className="rounded-md border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-950"
          data-testid="glossary-limited-meaning"
          aria-labelledby="glossary-limited-meaning-heading"
        >
          <h2
            id="glossary-limited-meaning-heading"
            className="text-lg font-semibold text-gray-900 dark:text-gray-100"
          >
            Limited meaning notes
          </h2>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            These everyday verbs have a limited meaning in Annex 3. This page lists them
            for clarity. The app does not attach hover tips to these verbs.
          </p>
          <ul className="mt-3 space-y-3">
            {ANNEX3_LIMITED_MEANING_NOTES.map((note) => (
              <li key={note.id}>
                <p className="font-medium text-gray-900 dark:text-gray-100">
                  {note.term}
                </p>
                <p className="text-sm text-gray-700 dark:text-gray-300">{note.note}</p>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}

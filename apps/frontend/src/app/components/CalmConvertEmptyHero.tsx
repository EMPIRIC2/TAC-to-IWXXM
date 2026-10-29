/**
 * First-visit / empty Convert hero (Calmer Convert screen 4 / UJ-088).
 *
 * Layout: title, one TAC card with example chips as a bar above the editor, then
 * drop/browse + Convert; tight Other tasks / profile under the card.
 *
 * [Corpus: product §F7] [Corpus: journeys §UJ-088] [Corpus: ui-style]
 */

import type { ReactNode } from 'react';

import {
  CalmConvertEmptyAffordances,
  type CalmExampleChip,
} from './CalmConvertEmptyAffordances';
import { Button } from './ui/button';
import { CALM_CONVERT_PRIMARY_LABEL } from '/utils/convertCalmState';

export type { CalmExampleChip };

/**
 * Props for the empty Convert hero.
 * @example
 * const _ = true;
 */
export interface CalmConvertEmptyHeroProps {
  children: ReactNode;
  convertDisabled: boolean;
  isConverting: boolean;
  onConvert: () => void;
  exampleChips: CalmExampleChip[];
  onExampleChip: (id: string) => void;
  profileLabel: string;
  onChangeProfile: () => void;
  onOtherTask?: (task: 'ahl' | 'validate_iwxxm' | 'collect') => void;
  onBrowseFiles?: () => void;
}

/**
 * Empty Convert layout: examples bar above TAC; Other tasks tight below the card.
 * @example
 * const _ = true;
 */
export function CalmConvertEmptyHero({
  children,
  convertDisabled,
  isConverting,
  onConvert,
  exampleChips,
  onExampleChip,
  profileLabel,
  onChangeProfile,
  onOtherTask,
  onBrowseFiles,
}: CalmConvertEmptyHeroProps) {
  return (
    <section
      className="mx-auto flex w-full max-w-3xl flex-col items-stretch gap-3 py-10"
      data-testid="convert-empty-hero"
    >
      <div className="space-y-2.5">
        <h2 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
          Convert a TAC report to IWXXM
        </h2>
        <p className="max-w-prose text-base text-gray-600 dark:text-gray-400">
          Paste a METAR, TAF, SIGMET, AIRMET or advisory. The report type is detected
          for you, and the IWXXM preview updates as you type.
        </p>
      </div>

      <div
        className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-900"
        data-testid="convert-empty-card"
      >
        {exampleChips.length > 0 ? (
          <div
            className="border-b border-gray-100 px-4 py-2.5 dark:border-gray-800"
            data-testid="convert-examples-bar"
          >
            <CalmConvertEmptyAffordances
              exampleChips={exampleChips}
              onExampleChip={onExampleChip}
            />
          </div>
        ) : null}
        <div className="px-1 pt-1">{children}</div>
        <div className="flex flex-wrap items-center gap-3 border-t border-dashed border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-950/60">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Or drop .tac, .txt, .xml or .zip files
            {onBrowseFiles ? (
              <>
                {' · '}
                <button
                  type="button"
                  className="font-medium text-blue-700 underline-offset-2 hover:underline dark:text-blue-300"
                  data-testid="convert-empty-browse"
                  onClick={onBrowseFiles}
                >
                  browse
                </button>
              </>
            ) : null}
          </p>
          <div className="ml-auto">
            <Button
              type="button"
              variant="default"
              data-testid="convert-primary-cta"
              disabled={convertDisabled}
              aria-busy={isConverting}
              onClick={onConvert}
              className="min-w-[11rem]"
            >
              {CALM_CONVERT_PRIMARY_LABEL}
            </Button>
          </div>
        </div>
      </div>

      <CalmConvertEmptyAffordances
        exampleChips={[]}
        onExampleChip={onExampleChip}
        onOtherTask={onOtherTask}
        profileLabel={profileLabel}
        onChangeProfile={onChangeProfile}
      />
    </section>
  );
}

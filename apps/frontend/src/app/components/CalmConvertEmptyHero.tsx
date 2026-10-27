/**
 * First-visit / empty Convert hero (Calmer Convert screen 4 / UJ-088).
 *
 * Layout tracks the Calmer Convert empty mockup: left-aligned title, TAC card with
 * primary CTA in the card footer, example chips, quiet other-task links, profile Change.
 *
 * [Corpus: product §F7] [Corpus: journeys §UJ-088]
 */

import type { ReactNode } from 'react';

import { Button } from './ui/button';
import { CALM_CONVERT_PRIMARY_LABEL } from '/utils/convertCalmState';

/**
 * One example chip on the empty Convert hero.
 * @example
 * const _ = true;
 */
export interface CalmExampleChip {
  id: string;
  label: string;
}

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
 * Centered empty Convert layout with one primary CTA and example chips.
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
      className="mx-auto flex w-full max-w-3xl flex-col items-stretch gap-7 py-10"
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

      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-900">
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

      <div
        className="flex flex-wrap items-center gap-2.5"
        data-testid="convert-example-chips"
      >
        <span className="mr-1 text-sm text-gray-600 dark:text-gray-400">
          Try an example
        </span>
        {exampleChips.map((chip) => (
          <Button
            key={chip.id}
            type="button"
            variant="outline"
            size="sm"
            data-testid={`convert-example-chip-${chip.id}`}
            onClick={() => onExampleChip(chip.id)}
            className="rounded-full"
          >
            {chip.label}
          </Button>
        ))}
      </div>

      {onOtherTask ? (
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-gray-200 pt-5 text-sm dark:border-gray-700">
          <span className="text-gray-500 dark:text-gray-400">Other tasks</span>
          <button
            type="button"
            className="text-blue-700 underline-offset-2 hover:underline dark:text-blue-300"
            onClick={() => onOtherTask('ahl')}
          >
            Convert a full bulletin (AHL)
          </button>
          <button
            type="button"
            className="text-blue-700 underline-offset-2 hover:underline dark:text-blue-300"
            onClick={() => onOtherTask('validate_iwxxm')}
          >
            Validate existing IWXXM
          </button>
          <button
            type="button"
            className="text-blue-700 underline-offset-2 hover:underline dark:text-blue-300"
            onClick={() => onOtherTask('collect')}
          >
            Build a COLLECT bundle
          </button>
        </div>
      ) : null}

      <footer className="text-sm text-gray-600 dark:text-gray-400">
        Profile:{' '}
        <span className="text-gray-900 dark:text-gray-100">{profileLabel}</span>
        {' · '}
        <button
          type="button"
          className="font-medium text-blue-700 underline-offset-2 hover:underline dark:text-blue-300"
          data-testid="convert-profile-change"
          onClick={onChangeProfile}
        >
          Change
        </button>
      </footer>
    </section>
  );
}

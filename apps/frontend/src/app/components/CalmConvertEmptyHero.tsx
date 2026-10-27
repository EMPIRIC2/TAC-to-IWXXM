/**
 * First-visit / empty Convert hero (Calmer Convert screen 4 / UJ-088).
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
}: CalmConvertEmptyHeroProps) {
  return (
    <section
      className="mx-auto flex w-full max-w-2xl flex-col items-stretch gap-6 py-8"
      data-testid="convert-empty-hero"
    >
      <div className="space-y-2 text-center">
        <h2 className="text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
          Convert a TAC report to IWXXM
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Paste a report, auto-detect the product, and preview IWXXM before you convert.
        </p>
      </div>

      <div className="space-y-3">{children}</div>

      <div className="flex flex-wrap items-center justify-center gap-2">
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

      <div className="space-y-2" data-testid="convert-example-chips">
        <p className="text-center text-xs font-medium uppercase tracking-wide text-gray-500">
          Try an example
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {exampleChips.map((chip) => (
            <Button
              key={chip.id}
              type="button"
              variant="outline"
              size="sm"
              data-testid={`convert-example-chip-${chip.id}`}
              onClick={() => onExampleChip(chip.id)}
            >
              {chip.label}
            </Button>
          ))}
        </div>
      </div>

      {onOtherTask ? (
        <div className="flex flex-wrap justify-center gap-x-4 gap-y-1 text-sm text-gray-600 dark:text-gray-400">
          <button
            type="button"
            className="underline-offset-2 hover:underline"
            onClick={() => onOtherTask('ahl')}
          >
            Convert full bulletin (AHL)
          </button>
          <button
            type="button"
            className="underline-offset-2 hover:underline"
            onClick={() => onOtherTask('validate_iwxxm')}
          >
            Validate existing IWXXM
          </button>
          <button
            type="button"
            className="underline-offset-2 hover:underline"
            onClick={() => onOtherTask('collect')}
          >
            Build COLLECT bundle
          </button>
        </div>
      ) : null}

      <footer className="flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
        <span>
          Profile:{' '}
          <span className="text-gray-800 dark:text-gray-200">{profileLabel}</span>
        </span>
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

/**
 * Empty Convert secondary affordances (UJ-088) — examples + other tasks.
 *
 * Example chips sit in a bar above the TAC editor inside the main convert card;
 * Other tasks / profile sit in a tight row under that card (one composition).
 *
 * [Corpus: product §F7] [Corpus: journeys §UJ-088] [Corpus: ui-style]
 */

import { Button } from './ui/button';

/**
 * One example chip under the empty Convert editor.
 * @example
 * const _ = true;
 */
export interface CalmExampleChip {
  id: string;
  label: string;
}

/**
 * Props for empty-state example / other-task affordances.
 * @example
 * const _ = true;
 */
export interface CalmConvertEmptyAffordancesProps {
  exampleChips: CalmExampleChip[];
  onExampleChip: (id: string) => void;
  onOtherTask?: (task: 'ahl' | 'validate_iwxxm' | 'collect') => void;
  profileLabel?: string;
  onChangeProfile?: () => void;
}

/**
 * Quiet affordances: example chips (in-card) and/or other-task links + profile.
 *
 * @param props - Chip list and handlers
 * @returns Empty-state affordances (omit empty sections)
 * @example
 * const _ = true;
 */
export function CalmConvertEmptyAffordances({
  exampleChips,
  onExampleChip,
  onOtherTask,
  profileLabel,
  onChangeProfile,
}: CalmConvertEmptyAffordancesProps) {
  const showExamples = exampleChips.length > 0;
  const showOtherTasks = Boolean(onOtherTask);
  const showProfile = Boolean(profileLabel && onChangeProfile);
  if (!showExamples && !showOtherTasks && !showProfile) {
    return null;
  }

  return (
    <div className="space-y-2" data-testid="convert-empty-affordances">
      {showExamples ? (
        <div
          className="flex flex-wrap items-center gap-2"
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
      ) : null}

      {showOtherTasks ? (
        <div className="flex flex-wrap items-center gap-x-5 gap-y-1 text-sm">
          <span className="text-gray-500 dark:text-gray-400">Other tasks</span>
          <button
            type="button"
            className="text-blue-700 underline-offset-2 hover:underline dark:text-blue-300"
            onClick={() => onOtherTask?.('ahl')}
          >
            Convert a full bulletin (AHL)
          </button>
          <button
            type="button"
            className="text-blue-700 underline-offset-2 hover:underline dark:text-blue-300"
            onClick={() => onOtherTask?.('validate_iwxxm')}
          >
            Validate existing IWXXM
          </button>
          <button
            type="button"
            className="text-blue-700 underline-offset-2 hover:underline dark:text-blue-300"
            onClick={() => onOtherTask?.('collect')}
          >
            Build a COLLECT bundle
          </button>
        </div>
      ) : null}

      {showProfile ? (
        <p className="text-sm text-gray-600 dark:text-gray-400">
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
        </p>
      ) : null}
    </div>
  );
}

/**
 * Diff the latest successful convert against the previous version.
 */

import { unifiedLineDiff } from '/utils/unifiedLineDiff';
import type { OutputVersion } from '/utils/outputVersions';

/**
 * Type `OutputVersionCompareProps`.
 * @example
 * const _ = true;
 */
export interface OutputVersionCompareProps {
  versions: OutputVersion[];
}

/**
 * Show added and removed XML lines between the last two versions.
 *
 * @param props.versions - Chronological convert versions
 * @example
 * const _ = true;
 */
export function OutputVersionCompare({ versions }: OutputVersionCompareProps) {
  if (versions.length < 2) {
    return null;
  }
  const previous = versions[versions.length - 2] as OutputVersion;
  const latest = versions[versions.length - 1] as OutputVersion;
  const changes = unifiedLineDiff(previous.xml, latest.xml).filter(
    (line) => line.op !== 'equal',
  );

  return (
    <section
      data-testid="output-version-compare"
      aria-label="Compare versions"
      className="mt-3 rounded-md border border-gray-200 p-3 text-xs dark:border-gray-700"
    >
      <h3 className="mb-2 font-semibold text-gray-900 dark:text-gray-100">
        Compare versions
      </h3>
      <p className="mb-2 text-gray-600 dark:text-gray-300">
        Version {versions.length} against version {versions.length - 1}
        {latest.conversionProfile
          ? `. Conversion profile: ${latest.conversionProfile}`
          : ''}
      </p>
      {changes.length === 0 ? (
        <p>No XML line changes.</p>
      ) : (
        <ol className="space-y-1 font-mono">
          {changes.slice(0, 40).map((line, index) => (
            <li key={`${line.op}-${index}-${line.text}`}>
              <span className="mr-2 font-sans font-semibold">
                {line.op === 'add' ? 'Added' : 'Removed'}
              </span>
              {line.text}
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}

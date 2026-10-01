/**
 * Pick one report from an AHL bulletin, or keep the whole bulletin in view.
 */

import type { BulletinReport } from '/utils/bulletinReportList';

/**
 * Type `BulletinReportListProps`.
 * @example
 * const _ = true;
 */
export interface BulletinReportListProps {
  reports: BulletinReport[];
  /** Null while the whole bulletin is in the editor. */
  selectedIndex: number | null;
  onSelect: (index: number, tac: string) => void;
  onShowAll: () => void;
}

/**
 * Report list for bulletin mode.
 *
 * @param props.reports - Reports found in the bulletin
 * @param props.selectedIndex - Open report, if any
 * @example
 * const _ = true;
 */
export function BulletinReportList({
  reports,
  selectedIndex,
  onSelect,
  onShowAll,
}: BulletinReportListProps) {
  return (
    <div className="mb-3" data-testid="bulletin-report-list">
      <p className="mb-1 text-xs font-medium text-gray-700 dark:text-gray-200">
        Reports in this bulletin
      </p>
      <div
        className="flex flex-wrap gap-1"
        role="group"
        aria-label="Reports in this bulletin"
      >
        <button
          type="button"
          aria-pressed={selectedIndex === null}
          className="rounded px-2 py-1 text-xs font-medium text-gray-900 dark:text-gray-100"
          onClick={onShowAll}
        >
          Whole bulletin
        </button>
        {reports.map((report, index) => (
          <button
            key={`${index}-${report.title}`}
            type="button"
            aria-pressed={selectedIndex === index}
            className="rounded px-2 py-1 text-left font-mono text-xs text-gray-900 dark:text-gray-100"
            onClick={() => onSelect(index, report.tac)}
          >
            Report {index + 1} {report.title}
          </button>
        ))}
      </div>
    </div>
  );
}

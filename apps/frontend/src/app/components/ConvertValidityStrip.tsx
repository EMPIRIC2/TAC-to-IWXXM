/**
 * Post-convert validity strip (Calmer Convert screen 2 / TC-UX-CALM-010).
 */

export interface ConvertValidityStripProps {
  notesCount?: number;
  onNotesClick?: () => void;
}

/**
 * Green success banner for a valid IWXXM bulletin.
 */
export function ConvertValidityStrip({
  notesCount = 0,
  onNotesClick,
}: ConvertValidityStripProps) {
  return (
    <div
      className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-md bg-emerald-600 px-4 py-3 text-white"
      data-testid="convert-validity-strip"
      role="status"
    >
      <div className="space-y-1">
        <p className="font-semibold">Valid IWXXM bulletin, ready to send</p>
        <ul className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-emerald-50">
          <li>TAC decoded</li>
          <li>XML schema passed</li>
          <li>Schematron passed</li>
        </ul>
      </div>
      {notesCount > 0 && onNotesClick ? (
        <button
          type="button"
          className="text-sm font-medium underline underline-offset-2"
          onClick={onNotesClick}
        >
          {notesCount} notes
        </button>
      ) : null}
    </div>
  );
}

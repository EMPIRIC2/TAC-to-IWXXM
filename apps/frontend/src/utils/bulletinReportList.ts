/**
 * List the TAC reports inside a pasted AHL bulletin so the operator can
 * open one report in the live panes.
 */

/**
 * Type `BulletinReport`.
 * @example
 * const _ = true;
 */
export interface BulletinReport {
  tac: string;
  title: string;
}

const REPORT_RE =
  /(?:^|\n)\s*((?:METAR|SPECI|TAF)\b[\s\S]*?=|[A-Z]{4}\s+(?:SIGMET|AIRMET)\b[\s\S]*?=)/g;

/**
 * TAC reports in bulletin order. The abbreviated heading is not a report.
 *
 * @param text - Full bulletin text
 * @returns Reports that can be opened on their own
 * @example
 * const _ = true;
 */
export function listBulletinReports(text: string): BulletinReport[] {
  if (!text.trim()) {
    return [];
  }
  const reports: BulletinReport[] = [];
  for (const match of text.matchAll(REPORT_RE)) {
    const tac = String(match[1]).trim();
    reports.push({
      tac,
      title: tac.split(/\s+/).slice(0, 4).join(' '),
    });
  }
  return reports;
}

/**
 * Replace one listed report inside the full bulletin.
 *
 * @param full - Bulletin text
 * @param index - Zero-based report index
 * @param next - Replacement TAC
 * @returns Bulletin with that report replaced
 * @example
 * const _ = true;
 */
export function replaceBulletinReport(
  full: string,
  index: number,
  next: string,
): string {
  const current = listBulletinReports(full)[index];
  if (!current) {
    return full;
  }
  const pos = full.indexOf(current.tac);
  return full.slice(0, pos) + next + full.slice(pos + current.tac.length);
}

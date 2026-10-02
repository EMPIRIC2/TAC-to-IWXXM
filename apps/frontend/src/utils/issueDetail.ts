/**
 * Build the fuller description shown when an operator opens an issue row.
 *
 * Catalog fields fill rule text, source, product, and tags when the code is loaded.
 */

import type { LintIssueCatalogEntry } from '@/utils/api';
import { ISSUE_DETAIL_EMPTY } from '@/utils/issueDetailCopy';

/**
 * Type `IssueDetailModel`.
 * @example
 * const _ = true;
 */
export type IssueDetailModel = {
  code: string;
  severity: string;
  message: string;
  rule: string;
  hint: string;
  source: string;
  product: string;
  tags: string;
  location: string;
};

/**
 * Type `IssueDetailInput`.
 * @example
 * const _ = true;
 */
export type IssueDetailInput = {
  code?: string | null;
  severity?: string | null;
  message?: string | null;
  hint?: string | null;
  location?: string | null;
  start?: number | null;
  end?: number | null;
  catalog?: LintIssueCatalogEntry | null;
};

/**
 * Show a trimmed string, or an em dash when it is blank.
 *
 * @param value - Operator field
 * @returns Visible text
 * @example
 * const _ = true;
 */
function filled(value: string | null | undefined): string {
  const trimmed = (value ?? '').trim();
  return trimmed || ISSUE_DETAIL_EMPTY;
}

/**
 * Source line from a catalog row.
 *
 * @param catalog - Loaded catalog row, when the code is known
 * @returns Attribution, source id, or an em dash
 * @example
 * const _ = true;
 */
function sourceLabel(catalog: LintIssueCatalogEntry | null | undefined): string {
  if (!catalog) {
    return ISSUE_DETAIL_EMPTY;
  }
  const attribution = (catalog.source_attribution ?? '').trim();
  if (attribution) {
    return attribution;
  }
  const sourceId = (catalog.source_id ?? '').trim();
  if (!sourceId) {
    return ISSUE_DETAIL_EMPTY;
  }
  const url = (catalog.source_url ?? '').trim();
  return url ? `${sourceId} (${url})` : sourceId;
}

/**
 * Location line from a parser span or a location sentence.
 *
 * @param location - Free-text location
 * @param start - Inclusive offset
 * @param end - Exclusive offset
 * @returns Location text or an em dash
 * @example
 * const _ = true;
 */
function locationLabel(
  location: string | null | undefined,
  start: number | null | undefined,
  end: number | null | undefined,
): string {
  const sentence = (location ?? '').trim();
  if (sentence) {
    return sentence;
  }
  if (typeof start === 'number' && typeof end === 'number') {
    return `Characters ${start}–${end}`;
  }
  return ISSUE_DETAIL_EMPTY;
}

/**
 * Assemble one issue detail from the row and an optional catalog entry.
 *
 * @param input - Row fields plus the catalog row for its code
 * @returns Plain fields for the dialog
 * @example
 * const _ = true;
 */
export function buildIssueDetail(input: IssueDetailInput): IssueDetailModel {
  const catalog = input.catalog ?? null;
  const message = filled(input.message);
  const ruleRaw = (catalog?.message_template ?? '').trim();
  const rule =
    ruleRaw && ruleRaw !== (input.message ?? '').trim() ? ruleRaw : ISSUE_DETAIL_EMPTY;
  const tags = (catalog?.tags ?? []).map((tag) => tag.trim()).filter(Boolean);
  return {
    code: filled(input.code ?? catalog?.code),
    severity: filled(input.severity ?? catalog?.severity),
    message,
    rule,
    hint: filled(input.hint),
    source: sourceLabel(catalog),
    product: filled(catalog?.product),
    tags: tags.length > 0 ? tags.join(', ') : ISSUE_DETAIL_EMPTY,
    location: locationLabel(input.location, input.start, input.end),
  };
}

/**
 * First bracketed code in a console line that is in the loaded catalog.
 *
 * @param message - Console line text
 * @param catalog - Catalog index
 * @returns Code, or undefined when none of the tokens are loaded
 * @example
 * const _ = true;
 */
export function catalogCodeInMessage(
  message: string,
  catalog?: Map<string, LintIssueCatalogEntry>,
): string | undefined {
  if (!catalog || catalog.size === 0) {
    return undefined;
  }
  for (const match of message.matchAll(/\[([A-Z][A-Z0-9_]*)\]/g)) {
    const code = match[1];
    if (code && catalog.has(code)) {
      return code;
    }
  }
  return undefined;
}

/**
 * Detail for one live console line.
 *
 * @param line - Console line
 * @param catalog - Catalog index
 * @returns Dialog fields
 * @example
 * const _ = true;
 */
export function issueDetailFromConsoleLine(
  line: { level: string; message: string },
  catalog?: Map<string, LintIssueCatalogEntry>,
): IssueDetailModel {
  const code = catalogCodeInMessage(line.message, catalog);
  return buildIssueDetail({
    code,
    severity: line.level,
    message: line.message,
    catalog: code && catalog ? catalog.get(code) : null,
  });
}

/**
 * Read a non-empty string field from a diagnostic record.
 *
 * @param item - Diagnostic object
 * @param key - Field name
 * @returns Trimmed text, or null
 * @example
 * const _ = true;
 */
function textField(item: Record<string, unknown>, key: string): string | null {
  const value = item[key];
  if (typeof value !== 'string') {
    return null;
  }
  const trimmed = value.trim();
  return trimmed || null;
}

/**
 * Read a finite numeric field from a diagnostic record.
 *
 * @param item - Diagnostic object
 * @param key - Field name
 * @returns Number, or null
 * @example
 * const _ = true;
 */
function numberField(item: Record<string, unknown>, key: string): number | null {
  const value = item[key];
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

/**
 * JSON text for a diagnostic that has no message or code.
 *
 * @param item - Diagnostic object
 * @returns JSON, or the object text when it cannot be serialized
 * @example
 * const _ = true;
 */
function jsonFallback(item: Record<string, unknown>): string {
  try {
    return JSON.stringify(item);
  } catch {
    return String(item);
  }
}

/**
 * Detail for a quality-metrics or validate diagnostic object.
 *
 * @param value - Issue string, object, or empty
 * @param catalog - Catalog index
 * @returns Dialog fields
 * @example
 * const _ = true;
 */
export function issueDetailFromUnknown(
  value: unknown,
  catalog?: Map<string, LintIssueCatalogEntry>,
): IssueDetailModel {
  if (typeof value === 'string') {
    return buildIssueDetail({ message: value });
  }
  if (!value || typeof value !== 'object') {
    return buildIssueDetail({ message: value == null ? 'Issue' : String(value) });
  }
  const item = value as Record<string, unknown>;
  const code = textField(item, 'code');
  const message =
    textField(item, 'message') ??
    textField(item, 'detail') ??
    (code ? '' : jsonFallback(item));
  return buildIssueDetail({
    code,
    severity: textField(item, 'severity'),
    message,
    hint: textField(item, 'hint') ?? textField(item, 'remediation'),
    location: textField(item, 'location'),
    start: numberField(item, 'start'),
    end: numberField(item, 'end'),
    catalog: code && catalog ? (catalog.get(code) ?? null) : null,
  });
}

/**
 * Plain-language status for one convert result.
 *
 * Valid, valid with notes, or needs attention. An invalid result must not be published.
 */

/** Browser and page title for the converter. */
export const PAGE_TITLE = 'TAC to IWXXM';

/** Clean convert. */
export const RESULT_STATUS_VALID = 'Valid';

/** Convert succeeded and only informational notes were returned. */
export const RESULT_STATUS_NOTES = 'Valid with notes';

/** Errors or invalid XML. */
export const RESULT_STATUS_ATTENTION = 'Needs attention';

/** Shown when the result must not be published. */
export const DO_NOT_PUBLISH_LABEL = 'Do not publish';

/**
 * Status id for one result card.
 * @example
 * const _ = true;
 */
export type ResultCardStatus = 'valid' | 'valid-with-notes' | 'needs-attention';

/**
 * One error or note line. The code is optional and secondary.
 * @example
 * const _ = true;
 */
export interface ResultCardLine {
  message: string;
  code?: string;
}

/**
 * Operator-facing assessment of one result.
 * @example
 * const _ = true;
 */
export interface ResultCardAssessment {
  status: ResultCardStatus;
  statusLabel: string;
  publishBlocked: boolean;
  errors: ResultCardLine[];
  notes: ResultCardLine[];
}

/**
 * Issue fields the result card reads. Other issue fields are ignored.
 * @example
 * const _ = true;
 */
export interface ResultIssueInput {
  severity?: string | null;
  message?: string | null;
  code?: string | null;
}

const NOTE_SEVERITIES = new Set(['info', 'warning', 'warn', 'note']);

/** Soft schema/Schematron failure on convert — must not be published. */
const PUBLISH_BLOCKING_CODES = new Set(['OUTPUT_VALIDATION_WARNING']);

/**
 * Error severity blocks publish. Missing severity is an error. Info and warnings are notes.
 *
 * @param severity - Engine severity token
 * @returns True when the issue belongs with errors
 * @example
 * const _ = true;
 */
export function isErrorSeverity(severity: string | null | undefined): boolean {
  const token = (severity ?? '').trim().toLowerCase();
  return !NOTE_SEVERITIES.has(token);
}

/**
 * True when an issue code means the XML must not be published.
 *
 * @param code - Issue code from convert/validate
 * @returns Whether this code alone blocks publish
 * @example
 * const _ = true;
 */
export function codeBlocksPublish(code: string | null | undefined): boolean {
  const token = (code ?? '').trim().toUpperCase();
  return PUBLISH_BLOCKING_CODES.has(token);
}

/**
 * True when XML text is missing or not well-formed.
 *
 * @param xml - Converted XML, when the caller has it
 * @returns True when this text must not be published
 * @example
 * const _ = true;
 */
export function xmlBlocksPublish(xml: string | null | undefined): boolean {
  if (xml == null) {
    return false;
  }
  const trimmed = xml.trim();
  if (!trimmed) {
    return true;
  }
  // Require a tag-shaped payload. Do not use DOMParser here: prefixed IWXXM
  // without xmlns (common in stubs) is still downloadable; schema failures
  // arrive as OUTPUT_VALIDATION_WARNING / ok=false instead.
  if (!trimmed.includes('<') || !trimmed.includes('>')) {
    return true;
  }
  return false;
}

/**
 * Split errors from notes and choose the card status.
 *
 * @param input.errors - Plain error strings from the convert response
 * @param input.issues - Structured issues
 * @param input.xml - IWXXM text for this result
 * @param input.ok - False when the convert response says the result is not ok
 * @returns Status, publish block, errors, and notes
 * @example
 * const _ = true;
 */
export function assessResultCard(input: {
  errors?: readonly string[];
  issues?: readonly ResultIssueInput[];
  xml?: string | null;
  ok?: boolean | null;
}): ResultCardAssessment {
  const errors: ResultCardLine[] = [];
  const notes: ResultCardLine[] = [];

  for (const error of input.errors ?? []) {
    const message = error.trim();
    if (message) {
      errors.push({ message });
    }
  }

  let blockingCode = false;
  for (const issue of input.issues ?? []) {
    const message = issue.message?.trim() ?? '';
    if (!message) {
      continue;
    }
    const code = issue.code?.trim();
    const line: ResultCardLine = code ? { message, code } : { message };
    if (codeBlocksPublish(code)) {
      blockingCode = true;
      errors.push(line);
    } else if (isErrorSeverity(issue.severity)) {
      errors.push(line);
    } else {
      notes.push(line);
    }
  }

  const publishBlocked =
    errors.length > 0 ||
    blockingCode ||
    input.ok === false ||
    xmlBlocksPublish(input.xml);

  if (publishBlocked) {
    return {
      status: 'needs-attention',
      statusLabel: RESULT_STATUS_ATTENTION,
      publishBlocked: true,
      errors,
      notes,
    };
  }
  if (notes.length > 0) {
    return {
      status: 'valid-with-notes',
      statusLabel: RESULT_STATUS_NOTES,
      publishBlocked: false,
      errors,
      notes,
    };
  }
  return {
    status: 'valid',
    statusLabel: RESULT_STATUS_VALID,
    publishBlocked: false,
    errors,
    notes,
  };
}

/**
 * Assess a converted file, including older cards that have no stored issues.
 *
 * @param file.convertedContent - IWXXM text
 * @param file.resultCard - Issues captured when this result was converted
 * @returns Card assessment
 * @example
 * const _ = true;
 */
export function assessConvertedFile(file: {
  convertedContent: string;
  resultCard?: {
    errors?: readonly string[];
    issues?: readonly ResultIssueInput[];
    ok?: boolean;
  };
}): ResultCardAssessment {
  return assessResultCard({
    errors: file.resultCard?.errors,
    issues: file.resultCard?.issues,
    xml: file.convertedContent,
    ok: file.resultCard?.ok,
  });
}

/**
 * Thin aliases over openapi-typescript schemas (EV-052 / AC9 / D-S061-orval=1).
 *
 * Prefer these for high-churn convert / validate / lint response shapes so the FE
 * stays aligned with the committed OpenAPI snapshot. Array fields that OpenAPI
 * marks optional (Pydantic ``default_factory``) are required here to match the
 * msgspec runtime contract and existing callers.
 */
import type { components } from '../generated/openapi';

type Schemas = components['schemas'];

/** OpenAPI ``ConversionIssue`` — severity optional for partial fixtures. */
export type ConversionIssue = Omit<Schemas['ConversionIssue'], 'severity'> & {
  severity?: Schemas['ConversionIssueSeverity'];
};

/**
 * OpenAPI ``ConversionResult`` plus legacy optional XML aliases used by mocks /
 * older clients. Prefer ``content`` (canonical OpenAPI field).
 */
export type ConversionResult = Omit<Schemas['ConversionResult'], 'tac_input'> & {
  tac_input?: string | null;
  iwxxm_xml?: string;
  xml?: string;
};

/** Soft-preview spans — OpenAPI allows null; FE views use ``string | undefined``. */
export type FailedSpan = {
  start: number;
  end: number;
  code?: string;
  message?: string;
};

/** OpenAPI ``ConversionResponse`` (POST /api/v1/convert). */
export type ConversionResponse = {
  results: ConversionResult[];
  errors: string[];
  issues?: ConversionIssue[];
  total_processed: number;
  successful: number;
  failed: number;
  metadata?: Schemas['ConversionResponse']['metadata'];
  ok?: Schemas['ConversionResponse']['ok'];
  failed_spans?: FailedSpan[];
};

/** OpenAPI ``ValidateResponse`` (POST /api/v1/validate). */
export type ValidateResponse = Schemas['ValidateResponse'] & {
  is_valid: boolean;
  version: string;
  segments?: Schemas['DecodeSegmentModel'][];
  summary?: string | null;
};

export type ValidateIssue = Schemas['ValidateIssueModel'];

export type LintIssue = Schemas['LintIssueModel'];
export type LintFix = Schemas['LintFixModel'];

export type LintTacResponse = {
  ok: boolean;
  issues: LintIssue[];
  fixes: LintFix[];
  product?: string | null;
};

export type BulletinMeta = Schemas['BulletinMetaModel'];
export type BulletinReportResult = Schemas['BulletinReportResultModel'] & {
  issues: LintIssue[];
  fixes: LintFix[];
};

export type ConvertBulletinResponse = {
  bulletin_meta: BulletinMeta;
  results: BulletinReportResult[];
};

export type DecodeSegment = Schemas['DecodeSegmentModel'];
export type DecodeResidual = Schemas['DecodeResidualModel'];

export type DecodeTacResponse = {
  product: string;
  segments: DecodeSegment[];
  residuals: DecodeResidual[];
  summary: string;
};

export type LintIssueCatalogEntry = Schemas['LintIssueCatalogEntryModel'] & {
  tags: string[];
  family?: string | null;
  source_type?: string | null;
  status?: string | null;
  semantic_identifier?: string | null;
  last_verified?: string | null;
  replacement_url?: string | null;
  issue_type?: string | null;
  source_locator?: string | null;
  source_access?: string | null;
};

export type LintIssueCatalogResponse = {
  issues: LintIssueCatalogEntry[];
};

export type QualityMetricsSummary = Schemas['QualityMetricsSummaryModel'];
export type QualityMetricsFileRow = Schemas['QualityMetricsFileRowModel'];

export type QualityMetricsListResponse = {
  generated_at: string;
  iwxxm_pin: string;
  summaries: QualityMetricsSummary[];
  files: QualityMetricsFileRow[];
};

export type QualityMetricsDetailResponse = Schemas['QualityMetricsDetailResponse'] & {
  stem: string;
  product: string;
  tier: string;
  match_status: string;
  residuals: Record<string, unknown>[];
  lint_issues: Record<string, unknown>[];
  validate_issues: Record<string, unknown>[];
};

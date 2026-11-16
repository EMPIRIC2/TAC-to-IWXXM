/**
 * Bridge for OpenAPI typed FE clients (TC-EV052-009).
 *
 * Implementation aliases live in `@/models/openapi` (imports generated schemas).
 */
export type {
  ConversionIssue,
  ConversionResponse,
  ConversionResult,
  FailedSpan,
  GroupTraceEntry,
  LintIssueCatalogEntry,
  LintIssueCatalogResponse,
  LintTacResponse,
  QualityMetricsIssue,
  QualityMetricsResidual,
  QualityMetricsSummary,
  ValidateResponse,
} from '../models/openapi';

export type * from '../models/openapi';

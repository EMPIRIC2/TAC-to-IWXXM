/**
 * Catalog of operator-visible string exports for EV-048 guard scans (TC-EV048-003).
 *
 * Source comments / test files are out of scope — only these runtime strings.
 * [Corpus: product §F7] [Corpus: tests]
 */

import { EXAMPLES } from '@/fixtures/examples/examplesCatalog';
import { SHELL_NAV_LABELS } from '@/app/components/AppShellNav';
import {
  QUALITY_METRICS_DIFF_EMPTY_LABEL,
  QUALITY_METRICS_DIFF_EXPAND_ALL,
  QUALITY_METRICS_DIFF_COLLAPSE_ALL,
  QUALITY_METRICS_DIFF_HEADING,
  QUALITY_METRICS_EMPTY_DIAGNOSTICS,
  QUALITY_METRICS_LINT_HELP,
  QUALITY_METRICS_RESIDUALS_HELP,
  QUALITY_METRICS_VALIDATE_HELP,
  QUALITY_METRICS_XML_VIEW_HELP,
  QUALITY_METRICS_XML_VIEW_NORMALIZED,
  QUALITY_METRICS_XML_VIEW_RAW,
} from '@/app/components/QualityMetricsDetail';
import {
  QUALITY_METRICS_DEFERRED_LABEL,
  QUALITY_METRICS_DETAIL_LOAD_FAILED,
  QUALITY_METRICS_DETAIL_LOADING,
  QUALITY_METRICS_EMPTY_LIST,
  QUALITY_METRICS_PAGE_SUBTITLE,
  QUALITY_METRICS_PAGE_TITLE,
} from '@/utils/qualityMetricsCopy';
import {
  IWXXM_PRODUCT_CONVERT_ARIA,
  IWXXM_PRODUCT_CONVERT_LABEL,
  IWXXM_PRODUCT_HELP,
} from '@/utils/iwxxmProductCopy';
import {
  BULLETIN_ID_FIELD_ERROR,
  ISSUING_CENTER_FIELD_ERROR,
} from '@/utils/bulletinFieldsCopy';
import {
  SOFT_PREVIEW_HELP,
  SOFT_PREVIEW_LABEL,
} from '@/app/components/SoftPreviewControl';
import { GUEST_LOSS_OF_PROGRESS_MESSAGE } from '@/utils/guestLossNotice';
import { OPERATOR_HANDBOOK_URL, OPERATOR_ONE_PAGER_URL } from '@/utils/operatorHelp';
import { STORAGE_INVENTORY } from '@/utils/privacyPreferences';
import {
  QUALITY_METRICS_SCHEMA_IMPORT_RESOLVED,
  QUALITY_METRICS_SCHEMA_IMPORT_WARNING,
  QUALITY_METRICS_SCHEMATRON_EVALUATED,
  QUALITY_METRICS_SCHEMATRON_SKIPPED,
} from '@/utils/validateDispositionChips';

export type OperatorVisibleCopyEntry = {
  id: string;
  text: string;
};

/**
 * Collect agreed FE string catalogs for the internal-doc-ref guard.
 *
 * @returns Flat list of `{ id, text }` entries
 */
export function collectOperatorVisibleCopy(): OperatorVisibleCopyEntry[] {
  const entries: OperatorVisibleCopyEntry[] = [
    { id: 'soft-preview.label', text: SOFT_PREVIEW_LABEL },
    { id: 'soft-preview.help', text: SOFT_PREVIEW_HELP },
    { id: 'iwxxm-product.help', text: IWXXM_PRODUCT_HELP },
    { id: 'iwxxm-product.convert-label', text: IWXXM_PRODUCT_CONVERT_LABEL },
    { id: 'iwxxm-product.convert-aria', text: IWXXM_PRODUCT_CONVERT_ARIA },
    { id: 'bulletin-id.field-error', text: BULLETIN_ID_FIELD_ERROR },
    { id: 'issuing-center.field-error', text: ISSUING_CENTER_FIELD_ERROR },
    { id: 'guest.loss-of-progress', text: GUEST_LOSS_OF_PROGRESS_MESSAGE },
    { id: 'help.one-pager-url', text: OPERATOR_ONE_PAGER_URL },
    { id: 'help.handbook-url', text: OPERATOR_HANDBOOK_URL },
    { id: 'shell.nav.convert', text: SHELL_NAV_LABELS.converter },
    { id: 'shell.nav.history', text: SHELL_NAV_LABELS.history },
    { id: 'shell.nav.quality', text: SHELL_NAV_LABELS.quality },
    { id: 'quality-metrics.title', text: QUALITY_METRICS_PAGE_TITLE },
    { id: 'quality-metrics.subtitle', text: QUALITY_METRICS_PAGE_SUBTITLE },
    { id: 'quality-metrics.deferred-label', text: QUALITY_METRICS_DEFERRED_LABEL },
    { id: 'quality-metrics.empty-list', text: QUALITY_METRICS_EMPTY_LIST },
    {
      id: 'quality-metrics.detail-load-failed',
      text: QUALITY_METRICS_DETAIL_LOAD_FAILED,
    },
    {
      id: 'quality-metrics.detail-loading',
      text: QUALITY_METRICS_DETAIL_LOADING,
    },
    { id: 'quality-metrics.diff-empty', text: QUALITY_METRICS_DIFF_EMPTY_LABEL },
    { id: 'quality-metrics.diff-heading', text: QUALITY_METRICS_DIFF_HEADING },
    {
      id: 'quality-metrics.diff-expand-all',
      text: QUALITY_METRICS_DIFF_EXPAND_ALL,
    },
    {
      id: 'quality-metrics.diff-collapse-all',
      text: QUALITY_METRICS_DIFF_COLLAPSE_ALL,
    },
    {
      id: 'quality-metrics.empty-diagnostics',
      text: QUALITY_METRICS_EMPTY_DIAGNOSTICS,
    },
    { id: 'quality-metrics.residuals-help', text: QUALITY_METRICS_RESIDUALS_HELP },
    { id: 'quality-metrics.lint-help', text: QUALITY_METRICS_LINT_HELP },
    { id: 'quality-metrics.validate-help', text: QUALITY_METRICS_VALIDATE_HELP },
    {
      id: 'quality-metrics.xml-view-normalized',
      text: QUALITY_METRICS_XML_VIEW_NORMALIZED,
    },
    { id: 'quality-metrics.xml-view-raw', text: QUALITY_METRICS_XML_VIEW_RAW },
    { id: 'quality-metrics.xml-view-help', text: QUALITY_METRICS_XML_VIEW_HELP },
    {
      id: 'quality-metrics.schematron-evaluated',
      text: QUALITY_METRICS_SCHEMATRON_EVALUATED,
    },
    {
      id: 'quality-metrics.schematron-skipped',
      text: QUALITY_METRICS_SCHEMATRON_SKIPPED,
    },
    {
      id: 'quality-metrics.schema-import-resolved',
      text: QUALITY_METRICS_SCHEMA_IMPORT_RESOLVED,
    },
    {
      id: 'quality-metrics.schema-import-warning',
      text: QUALITY_METRICS_SCHEMA_IMPORT_WARNING,
    },
  ];

  for (const item of STORAGE_INVENTORY) {
    entries.push({
      id: `privacy.inventory.${item.kind}`,
      text: item.purpose,
    });
  }

  for (const example of EXAMPLES) {
    entries.push({
      id: `examples.${example.id}.label`,
      text: example.label,
    });
  }

  return entries;
}

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
  QUALITY_METRICS_EMPTY_DIAGNOSTICS,
  QUALITY_METRICS_XML_VIEW_HELP,
  QUALITY_METRICS_XML_VIEW_NORMALIZED,
  QUALITY_METRICS_XML_VIEW_RAW,
} from '@/app/components/QualityMetricsDetail';
import {
  QUALITY_METRICS_DEFERRED_LABEL,
  QUALITY_METRICS_PAGE_TITLE,
} from '@/app/components/QualityMetricsPage';
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
    { id: 'guest.loss-of-progress', text: GUEST_LOSS_OF_PROGRESS_MESSAGE },
    { id: 'help.one-pager-url', text: OPERATOR_ONE_PAGER_URL },
    { id: 'help.handbook-url', text: OPERATOR_HANDBOOK_URL },
    { id: 'shell.nav.convert', text: SHELL_NAV_LABELS.converter },
    { id: 'shell.nav.history', text: SHELL_NAV_LABELS.history },
    { id: 'shell.nav.quality', text: SHELL_NAV_LABELS.quality },
    { id: 'quality-metrics.title', text: QUALITY_METRICS_PAGE_TITLE },
    { id: 'quality-metrics.deferred-label', text: QUALITY_METRICS_DEFERRED_LABEL },
    { id: 'quality-metrics.diff-empty', text: QUALITY_METRICS_DIFF_EMPTY_LABEL },
    {
      id: 'quality-metrics.empty-diagnostics',
      text: QUALITY_METRICS_EMPTY_DIAGNOSTICS,
    },
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

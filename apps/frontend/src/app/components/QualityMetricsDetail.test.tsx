/**
 * TC-EV055-001 / AC6 — C14N panes, raw override, validate disposition chips.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  QUALITY_METRICS_DIFF_EMPTY_LABEL,
  QUALITY_METRICS_XML_VIEW_NORMALIZED,
  QUALITY_METRICS_XML_VIEW_RAW,
  QualityMetricsDetail,
} from './QualityMetricsDetail';
import { qualityMetricsDisplayXml } from '@/utils/qualityMetricsDisplayXml';
import {
  QUALITY_METRICS_SCHEMA_IMPORT_RESOLVED,
  QUALITY_METRICS_SCHEMA_IMPORT_WARNING,
  QUALITY_METRICS_SCHEMATRON_EVALUATED,
  QUALITY_METRICS_SCHEMATRON_SKIPPED,
  validateDispositionChips,
} from '@/utils/validateDispositionChips';
import type { QualityMetricsDetailResponse } from '@/utils/openapiTypes';

const FORMATTING_ONLY: QualityMetricsDetailResponse = {
  stem: 'metar-format-only',
  product: 'metar',
  tier: 'wmoPass',
  deferred: false,
  deferral_reason: null,
  tac: 'METAR YUDO 221630Z=',
  official_xml: `<?xml version="1.0"?>
<root xmlns="urn:x">
  <v>1</v>
</root>
`,
  converted_xml: '<?xml version="1.0"?><root xmlns="urn:x"><v>1</v></root>',
  match_status: 'equal',
  residuals: [],
  lint_issues: [],
  validate_issues: [],
};

const SEMANTIC_DIFF: QualityMetricsDetailResponse = {
  ...FORMATTING_ONLY,
  stem: 'metar-semantic',
  match_status: 'unequal',
  official_xml: '<root xmlns="urn:x"><v>1</v></root>',
  converted_xml: '<root xmlns="urn:x"><v>2</v></root>',
};

describe('validateDispositionChips (TC-EV055 AC6)', () => {
  it('treats empty validate issues as Schematron evaluated and schema import resolved', () => {
    const chips = validateDispositionChips([]);
    expect(chips).toEqual([
      {
        id: 'schematron',
        label: QUALITY_METRICS_SCHEMATRON_EVALUATED,
        ok: true,
      },
      {
        id: 'schema-import',
        label: QUALITY_METRICS_SCHEMA_IMPORT_RESOLVED,
        ok: true,
      },
    ]);
  });

  it('does not treat soft-skip codes as success', () => {
    const chips = validateDispositionChips([
      { code: 'SCHEMATRON_SKIPPED', message: 'xslt2 unsupported' },
      { code: 'SCHEMA_IMPORT_WARNING', message: 'import unresolved' },
    ]);
    expect(chips.find((c) => c.id === 'schematron')).toMatchObject({
      label: QUALITY_METRICS_SCHEMATRON_SKIPPED,
      ok: false,
    });
    expect(chips.find((c) => c.id === 'schema-import')).toMatchObject({
      label: QUALITY_METRICS_SCHEMA_IMPORT_WARNING,
      ok: false,
    });
  });
});

describe('QualityMetricsDetail C14N panes (TC-EV055-001)', () => {
  it('defaults to normalized panes and empty diff for formatting-only peers', () => {
    render(<QualityMetricsDetail detail={FORMATTING_ONLY} />);

    const expected = qualityMetricsDisplayXml(FORMATTING_ONLY.official_xml);
    expect(screen.getByTestId('quality-metrics-xml-view-mode')).toHaveTextContent(
      QUALITY_METRICS_XML_VIEW_NORMALIZED,
    );
    const officialPre = screen
      .getByTestId('quality-metrics-pane-official-xml')
      .querySelector('pre');
    const convertedPre = screen
      .getByTestId('quality-metrics-pane-converted-xml')
      .querySelector('pre');
    expect(officialPre?.textContent).toBe(expected);
    expect(convertedPre?.textContent).toBe(expected);
    expect(expected.includes('\n')).toBe(true);
    expect(screen.getByTestId('quality-metrics-diff-empty')).toHaveTextContent(
      QUALITY_METRICS_DIFF_EMPTY_LABEL,
    );
    expect(
      screen.getByTestId('quality-metrics-validate-chip-schematron'),
    ).toHaveTextContent(QUALITY_METRICS_SCHEMATRON_EVALUATED);
    expect(
      screen.getByTestId('quality-metrics-validate-chip-schema-import'),
    ).toHaveTextContent(QUALITY_METRICS_SCHEMA_IMPORT_RESOLVED);
  });

  it('toggle shows raw XML while unified diff stays on normalized peers', async () => {
    const user = userEvent.setup();
    render(<QualityMetricsDetail detail={FORMATTING_ONLY} />);

    await user.click(screen.getByTestId('quality-metrics-xml-view-raw'));

    expect(screen.getByTestId('quality-metrics-xml-view-mode')).toHaveTextContent(
      QUALITY_METRICS_XML_VIEW_RAW,
    );
    expect(
      screen.getByTestId('quality-metrics-pane-official-xml').textContent,
    ).toContain('<v>1</v>');
    // Raw official keeps pretty indentation markers that C14N strips from default view
    expect(screen.getByTestId('quality-metrics-pane-official-xml').textContent).toMatch(
      /\n\s+<v>/,
    );
    expect(screen.getByTestId('quality-metrics-diff-empty')).toBeInTheDocument();
  });

  it('keeps semantic differences visible in the unified diff', () => {
    render(<QualityMetricsDetail detail={SEMANTIC_DIFF} />);

    expect(screen.getByTestId('quality-metrics-diff-body')).toHaveTextContent(
      '<v>1</v>',
    );
    expect(screen.getByTestId('quality-metrics-diff-body')).toHaveTextContent(
      '<v>2</v>',
    );
  });

  it('qualityMetricsDisplayXml falls back to raw on malformed input', () => {
    expect(qualityMetricsDisplayXml('<not-closed>')).toBe('<not-closed>');
  });

  it('qualityMetricsDisplayXml returns empty for blank input', () => {
    expect(qualityMetricsDisplayXml('')).toBe('');
    expect(qualityMetricsDisplayXml('   ')).toBe('');
    expect(qualityMetricsDisplayXml(undefined as unknown as string)).toBe('');
  });

  it('formats validate diagnostics without a message via JSON', () => {
    const detail: QualityMetricsDetailResponse = {
      ...FORMATTING_ONLY,
      validate_issues: [{ code: 'X', other: true }],
    };
    render(<QualityMetricsDetail detail={detail} />);
    expect(screen.getByTestId('quality-metrics-pane-validate')).toHaveTextContent('X');
  });
});

/**
 * TC-EV055-001 / AC6 — C14N panes, raw override, validate disposition chips.
 */

import { describe, it, expect, vi } from 'vitest';
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

  it('formats diagnostics from detail when message is absent', () => {
    const detail: QualityMetricsDetailResponse = {
      ...FORMATTING_ONLY,
      residuals: [{ detail: 'leftover token' }],
      lint_issues: [{ code: 'LINT1', message: 'bad group' }],
    };
    render(<QualityMetricsDetail detail={detail} />);
    expect(screen.getByTestId('quality-metrics-pane-residuals')).toHaveTextContent(
      'leftover token',
    );
    expect(screen.getByTestId('quality-metrics-pane-lint')).toHaveTextContent(
      'LINT1: bad group',
    );
  });

  it('collapses distant equal context and expands on click', async () => {
    const user = userEvent.setup();
    const makeXml = (mid: string) => {
      const rows = Array.from({ length: 40 }, (_, i) =>
        i === 20 ? `  <v>${mid}</v>` : `  <n${i}/>`,
      );
      return `<root xmlns="urn:x">\n${rows.join('\n')}\n</root>`;
    };
    const detail: QualityMetricsDetailResponse = {
      ...FORMATTING_ONLY,
      stem: 'metar-long-diff',
      match_status: 'unequal',
      official_xml: makeXml('1'),
      converted_xml: makeXml('2'),
    };
    render(<QualityMetricsDetail detail={detail} />);

    expect(screen.getByTestId('quality-metrics-diff-body')).toBeInTheDocument();
    const expandHunks = screen.getAllByTestId('quality-metrics-diff-expand-hunk');
    expect(expandHunks.length).toBeGreaterThan(0);
    expect(screen.getByTestId('quality-metrics-diff-expand-all')).toHaveTextContent(
      /Show all unchanged lines/i,
    );

    await user.click(expandHunks[0]!);
    // Expanding one hunk may leave other collapse controls.
    expect(screen.getByTestId('quality-metrics-diff-expand-all')).toBeInTheDocument();

    // Toggle the same hunk off (covers expandedCollapseKeys delete branch).
    const hunksAfterExpand = screen.getAllByTestId('quality-metrics-diff-expand-hunk');
    await user.click(hunksAfterExpand[0]!);

    await user.click(screen.getByTestId('quality-metrics-diff-expand-all'));
    expect(screen.getByTestId('quality-metrics-diff-expand-all')).toHaveTextContent(
      /Hide distant unchanged lines/i,
    );
    expect(screen.queryAllByTestId('quality-metrics-diff-expand-hunk')).toHaveLength(0);

    await user.click(screen.getByTestId('quality-metrics-diff-expand-all'));
    expect(
      screen.getAllByTestId('quality-metrics-diff-expand-hunk').length,
    ).toBeGreaterThan(0);
  });

  it('shows plain-language match status for unequal and deferred', () => {
    const unequal: QualityMetricsDetailResponse = {
      ...SEMANTIC_DIFF,
      deferred: true,
      match_status: 'unequal',
    };
    const { rerender } = render(<QualityMetricsDetail detail={unequal} />);
    expect(screen.getByTestId('quality-metrics-match-status')).toHaveTextContent(
      'Differs from official',
    );
    expect(screen.getByText(/Deferred — not scored yet/i)).toBeInTheDocument();

    rerender(
      <QualityMetricsDetail
        detail={{
          ...FORMATTING_ONLY,
          match_status: 'deferred',
          deferred: true,
        }}
      />,
    );
    expect(screen.getByTestId('quality-metrics-match-status')).toHaveTextContent(
      'Deferred — not scored yet',
    );
  });

  it('shows empty pane placeholders when payloads are blank', () => {
    render(
      <QualityMetricsDetail
        detail={{
          ...FORMATTING_ONLY,
          tac: '',
          official_xml: '',
          converted_xml: '',
        }}
      />,
    );
    expect(screen.getByTestId('quality-metrics-pane-tac')).toHaveTextContent(
      /No TAC available/i,
    );
    expect(screen.getByTestId('quality-metrics-pane-official-xml')).toHaveTextContent(
      /No official XML available/i,
    );
  });

  it('treats missing official/converted XML as empty, including raw view', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(
      <QualityMetricsDetail
        detail={{
          ...FORMATTING_ONLY,
          official_xml: undefined as unknown as string,
          converted_xml: undefined as unknown as string,
        }}
        onClose={onClose}
        closeLabel="Back to list"
      />,
    );
    expect(screen.getByTestId('quality-metrics-pane-official-xml')).toHaveTextContent(
      /No official XML available/i,
    );
    expect(screen.getByTestId('quality-metrics-pane-converted-xml')).toHaveTextContent(
      /No converted XML available/i,
    );
    await user.click(screen.getByTestId('quality-metrics-xml-view-raw'));
    expect(screen.getByTestId('quality-metrics-xml-view-mode')).toHaveTextContent(
      QUALITY_METRICS_XML_VIEW_RAW,
    );
    await user.click(screen.getByTestId('quality-metrics-detail-close'));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('formats diagnostics for message-only, empty object, and circular payload', () => {
    const circular: Record<string, unknown> = { mark: 'circ' };
    circular.self = circular;
    const detail: QualityMetricsDetailResponse = {
      ...FORMATTING_ONLY,
      residuals: [{ message: 'only-msg' }],
      lint_issues: [{ other: true }],
      validate_issues: [circular],
    };
    render(<QualityMetricsDetail detail={detail} />);
    expect(screen.getByTestId('quality-metrics-pane-residuals')).toHaveTextContent(
      'only-msg',
    );
    expect(screen.getByTestId('quality-metrics-pane-lint')).toHaveTextContent('{');
    expect(screen.getByTestId('quality-metrics-pane-validate')).toHaveTextContent(
      '[object Object]',
    );
  });
});

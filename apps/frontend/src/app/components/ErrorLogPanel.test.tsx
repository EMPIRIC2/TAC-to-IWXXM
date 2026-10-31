import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ErrorLogPanel } from './ErrorLogPanel';
import type { LintIssueCatalogEntry } from '@/utils/api';

const CATALOG_ENTRY: LintIssueCatalogEntry = {
  code: 'MISSING_TERMINATOR',
  severity: 'info',
  message_template: "Reports in bulletins end with '='",
  product: null,
  tags: ['terminator'],
  family: 'lint',
};

describe('ErrorLogPanel', () => {
  it('renders nothing when log is empty', () => {
    const { container } = render(<ErrorLogPanel log={{ errors: [], issues: [] }} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('shows errors and issues with collapse toggle', async () => {
    const user = userEvent.setup();
    render(
      <ErrorLogPanel
        log={{
          errors: ['Invalid METAR syntax'],
          issues: [
            {
              source: 'parser',
              message: 'Unexpected token',
              severity: 'warning',
              hint: 'Check TAC format',
              code: 'E001',
            },
          ],
        }}
      />,
    );

    expect(screen.getByLabelText(/conversion error log/i)).toBeInTheDocument();
    expect(screen.getByText('Invalid METAR syntax')).toBeInTheDocument();
    expect(screen.getByRole('region', { name: 'Errors' })).toHaveTextContent(
      'Invalid METAR syntax',
    );
    expect(screen.getByRole('region', { name: 'Notes' })).toHaveTextContent(
      'Unexpected token',
    );
    expect(screen.getByText(/Unexpected token/)).toBeInTheDocument();
    expect(screen.getByText(/Check TAC format/)).toBeInTheDocument();
    expect(screen.getByText(/Code: E001/)).toBeInTheDocument();

    await user.click(
      screen.getByRole('button', { name: /conversion \/ validation log/i }),
    );
    expect(screen.queryByText('Invalid METAR syntax')).not.toBeInTheDocument();
  });

  it('defaults missing issue severity to error', () => {
    render(
      <ErrorLogPanel
        log={{
          errors: [],
          issues: [
            {
              source: 'parser',
              message: 'Missing severity field',
            },
          ],
        }}
      />,
    );

    expect(screen.getByRole('region', { name: 'Errors' })).toHaveTextContent(
      'Missing severity field',
    );
    expect(screen.queryByRole('region', { name: 'Notes' })).not.toBeInTheDocument();
  });

  it('scrubs planning ids and emphasizes error rows with destructive chrome', () => {
    render(
      <ErrorLogPanel
        log={{
          errors: ['Fatal convert EV-048 #702'],
          issues: [
            {
              source: 'parser',
              message: 'Schema failed - TC-F7-002 / EV-040',
              severity: 'error',
              hint: 'See ADR-022',
              code: 'XML_SCHEMA',
            },
            {
              source: 'parser',
              message: 'Cloud group unusual EV-011',
              severity: 'warning',
            },
          ],
        }}
      />,
    );

    expect(screen.getByText('Fatal convert')).toBeInTheDocument();
    expect(screen.queryByText(/EV-048/)).not.toBeInTheDocument();
    expect(screen.queryByText(/#702/)).not.toBeInTheDocument();

    const errorOpen = screen.getByTestId('issue-detail-open-0');
    expect(errorOpen).toHaveTextContent('Schema failed');
    expect(errorOpen).not.toHaveTextContent('TC-F7-002');
    expect(errorOpen).not.toHaveTextContent('EV-040');
    expect(errorOpen.querySelector('p')?.className).toMatch(/text-destructive/);

    const errorCard = errorOpen.closest('li');
    expect(errorCard).toHaveAttribute('data-error-emphasis', 'true');
    expect(errorCard?.className).toMatch(/bg-destructive\//);

    const noteOpen = screen.getByTestId('issue-detail-open-1');
    expect(noteOpen).toHaveTextContent('Cloud group unusual');
    expect(noteOpen).not.toHaveTextContent('EV-011');
    expect(noteOpen.closest('li')).toHaveAttribute('data-error-emphasis', 'false');
  });

  it('hides sub-critical issues when the operator log level is CRITICAL', () => {
    render(
      <ErrorLogPanel
        minLogLevel="CRITICAL"
        log={{
          errors: ['Fatal conversion error'],
          issues: [
            {
              source: 'parser',
              message: 'Minor warning',
              severity: 'warning',
            },
          ],
        }}
      />,
    );

    expect(screen.getByText(/Fatal conversion error/)).toBeInTheDocument();
    expect(screen.getByText(/1 · 1 hidden by log level/i)).toBeInTheDocument();
    expect(screen.queryByText(/Minor warning/)).not.toBeInTheDocument();
  });

  it('shows the log-level empty message when everything is filtered out', () => {
    render(
      <ErrorLogPanel
        minLogLevel="CRITICAL"
        log={{
          errors: [],
          issues: [
            {
              source: 'parser',
              message: 'Info only',
              severity: 'info',
            },
          ],
        }}
      />,
    );

    expect(screen.getByText(/0 · 1 hidden by log level/i)).toBeInTheDocument();
    expect(screen.getByText(/no messages at CRITICAL or above/i)).toBeInTheDocument();
  });

  it('uses neutral chrome for info-only issues (TC-EV-beta-004)', () => {
    render(
      <ErrorLogPanel
        log={{
          errors: [],
          issues: [
            {
              source: 'manual_input',
              message: 'Informational note',
              severity: 'info',
              code: 'CAVOK_PRESENT',
            },
          ],
        }}
      />,
    );
    expect(screen.getByTestId('conversion-error-log')).toHaveAttribute(
      'data-tone',
      'neutral',
    );
  });

  it('hides DEPRECATED_PROFILE_ALIAS from operators (TC-EV-beta-005)', () => {
    const { container } = render(
      <ErrorLogPanel
        log={{
          errors: [],
          issues: [
            {
              source: 'manual_input',
              message: "profile alias 'annex3' is deprecated",
              severity: 'info',
              code: 'DEPRECATED_PROFILE_ALIAS',
            },
          ],
        }}
      />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it('shows soft OUTPUT_VALIDATION_WARNING and flattened details (TC-F7-044)', () => {
    render(
      <ErrorLogPanel
        log={{
          errors: [],
          issues: [
            {
              source: 'manual_input',
              message: 'manual_input: IWXXM validation issues found - 1 issues',
              severity: 'warning',
              hint: 'Output converted, but IWXXM validation reported issues.',
              code: 'OUTPUT_VALIDATION_WARNING',
            },
            {
              source: 'manual_input',
              message: 'Broken GML href',
              severity: 'error',
              hint: 'Fix the xlink:href target.',
              code: 'GML_HREF_MISSING',
              layer: 'gml_references',
            },
          ],
        }}
      />,
    );
    expect(screen.getByText(/Code: OUTPUT_VALIDATION_WARNING/)).toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: /open output_validation_warning/i }),
    ).not.toBeInTheDocument();
    expect(screen.getByText(/Broken GML href/)).toBeInTheDocument();
    expect(screen.getByText(/Code: GML_HREF_MISSING/)).toBeInTheDocument();
  });

  it('opens the rules catalog for a coded issue and keeps an unknown code as text', async () => {
    const user = userEvent.setup();
    const onOpenCatalog = vi.fn();
    render(
      <ErrorLogPanel
        catalogByCode={new Map([['MISSING_TERMINATOR', CATALOG_ENTRY]])}
        onOpenCatalog={onOpenCatalog}
        log={{
          errors: [],
          issues: [
            {
              source: 'lint',
              message: 'Add the end marker',
              severity: 'warning',
              code: 'MISSING_TERMINATOR',
            },
            {
              source: 'parser',
              message: 'Unexpected token',
              severity: 'warning',
              code: 'E001',
            },
          ],
        }}
      />,
    );

    const jump = screen.getByTestId('log-issue-catalog-MISSING_TERMINATOR');
    expect(jump).toHaveAttribute(
      'aria-label',
      'Open MISSING_TERMINATOR in the rules catalog',
    );
    jump.focus();
    await user.keyboard('{Enter}');
    expect(onOpenCatalog).toHaveBeenCalledWith('lint', 'MISSING_TERMINATOR');
    await user.click(jump);
    expect(onOpenCatalog).toHaveBeenCalledTimes(2);

    const unknown = screen.getByText(/Code: E001/);
    expect(unknown.tagName).toBe('P');
    expect(screen.queryByTestId('log-issue-catalog-E001')).not.toBeInTheDocument();
  });

  it('keeps a catalog code as text when the catalog cannot be opened', () => {
    render(
      <ErrorLogPanel
        catalogByCode={new Map([['MISSING_TERMINATOR', CATALOG_ENTRY]])}
        log={{
          errors: [],
          issues: [
            {
              source: 'lint',
              message: 'Add the end marker',
              severity: 'warning',
              code: 'MISSING_TERMINATOR',
            },
          ],
        }}
      />,
    );
    expect(screen.getByText(/Code: MISSING_TERMINATOR/).tagName).toBe('P');
  });

  it('enriches sparse RVR_PRESENT and NSW_PRESENT notes with reason/consequence (UX-2026-10-30)', () => {
    render(
      <ErrorLogPanel
        catalogByCode={
          new Map([
            [
              'RVR_PRESENT',
              {
                code: 'RVR_PRESENT',
                severity: 'info',
                message_template:
                  '{product} includes one or more runway visual range (RVR) groups. ' +
                  'Informational: noted for operator awareness; does not by itself block conversion. ' +
                  'Source: ICAO Annex 3. Full normative text may require purchase.',
                product: null,
                tags: ['rvr'],
                family: 'lint',
              },
            ],
            [
              'NSW_PRESENT',
              {
                code: 'NSW_PRESENT',
                severity: 'info',
                message_template:
                  '{product} includes NSW (nil significant weather). ' +
                  'Informational: noted for operator awareness; does not by itself block conversion. ' +
                  'Source: ICAO Annex 3. Full normative text may require purchase.',
                product: null,
                tags: ['weather'],
                family: 'lint',
              },
            ],
          ])
        }
        log={{
          errors: [],
          issues: [
            {
              source: 'lint',
              message: "METAR RVR group 'R12/1000U' present",
              severity: 'info',
              code: 'RVR_PRESENT',
            },
            {
              source: 'lint',
              message: 'METAR NSW present',
              severity: 'info',
              code: 'NSW_PRESENT',
            },
            {
              source: 'validation',
              message: 'Station YUDO is not in the aerodrome registry',
              severity: 'warning',
              hint: "Designator 'YUDO' was not found in the local airport catalog; conversion continues, but coordinates and airport name may be incomplete",
              code: 'UNKNOWN_ICAO',
            },
          ],
        }}
      />,
    );

    expect(screen.getByText(/runway visual range \(RVR\)/i)).toBeInTheDocument();
    expect(screen.getByText(/NSW \(nil significant weather\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Designator 'YUDO'/)).toBeInTheDocument();
    expect(screen.queryByText(/Source:/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/EV-|ADR-|UJ-/)).not.toBeInTheDocument();
  });

  it('uses plain-language RVR/NSW glosses when catalog is not loaded', () => {
    render(
      <ErrorLogPanel
        log={{
          errors: [],
          issues: [
            {
              source: 'lint',
              message: "METAR RVR group 'R12/1000U' present",
              severity: 'info',
              code: 'RVR_PRESENT',
            },
            {
              source: 'lint',
              message: 'METAR NSW present',
              severity: 'info',
              code: 'NSW_PRESENT',
            },
          ],
        }}
      />,
    );
    expect(screen.getByText(/Runway Visual Range/i)).toBeInTheDocument();
    expect(screen.getByText(/No Significant Weather/i)).toBeInTheDocument();
  });

  it('opens a fuller description for a lint issue and closes it', async () => {
    const user = userEvent.setup();
    render(
      <ErrorLogPanel
        catalogByCode={
          new Map([
            [
              'MISSING_TERMINATOR',
              {
                ...CATALOG_ENTRY,
                source_attribution: 'WMO code list',
                product: 'METAR',
                tags: ['terminator'],
              },
            ],
          ])
        }
        log={{
          errors: [],
          issues: [
            {
              source: 'lint',
              message: 'Add the end marker',
              severity: 'warning',
              hint: 'End the report with =',
              code: 'MISSING_TERMINATOR',
              location: 'line 1',
              start: 0,
              end: 4,
            },
            {
              source: 'parser',
              message: 'No code on this row',
              severity: 'error',
            },
          ],
        }}
      />,
    );
    const open = screen.getByTestId('issue-detail-open-0');
    open.focus();
    await user.keyboard('{Enter}');
    expect(screen.getByTestId('issue-detail-dialog')).toHaveTextContent(
      "Reports in bulletins end with '='",
    );
    expect(screen.getByTestId('issue-detail-dialog')).toHaveTextContent(
      'WMO code list',
    );
    expect(screen.getByTestId('issue-detail-dialog')).toHaveTextContent(
      'End the report with =',
    );
    await user.click(screen.getByTestId('issue-detail-close'));
    expect(screen.queryByTestId('issue-detail-dialog')).not.toBeInTheDocument();
    await user.click(screen.getByTestId('issue-detail-open-1'));
    expect(screen.getByTestId('issue-detail-dialog')).toHaveTextContent(
      'No code on this row',
    );
  });
});

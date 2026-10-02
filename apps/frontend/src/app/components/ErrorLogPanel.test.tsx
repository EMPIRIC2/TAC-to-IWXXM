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

    expect(
      screen.getByText(/\[error\] parser: Missing severity field/),
    ).toBeInTheDocument();
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

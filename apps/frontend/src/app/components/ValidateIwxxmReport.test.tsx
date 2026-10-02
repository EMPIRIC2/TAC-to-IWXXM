/**
 * Branch coverage for validate-only IWXXM report (F7.s / #838).
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ValidateIwxxmReport } from './ValidateIwxxmReport';
import type { LintIssueCatalogEntry } from '@/utils/api';
import type { ValidateResponse } from '/utils/openapiTypes';

function report(partial: {
  is_valid: boolean;
  version?: string;
  layers_passed?: string[];
  layers_failed?: string[];
  package_issues?: unknown[];
  issues?: unknown[];
}): ValidateResponse {
  return {
    version: '2025-2',
    ...partial,
  } as ValidateResponse;
}

describe('ValidateIwxxmReport', () => {
  it('renders Valid with passed layers and no issues copy', () => {
    render(
      <ValidateIwxxmReport
        report={report({
          is_valid: true,
          layers_passed: ['XML_SCHEMA'],
          layers_failed: [],
          package_issues: [],
        })}
      />,
    );
    expect(screen.getByTestId('validate-iwxxm-status')).toHaveTextContent(/Valid/);
    expect(screen.getByTestId('validate-iwxxm-schema')).toHaveTextContent(
      'XML schema: passed',
    );
    expect(screen.getByTestId('validate-iwxxm-schematron')).toHaveTextContent(
      'Schematron: not run',
    );
    expect(screen.getByText(/Passed: XML_SCHEMA/)).toBeInTheDocument();
    expect(screen.getByText(/No package issues reported/)).toBeInTheDocument();
  });

  it('shows no-issues copy when both package_issues and issues are omitted', () => {
    render(<ValidateIwxxmReport report={report({ is_valid: true })} />);
    expect(screen.getByText(/No package issues reported/)).toBeInTheDocument();
  });

  it('defaults missing layer arrays and falls back to issues when package_issues omitted', () => {
    render(
      <ValidateIwxxmReport
        report={report({
          is_valid: false,
          issues: ['bare string issue'],
        })}
      />,
    );
    expect(screen.getByTestId('validate-iwxxm-status')).toHaveTextContent(/Invalid/);
    expect(screen.getByTestId('validate-iwxxm-issues')).toHaveTextContent(
      'bare string issue',
    );
  });

  it('renders failed layers and object issues with code, missing code, and missing message', () => {
    render(
      <ValidateIwxxmReport
        report={report({
          is_valid: false,
          layers_failed: ['SCHEMATRON'],
          package_issues: [
            { message: 'schema boom', code: 'XSD' },
            { message: 'no code' },
            { code: 'EMPTY_MSG' },
            { message: undefined, code: undefined },
            null as unknown as { message: string },
          ],
        })}
      />,
    );
    expect(screen.getByTestId('validate-iwxxm-schema')).toHaveTextContent(
      'XML schema: not run',
    );
    expect(screen.getByTestId('validate-iwxxm-schematron')).toHaveTextContent(
      'Schematron: failed',
    );
    expect(screen.getByTestId('validate-iwxxm-failed-layers')).toHaveTextContent(
      /Failed: SCHEMATRON/,
    );
    const list = screen.getByTestId('validate-iwxxm-issues');
    expect(list).toHaveTextContent('XSD:');
    expect(list).toHaveTextContent('schema boom');
    expect(list).toHaveTextContent('no code');
    expect(list).toHaveTextContent('EMPTY_MSG:');
    expect(list).toHaveTextContent('Issue');
  });

  it('opens a fuller description for a validation issue and closes it', async () => {
    const user = userEvent.setup();
    const catalog: LintIssueCatalogEntry = {
      code: 'XSD',
      severity: 'error',
      message_template: 'XML schema check failed',
      product: null,
      tags: [],
      source_attribution: 'IWXXM schema',
    };
    render(
      <ValidateIwxxmReport
        catalogByCode={new Map([['XSD', catalog]])}
        report={report({
          is_valid: false,
          package_issues: [
            {
              message: 'schema boom',
              code: 'XSD',
              hint: 'Check the element',
              location: 'line 2',
              start: 1,
              end: 4,
              severity: 'error',
            },
            'bare string issue',
          ],
        })}
      />,
    );
    await user.click(screen.getByTestId('issue-detail-open-0'));
    expect(screen.getByTestId('issue-detail-dialog')).toHaveTextContent(
      'XML schema check failed',
    );
    expect(screen.getByTestId('issue-detail-dialog')).toHaveTextContent('IWXXM schema');
    await user.click(screen.getByTestId('issue-detail-close'));
    expect(screen.queryByTestId('issue-detail-dialog')).not.toBeInTheDocument();
    await user.click(screen.getByTestId('issue-detail-open-1'));
    expect(screen.getByTestId('issue-detail-dialog')).toHaveTextContent(
      'bare string issue',
    );
  });
});

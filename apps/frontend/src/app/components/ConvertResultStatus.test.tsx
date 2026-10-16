import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';

import { ConvertResultStatus } from './ConvertResultStatus';
import { assessResultCard } from '/utils/resultCard';

describe('ConvertResultStatus', () => {
  it('leads with Valid and hides publish and message sections', () => {
    render(
      <ConvertResultStatus
        assessment={assessResultCard({ xml: '<iwxxm>ok</iwxxm>', ok: true })}
      />,
    );
    expect(screen.getByTestId('result-status-label')).toHaveTextContent('Valid');
    expect(screen.queryByTestId('result-do-not-publish')).not.toBeInTheDocument();
    expect(screen.queryByRole('region', { name: 'Errors' })).not.toBeInTheDocument();
    expect(screen.queryByRole('region', { name: 'Notes' })).not.toBeInTheDocument();
    expect(screen.queryByText('Passed')).not.toBeInTheDocument();
  });

  it('separates notes from errors and keeps the code under the message', () => {
    render(
      <ConvertResultStatus
        assessment={assessResultCard({
          xml: '<iwxxm>ok</iwxxm>',
          issues: [
            {
              severity: 'info',
              message: 'Remark stays in the decode',
              code: 'RMK_NOTE',
            },
            { severity: 'warning', message: 'Cloud group is unusual' },
          ],
        })}
      />,
    );
    expect(screen.getByTestId('result-status-label')).toHaveTextContent(
      'Valid with notes',
    );
    expect(screen.queryByTestId('result-do-not-publish')).not.toBeInTheDocument();
    const notes = screen.getByRole('region', { name: 'Notes' });
    expect(notes).toHaveTextContent('Remark stays in the decode');
    expect(notes).toHaveTextContent('Code: RMK_NOTE');
    expect(notes).toHaveTextContent('Cloud group is unusual');
    expect(screen.queryByRole('region', { name: 'Errors' })).not.toBeInTheDocument();
  });

  it('says do not publish on an invalid result and lists errors apart from notes', () => {
    render(
      <ConvertResultStatus
        assessment={assessResultCard({
          xml: '<iwxxm',
          ok: false,
          errors: ['XML is not valid'],
          issues: [
            { severity: 'error', message: 'Schema check failed', code: 'XML_SCHEMA' },
            { severity: 'info', message: 'A note stays with notes' },
          ],
        })}
      />,
    );
    const status = screen.getByTestId('result-card-status');
    expect(screen.getByTestId('result-status-label')).toHaveTextContent(
      'Needs attention',
    );
    expect(screen.getByTestId('result-do-not-publish')).toHaveTextContent(
      'Do not publish',
    );
    expect(status.textContent?.indexOf('Needs attention')).toBeLessThan(
      status.textContent?.indexOf('Schema check failed') ?? -1,
    );
    const errors = screen.getByRole('region', { name: 'Errors' });
    const notes = screen.getByRole('region', { name: 'Notes' });
    expect(errors).toHaveTextContent('XML is not valid');
    expect(errors).toHaveTextContent('Schema check failed');
    expect(errors).toHaveTextContent('Code: XML_SCHEMA');
    expect(notes).toHaveTextContent('A note stays with notes');
    expect(notes).not.toHaveTextContent('Schema check failed');
    expect(screen.queryByText('Passed')).not.toBeInTheDocument();
  });
});

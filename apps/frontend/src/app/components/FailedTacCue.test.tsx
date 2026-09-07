/**
 * T3.3 — Failed-TAC visual cue in editor/results (UJ-016 / #665).
 *
 * Expected red until T3.4 ships FailedTacCue + TacEditor failed chrome.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FailedTacCue, type FailedTacCueProps } from './FailedTacCue';
import { TacEditor } from './TacEditor';

describe('FailedTacCue', () => {
  it('renders a distinct Failed-TAC label (not a generic error toast)', () => {
    render(
      <FailedTacCue
        failedSpans={[
          {
            start: 0,
            end: 12,
            code: 'PARSE_ERROR',
            message: 'no METAR/SPECI report found in TAC',
          },
        ]}
      />,
    );

    const cue = screen.getByTestId('failed-tac-cue');
    expect(cue).toBeInTheDocument();
    expect(cue).toHaveTextContent(/Failed-TAC/i);
    expect(cue).toHaveAttribute('role', 'status');
    expect(screen.getByText(/PARSE_ERROR/i)).toBeInTheDocument();
  });

  it('is hidden when there are no failed spans', () => {
    const { container } = render(<FailedTacCue failedSpans={[]} />);
    expect(container.querySelector('[data-testid="failed-tac-cue"]')).toBeNull();
  });

  it('summarizes span count for multiple failures', () => {
    render(
      <FailedTacCue
        failedSpans={[
          { start: 0, end: 5, code: 'A', message: 'first' },
          { start: 10, end: 15, code: 'B', message: 'second' },
        ]}
      />,
    );
    expect(screen.getByTestId('failed-tac-cue')).toHaveTextContent(/2/);
  });

  it('omits optional code and message lines when absent', () => {
    render(<FailedTacCue failedSpans={[{ start: 0, end: 5 }]} />);
    const cue = screen.getByTestId('failed-tac-cue');
    expect(cue).toHaveTextContent(/Failed-TAC/i);
    expect(cue.querySelector('.font-mono')).toBeNull();
  });

  it('renders message-only spans without a code line', () => {
    render(
      <FailedTacCue failedSpans={[{ start: 0, end: 5, message: 'partial preview' }]} />,
    );
    expect(screen.getByText('partial preview')).toBeInTheDocument();
    expect(screen.queryByText(/PARSE_ERROR/i)).toBeNull();
  });

  it('renders code-only spans without a message line', () => {
    render(<FailedTacCue failedSpans={[{ start: 0, end: 5, code: 'WARN_ONLY' }]} />);
    expect(screen.getByText('WARN_ONLY')).toBeInTheDocument();
  });

  it('returns null when the first span slot is missing', () => {
    const sparseSpans = [] as FailedTacCueProps['failedSpans'];
    sparseSpans[1] = { start: 0, end: 5, message: 'later span only' };
    const { container } = render(<FailedTacCue failedSpans={sparseSpans} />);
    expect(container.querySelector('[data-testid="failed-tac-cue"]')).toBeNull();
  });
});

describe('TacEditor failed-TAC chrome', () => {
  it('marks the editor host when failedSpans are present', () => {
    render(
      <TacEditor
        value="METAR XXXX GARBAGE="
        onChange={() => {}}
        failedSpans={[
          { start: 6, end: 10, code: 'PARSE_ERROR', message: 'bad station' },
        ]}
      />,
    );
    const host = screen.getByTestId('tac-editor');
    expect(host).toHaveAttribute('data-failed-tac', 'true');
  });

  it('does not mark the editor when failedSpans are empty', () => {
    render(
      <TacEditor
        value="METAR KJFK 231751Z NIL="
        onChange={() => {}}
        failedSpans={[]}
      />,
    );
    expect(screen.getByTestId('tac-editor')).not.toHaveAttribute(
      'data-failed-tac',
      'true',
    );
  });
});

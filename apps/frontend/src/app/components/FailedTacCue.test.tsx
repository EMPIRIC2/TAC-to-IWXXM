/**
 * T3.3 — Failed-TAC visual cue in editor/results (UJ-016 / #665).
 *
 * Expected red until T3.4 ships FailedTacCue + TacEditor failed chrome.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FailedTacCue } from './FailedTacCue';
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

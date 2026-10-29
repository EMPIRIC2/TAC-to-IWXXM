/**
 * Empty Convert secondary affordances (UX-2026-10-29-convert-polish).
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import { CalmConvertEmptyAffordances } from './CalmConvertEmptyAffordances';

describe('CalmConvertEmptyAffordances', () => {
  it('renders example chips and other-task links under the shared shell', async () => {
    const user = userEvent.setup();
    const onExampleChip = vi.fn();
    const onOtherTask = vi.fn();
    const onChangeProfile = vi.fn();

    render(
      <CalmConvertEmptyAffordances
        exampleChips={[
          { id: 'metar', label: 'METAR' },
          { id: 'taf', label: 'TAF' },
        ]}
        onExampleChip={onExampleChip}
        onOtherTask={onOtherTask}
        profileLabel="WMO"
        onChangeProfile={onChangeProfile}
      />,
    );

    expect(screen.getByTestId('convert-empty-affordances')).toBeInTheDocument();
    expect(screen.getByTestId('convert-example-chips')).toBeInTheDocument();
    await user.click(screen.getByTestId('convert-example-chip-metar'));
    expect(onExampleChip).toHaveBeenCalledWith('metar');
    await user.click(screen.getByRole('button', { name: /Convert a full bulletin/i }));
    expect(onOtherTask).toHaveBeenCalledWith('ahl');
    await user.click(screen.getByTestId('convert-profile-change'));
    expect(onChangeProfile).toHaveBeenCalled();
  });

  it('UX-2026-10-29-convert-one-interface-examples: supports examples-only embed without other tasks', () => {
    render(
      <CalmConvertEmptyAffordances
        exampleChips={[{ id: 'metar', label: 'METAR' }]}
        onExampleChip={() => undefined}
      />,
    );
    expect(screen.getByTestId('convert-example-chips')).toBeInTheDocument();
    expect(screen.queryByText('Other tasks')).not.toBeInTheDocument();
  });

  it('renders nothing when there are no chips, other tasks, or profile', () => {
    const { container } = render(
      <CalmConvertEmptyAffordances exampleChips={[]} onExampleChip={() => undefined} />,
    );
    expect(container).toBeEmptyDOMElement();
  });
});

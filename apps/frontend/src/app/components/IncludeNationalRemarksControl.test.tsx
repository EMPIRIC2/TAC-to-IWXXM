import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import {
  INCLUDE_NATIONAL_REMARKS_HELP,
  INCLUDE_NATIONAL_REMARKS_LABEL,
  IncludeNationalRemarksControl,
} from './IncludeNationalRemarksControl';

describe('IncludeNationalRemarksControl', () => {
  it('renders label/help and reports checkbox changes', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<IncludeNationalRemarksControl checked={true} onChange={onChange} />);

    expect(screen.getByText(INCLUDE_NATIONAL_REMARKS_LABEL)).toBeInTheDocument();
    expect(screen.getByText(INCLUDE_NATIONAL_REMARKS_HELP)).toBeInTheDocument();

    const toggle = screen.getByTestId('include-national-remarks-toggle');
    expect(toggle).toBeChecked();
    await user.click(toggle);
    expect(onChange).toHaveBeenCalledWith(false);
  });

  it('honours disabled', () => {
    render(
      <IncludeNationalRemarksControl checked={false} onChange={vi.fn()} disabled />,
    );
    expect(screen.getByTestId('include-national-remarks-toggle')).toBeDisabled();
  });
});

/**
 * StrictControls smoke coverage (ADR-054).
 */
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { StrictControls } from './StrictControls';

describe('StrictControls', () => {
  it('toggles Strict and shows step checkboxes when on', async () => {
    const user = userEvent.setup();
    const onStrictChange = vi.fn();
    const onStrictLintChange = vi.fn();
    const onStrictConvertChange = vi.fn();
    const onStrictValidateChange = vi.fn();

    const { rerender } = render(
      <StrictControls
        strict={false}
        strictLint
        strictConvert
        strictValidate
        onStrictChange={onStrictChange}
        onStrictLintChange={onStrictLintChange}
        onStrictConvertChange={onStrictConvertChange}
        onStrictValidateChange={onStrictValidateChange}
      />,
    );

    expect(screen.queryByTestId('strict-step-toggles')).not.toBeInTheDocument();
    await user.click(screen.getByTestId('strict-validation-checkbox'));
    expect(onStrictChange).toHaveBeenCalledWith(true);

    rerender(
      <StrictControls
        strict
        strictLint
        strictConvert
        strictValidate
        onStrictChange={onStrictChange}
        onStrictLintChange={onStrictLintChange}
        onStrictConvertChange={onStrictConvertChange}
        onStrictValidateChange={onStrictValidateChange}
      />,
    );

    expect(screen.getByTestId('strict-step-toggles')).toBeInTheDocument();
    await user.click(screen.getByTestId('strict-lint-checkbox'));
    expect(onStrictLintChange).toHaveBeenCalledWith(false);
    await user.click(screen.getByTestId('strict-convert-checkbox'));
    expect(onStrictConvertChange).toHaveBeenCalledWith(false);
    await user.click(screen.getByTestId('strict-validate-checkbox'));
    expect(onStrictValidateChange).toHaveBeenCalledWith(false);
  });
});

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OTPInputContext } from 'input-otp';

import { InputOTPSeparator, InputOTPSlot } from './input-otp';

const baseContext = {
  isFocused: false,
  isHovering: false,
} as const;

describe('input-otp ui', () => {
  it('renders an empty slot when the context has no entry for the index', () => {
    render(
      <OTPInputContext.Provider value={{ ...baseContext, slots: [] }}>
        <InputOTPSlot index={0} data-testid="slot" />
      </OTPInputContext.Provider>,
    );

    expect(screen.getByTestId('slot')).toBeInTheDocument();
    expect(screen.getByTestId('slot')).toHaveTextContent('');
  });

  it('renders slot content without a fake caret', () => {
    render(
      <OTPInputContext.Provider
        value={{
          ...baseContext,
          slots: [
            {
              char: '3',
              hasFakeCaret: false,
              isActive: false,
              placeholderChar: ' ',
            },
          ],
        }}
      >
        <InputOTPSlot index={0} data-testid="slot" />
      </OTPInputContext.Provider>,
    );

    expect(screen.getByTestId('slot')).toHaveTextContent('3');
    expect(screen.getByTestId('slot').querySelector('.animate-caret-blink')).toBeNull();
  });

  it('renders the fake caret when the slot requests it', () => {
    render(
      <OTPInputContext.Provider
        value={{
          ...baseContext,
          slots: [
            {
              char: '7',
              hasFakeCaret: true,
              isActive: true,
              placeholderChar: ' ',
            },
          ],
        }}
      >
        <InputOTPSlot index={0} data-testid="slot" />
      </OTPInputContext.Provider>,
    );

    expect(screen.getByTestId('slot')).toHaveTextContent('7');
    expect(
      screen.getByTestId('slot').querySelector('.animate-caret-blink'),
    ).not.toBeNull();
  });

  it('renders the separator icon', () => {
    render(<InputOTPSeparator data-testid="separator" />);
    expect(screen.getByTestId('separator')).toHaveAttribute('role', 'separator');
  });
});

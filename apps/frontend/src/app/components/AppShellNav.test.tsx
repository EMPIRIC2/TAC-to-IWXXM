import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AppShellNav, SHELL_NAV_LABELS } from './AppShellNav';

describe('AppShellNav', () => {
  it('renders Dissemination ops and Conversion profiles tabs', async () => {
    const user = userEvent.setup();
    const onNavigate = vi.fn();
    render(<AppShellNav activeView="converter" onNavigate={onNavigate} />);

    expect(screen.getByTestId('shell-nav-dissemination-ops')).toHaveTextContent(
      SHELL_NAV_LABELS['dissemination-ops'],
    );
    expect(screen.getByTestId('shell-nav-profiles')).toHaveTextContent(
      SHELL_NAV_LABELS.profiles,
    );
    await user.click(screen.getByTestId('shell-nav-profiles'));
    expect(onNavigate).toHaveBeenCalledWith('profiles');
  });

  it('marks the active tab as selected', () => {
    render(<AppShellNav activeView="profiles" onNavigate={() => undefined} />);
    expect(screen.getByTestId('shell-nav-profiles')).toHaveAttribute(
      'aria-selected',
      'true',
    );
    expect(screen.getByTestId('shell-nav-converter')).toHaveAttribute(
      'aria-selected',
      'false',
    );
  });
});

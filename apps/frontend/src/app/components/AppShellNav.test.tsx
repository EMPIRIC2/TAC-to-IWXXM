import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AppShellNav, SHELL_NAV_LABELS } from './AppShellNav';

describe('AppShellNav', () => {
  it('renders Dissemination ops and Rule catalogs tabs without Profile builder', async () => {
    const user = userEvent.setup();
    const onNavigate = vi.fn();
    render(<AppShellNav activeView="converter" onNavigate={onNavigate} />);

    expect(screen.getByTestId('shell-nav-dissemination-ops')).toHaveTextContent(
      SHELL_NAV_LABELS['dissemination-ops'],
    );
    expect(
      screen
        .getByTestId('shell-nav-dissemination-ops')
        .querySelector('[data-testid="beta-badge"]'),
    ).toHaveTextContent('Beta');
    expect(screen.getByTestId('shell-nav-catalog')).toHaveTextContent(
      SHELL_NAV_LABELS.catalog,
    );
    expect(screen.queryByTestId('shell-nav-profiles')).not.toBeInTheDocument();
    await user.click(screen.getByTestId('shell-nav-catalog'));
    expect(onNavigate).toHaveBeenCalledWith('catalog');
  });

  it('marks the active tab as selected', () => {
    render(<AppShellNav activeView="catalog" onNavigate={() => undefined} />);
    expect(screen.getByTestId('shell-nav-catalog')).toHaveAttribute(
      'aria-selected',
      'true',
    );
    expect(screen.getByTestId('shell-nav-converter')).toHaveAttribute(
      'aria-selected',
      'false',
    );
  });
});

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AppShellNav, SHELL_NAV_LABELS } from './AppShellNav';

describe('AppShellNav', () => {
  it('renders Convert, Decode visuals, History, Rule catalogs, Code names, Glossary, and Station health without Dissemination ops', async () => {
    const user = userEvent.setup();
    const onNavigate = vi.fn();
    render(<AppShellNav activeView="converter" onNavigate={onNavigate} />);

    expect(screen.getByTestId('shell-nav-converter')).toHaveTextContent(
      SHELL_NAV_LABELS.converter,
    );
    expect(screen.getByTestId('shell-nav-visuals')).toHaveTextContent(
      SHELL_NAV_LABELS.visuals,
    );
    expect(screen.getByTestId('shell-nav-history')).toHaveTextContent(
      SHELL_NAV_LABELS.history,
    );
    expect(screen.getByTestId('shell-nav-catalog')).toHaveTextContent(
      SHELL_NAV_LABELS.catalog,
    );
    expect(screen.getByTestId('shell-nav-dictionary')).toHaveTextContent(
      SHELL_NAV_LABELS.dictionary,
    );
    expect(screen.getByTestId('shell-nav-glossary')).toHaveTextContent(
      SHELL_NAV_LABELS.glossary,
    );
    expect(screen.getByTestId('shell-nav-stations')).toHaveTextContent(
      SHELL_NAV_LABELS.stations,
    );
    expect(screen.queryByTestId('shell-nav-dissemination-ops')).not.toBeInTheDocument();
    expect(screen.queryByTestId('shell-nav-profiles')).not.toBeInTheDocument();
    await user.click(screen.getByTestId('shell-nav-visuals'));
    expect(onNavigate).toHaveBeenCalledWith('visuals');
    await user.click(screen.getByTestId('shell-nav-catalog'));
    expect(onNavigate).toHaveBeenCalledWith('catalog');
    await user.click(screen.getByTestId('shell-nav-dictionary'));
    expect(onNavigate).toHaveBeenCalledWith('dictionary');
    await user.click(screen.getByTestId('shell-nav-glossary'));
    expect(onNavigate).toHaveBeenCalledWith('glossary');
    await user.click(screen.getByTestId('shell-nav-stations'));
    expect(onNavigate).toHaveBeenCalledWith('stations');
  });

  it('follows a tighter Convert layout in this browser', () => {
    window.localStorage.setItem(
      'tac-to-iwxxm.live-convert.layout',
      JSON.stringify({
        density: 'detailed',
        wrapXml: true,
        paneWidths: [34, 27, 39],
        span: 'tight',
      }),
    );
    render(<AppShellNav activeView="converter" onNavigate={() => undefined} />);
    expect(screen.getByTestId('app-shell-nav').firstElementChild).toHaveClass(
      'max-w-6xl',
    );
    window.localStorage.clear();
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

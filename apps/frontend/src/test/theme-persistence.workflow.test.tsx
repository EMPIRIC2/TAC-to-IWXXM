import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeToggle } from '../app/components/ThemeToggle';

const setThemeMock = vi.hoisted(() => vi.fn());
const useThemeMock = vi.hoisted(() =>
  vi.fn(() => ({
    theme: 'light',
    setTheme: setThemeMock,
    themes: ['light', 'dark'],
    systemTheme: undefined,
    resolvedTheme: 'light',
  }))
);

vi.mock('next-themes', () => ({
  useTheme: useThemeMock,
}));

describe('UI Workflow: Theme Persistence', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useThemeMock.mockReturnValue({
      theme: 'light',
      setTheme: setThemeMock,
      themes: ['light', 'dark'],
      systemTheme: undefined,
      resolvedTheme: 'light',
    });
  });

  it('toggles from light to dark and requests theme persistence', async () => {
    const user = userEvent.setup();
    render(<ThemeToggle />);

    const toggle = screen.getByRole('switch', { name: /switch to dark mode/i });
    expect(toggle).toHaveAttribute('aria-checked', 'false');

    await user.click(toggle);
    expect(setThemeMock).toHaveBeenCalledWith('dark');
  });

  it('toggles from dark to light and exposes correct aria state', async () => {
    const user = userEvent.setup();
    useThemeMock.mockReturnValue({
      theme: 'dark',
      setTheme: setThemeMock,
      themes: ['light', 'dark'],
      systemTheme: undefined,
      resolvedTheme: 'dark',
    });

    render(<ThemeToggle />);

    const toggle = screen.getByRole('switch', { name: /switch to light mode/i });
    expect(toggle).toHaveAttribute('aria-checked', 'true');

    await user.click(toggle);
    expect(setThemeMock).toHaveBeenCalledWith('light');
  });

  it('maintains persisted dark state across remount', () => {
    useThemeMock.mockReturnValue({
      theme: 'dark',
      setTheme: setThemeMock,
      themes: ['light', 'dark'],
      systemTheme: undefined,
      resolvedTheme: 'dark',
    });

    const { unmount } = render(<ThemeToggle />);
    const darkToggle = screen.getByRole('switch', { name: /switch to light mode/i });
    expect(darkToggle).toHaveAttribute('aria-checked', 'true');

    unmount();

    render(<ThemeToggle />);
    const darkToggleAfterRemount = screen.getByRole('switch', { name: /switch to light mode/i });
    expect(darkToggleAfterRemount).toHaveAttribute('aria-checked', 'true');
  });
});

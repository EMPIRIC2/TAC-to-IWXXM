import { beforeEach, describe, expect, it, vi } from 'vitest';
import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { UserPreferencesDialog } from './UserPreferencesDialog';

const mockToast = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
}));

vi.mock('sonner', () => ({
  toast: mockToast,
}));

const defaultProps = {
  isOpen: true,
  onClose: vi.fn(),
  userEmail: 'prefs@example.com',
  onPreferencesSaved: vi.fn(),
};

describe('UserPreferencesDialog (EV-040 slim)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.clearAllMocks();
    localStorage.clear();
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
  });

  it('renders nothing when closed', () => {
    const { container } = render(
      <UserPreferencesDialog {...defaultProps} isOpen={false} />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it('loads defaults for first-time users', async () => {
    render(<UserPreferencesDialog {...defaultProps} />);

    expect(await screen.findByDisplayValue('prefs')).toBeInTheDocument();
    expect(screen.getByLabelText(/output file extension/i)).toHaveValue('.xml');
    expect(screen.queryByLabelText(/iwxxm schema version/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/bulletin id/i)).not.toBeInTheDocument();
  });

  it('merges display name and extension from localStorage', async () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({
        displayName: 'Ops Name',
        outputFileExtension: '.iwxxm',
        bulletinIdExample: 'ABCD12',
      }),
    );

    render(<UserPreferencesDialog {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByDisplayValue('Ops Name')).toBeInTheDocument();
      expect(screen.getByLabelText(/output file extension/i)).toHaveValue('.iwxxm');
    });
    expect(screen.queryByDisplayValue('ABCD12')).not.toBeInTheDocument();
  });

  it('falls back to the email prefix and default extension for incomplete storage', async () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({ displayName: 42, outputFileExtension: null }),
    );

    render(<UserPreferencesDialog {...defaultProps} />);

    expect(await screen.findByDisplayValue('prefs')).toBeInTheDocument();
    expect(screen.getByLabelText(/output file extension/i)).toHaveValue('.xml');
  });

  it('saves updated preferences and notifies parent', async () => {
    const onPreferencesSaved = vi.fn();
    const user = userEvent.setup();
    render(
      <UserPreferencesDialog
        {...defaultProps}
        onPreferencesSaved={onPreferencesSaved}
      />,
    );

    const displayName = await screen.findByLabelText(/display \/ output name/i);
    await user.clear(displayName);
    await user.type(displayName, 'Workflow User');
    await user.selectOptions(screen.getByLabelText(/output file extension/i), '.iwxxm');

    await user.click(screen.getByRole('button', { name: /save preferences/i }));

    const stored = JSON.parse(
      localStorage.getItem('metar_converter_preferences') || '{}',
    );
    expect(stored.displayName).toBe('Workflow User');
    expect(stored.outputFileExtension).toBe('.iwxxm');
    expect(mockToast.success).toHaveBeenCalledWith('Preferences saved successfully');
    expect(onPreferencesSaved).toHaveBeenCalledTimes(1);
    expect(screen.getByText(/preferences saved successfully/i)).toBeInTheDocument();
  });

  it('preserves legacy keys when saving slim fields', async () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({
        bulletinIdExample: 'KEEP12',
        displayName: 'Old',
        outputFileExtension: '.xml',
      }),
    );
    const user = userEvent.setup();
    render(<UserPreferencesDialog {...defaultProps} />);

    const displayName = await screen.findByLabelText(/display \/ output name/i);
    await user.clear(displayName);
    await user.type(displayName, 'New');
    await user.click(screen.getByRole('button', { name: /save preferences/i }));

    const stored = JSON.parse(
      localStorage.getItem('metar_converter_preferences') || '{}',
    );
    expect(stored.displayName).toBe('New');
    expect(stored.bulletinIdExample).toBe('KEEP12');
  });

  it('resets preferences after confirmation', async () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({
        displayName: 'Custom',
        outputFileExtension: '.iwxxm',
      }),
    );
    const user = userEvent.setup();
    vi.spyOn(window, 'confirm').mockReturnValue(true);

    render(<UserPreferencesDialog {...defaultProps} />);
    await screen.findByDisplayValue('Custom');
    await user.click(
      screen.getByRole('button', { name: /reset preferences to defaults/i }),
    );

    await waitFor(() => {
      expect(screen.getByDisplayValue('prefs')).toBeInTheDocument();
      expect(screen.getByLabelText(/output file extension/i)).toHaveValue('.xml');
    });
  });

  it('handles invalid stored preferences gracefully', async () => {
    localStorage.setItem('metar_converter_preferences', '{not-json');
    render(<UserPreferencesDialog {...defaultProps} />);
    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to load preferences');
    });
    expect(await screen.findByDisplayValue('prefs')).toBeInTheDocument();
  });

  it('does not reset when confirmation is cancelled', async () => {
    localStorage.setItem(
      'metar_converter_preferences',
      JSON.stringify({
        displayName: 'Keep Me',
        outputFileExtension: '.iwxxm',
      }),
    );
    const user = userEvent.setup();
    vi.spyOn(window, 'confirm').mockReturnValue(false);

    render(<UserPreferencesDialog {...defaultProps} />);
    await screen.findByDisplayValue('Keep Me');
    await user.click(
      screen.getByRole('button', { name: /reset preferences to defaults/i }),
    );

    expect(screen.getByDisplayValue('Keep Me')).toBeInTheDocument();
    expect(screen.getByLabelText(/output file extension/i)).toHaveValue('.iwxxm');
  });

  it('closes from cancel and from the dialog backdrop', async () => {
    const onClose = vi.fn();
    const user = userEvent.setup();
    const { rerender } = render(
      <UserPreferencesDialog {...defaultProps} onClose={onClose} />,
    );

    await screen.findByDisplayValue('prefs');
    await user.click(screen.getByRole('button', { name: /cancel/i }));
    expect(onClose).toHaveBeenCalledTimes(1);

    rerender(<UserPreferencesDialog {...defaultProps} onClose={onClose} />);
    await user.click(screen.getByRole('dialog'));
    expect(onClose).toHaveBeenCalledTimes(2);
  });

  it('keeps an empty prior object when the stored value cannot be parsed while saving', async () => {
    localStorage.setItem('metar_converter_preferences', '{broken');
    const user = userEvent.setup();
    render(<UserPreferencesDialog {...defaultProps} />);

    await screen.findByDisplayValue('prefs');
    await user.click(screen.getByRole('button', { name: /save preferences/i }));

    expect(
      JSON.parse(localStorage.getItem('metar_converter_preferences') || '{}'),
    ).toMatchObject({
      displayName: 'prefs',
      email: 'prefs@example.com',
      outputFileExtension: '.xml',
    });
  });

  it('toasts when save fails', async () => {
    const user = userEvent.setup();
    render(<UserPreferencesDialog {...defaultProps} />);
    await screen.findByDisplayValue('prefs');
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('quota');
    });

    await user.click(screen.getByRole('button', { name: /save preferences/i }));

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to save preferences');
    });
  });

  it('toasts when reset fails after confirm', async () => {
    const user = userEvent.setup();
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    render(<UserPreferencesDialog {...defaultProps} />);
    await screen.findByDisplayValue('prefs');
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('quota');
    });

    await user.click(
      screen.getByRole('button', { name: /reset preferences to defaults/i }),
    );

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to reset preferences');
    });
  });

  it('uses an empty display name when the email local-part is missing', async () => {
    render(<UserPreferencesDialog {...defaultProps} userEmail="@domain.com" />);

    const displayName = await screen.findByLabelText(/display \/ output name/i);
    expect(displayName).toHaveValue('');
  });

  it('loads first-time defaults from the email prefix when storage is empty', async () => {
    render(<UserPreferencesDialog {...defaultProps} userEmail="newuser@example.com" />);

    expect(await screen.findByDisplayValue('newuser')).toBeInTheDocument();
    expect(screen.getByLabelText(/output file extension/i)).toHaveValue('.xml');
  });

  it('shows loading spinner before preferences resolve', async () => {
    const { PreferencesLoadingBody } = await import('./UserPreferencesDialog');
    render(<PreferencesLoadingBody />);
    expect(screen.getByText(/loading preferences/i)).toBeInTheDocument();
  });

  it('renders saving label when isSaving', async () => {
    const { PreferencesSaveLabel, prefsControlsDisabled } =
      await import('./UserPreferencesDialog');
    const { rerender } = render(<PreferencesSaveLabel isSaving />);
    expect(screen.getByText(/saving/i)).toBeInTheDocument();
    rerender(<PreferencesSaveLabel isSaving={false} />);
    expect(screen.getByText(/save preferences/i)).toBeInTheDocument();
    expect(prefsControlsDisabled(true, false)).toBe(true);
    expect(prefsControlsDisabled(false, true)).toBe(true);
    expect(prefsControlsDisabled(false, false)).toBe(false);
  });

  it('clears success status after save timeout', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(<UserPreferencesDialog {...defaultProps} />);
    await screen.findByLabelText(/display \/ output name/i);
    await user.click(screen.getByRole('button', { name: /save preferences/i }));
    expect(screen.getByText(/preferences saved successfully/i)).toBeInTheDocument();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(2000);
    });
    expect(
      screen.queryByText(/preferences saved successfully/i),
    ).not.toBeInTheDocument();
    vi.useRealTimers();
  });
});

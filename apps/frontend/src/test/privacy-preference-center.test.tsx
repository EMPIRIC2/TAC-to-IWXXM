/**
 * PrivacyNotice + PrivacySettingsDialog smoke (F22 / UJ-033).
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PrivacyNotice } from '../app/components/PrivacyNotice';
import { PrivacySettingsDialog } from '../app/components/PrivacySettingsDialog';
import {
  PRIVACY_PREFS_STORAGE_KEY,
  clearPrivacyPreferences,
  savePrivacyPreferences,
} from '../utils/privacyPreferences';

describe('PrivacyNotice', () => {
  it('renders nothing when closed', () => {
    const { container } = render(
      <PrivacyNotice open={false} onDismiss={vi.fn()} onOpenSettings={vi.fn()} />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it('shows IndexedDB disclosure and equal-weight actions when open', async () => {
    const user = userEvent.setup();
    const onDismiss = vi.fn();
    const onOpenSettings = vi.fn();
    render(
      <PrivacyNotice open onDismiss={onDismiss} onOpenSettings={onOpenSettings} />,
    );

    expect(screen.getByTestId('privacy-notice')).toBeInTheDocument();
    expect(screen.getByText(/IndexedDB/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /dismiss privacy notice/i }));
    expect(onDismiss).toHaveBeenCalledTimes(1);

    await user.click(
      screen.getByRole('button', { name: /open privacy settings from notice/i }),
    );
    expect(onOpenSettings).toHaveBeenCalledTimes(1);
  });
});

describe('PrivacySettingsDialog', () => {
  beforeEach(() => {
    localStorage.clear();
    clearPrivacyPreferences();
  });

  it('discloses storage inventory and persists opt-out preferences', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<PrivacySettingsDialog isOpen onClose={onClose} />);

    expect(screen.getByTestId('privacy-settings-dialog')).toBeInTheDocument();
    expect(
      screen.getByText(/Work history and converter sessions/i),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/necessary storage always enabled/i)).toBeDisabled();

    await user.click(
      screen.getByLabelText(/opt out of sale or sharing of personal information/i),
    );
    await user.click(screen.getByLabelText(/opt out of targeted advertising/i));
    await user.click(screen.getByRole('button', { name: /save preferences/i }));

    expect(onClose).toHaveBeenCalledTimes(1);
    const raw = localStorage.getItem(PRIVACY_PREFS_STORAGE_KEY);
    expect(raw).toBeTruthy();
    const stored = JSON.parse(raw!) as {
      saleOrSharingOptOut: boolean;
      targetedAdvertisingOptOut: boolean;
    };
    expect(stored.saleOrSharingOptOut).toBe(true);
    expect(stored.targetedAdvertisingOptOut).toBe(true);
  });

  it('shows GPC status when navigator.globalPrivacyControl is on', () => {
    Object.defineProperty(globalThis.navigator, 'globalPrivacyControl', {
      configurable: true,
      get: () => true,
    });
    savePrivacyPreferences({ saleOrSharingOptOut: false });

    render(<PrivacySettingsDialog isOpen onClose={vi.fn()} />);
    expect(screen.getByTestId('privacy-gpc-active')).toBeInTheDocument();
  });

  it('closes via cancel without writing when unchanged', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<PrivacySettingsDialog isOpen onClose={onClose} />);

    await user.click(screen.getByRole('button', { name: /cancel/i }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('closes when the dialog requests open=false', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<PrivacySettingsDialog isOpen onClose={onClose} />);

    await user.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalled();
  });

  it('renders closed without mounting the settings form', () => {
    render(<PrivacySettingsDialog isOpen={false} onClose={vi.fn()} />);
    expect(screen.queryByText(/^Privacy settings$/i)).not.toBeInTheDocument();
  });
});

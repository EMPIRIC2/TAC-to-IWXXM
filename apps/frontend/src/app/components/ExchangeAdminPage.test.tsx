import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ExchangeAdminPage } from './ExchangeAdminPage';
import * as api from '@/utils/exchangeAdminApi';
import type { AllowlistView } from '@/utils/exchangeAdminApi';

vi.mock('@/utils/exchangeAdminApi', () => ({
  fetchExchangeAllowlist: vi.fn(),
  fetchInvitationGroups: vi.fn(),
  fetchExchangePrefs: vi.fn(),
  selectInvitationGroup: vi.fn(),
  setNationalRemarks: vi.fn(),
}));

describe('ExchangeAdminPage', () => {
  beforeEach(() => {
    vi.mocked(api.fetchExchangeAllowlist).mockResolvedValue({
      source: 'DISSEMINATION_EGRESS_ALLOWLIST',
      read_only: true,
      fail_closed: false,
      entries: ['wis2box'],
      admin_replay: false,
      sink_scope: 'wis2',
    });
    vi.mocked(api.fetchInvitationGroups).mockResolvedValue([
      { id: 'group-demo-a', name: 'Demo Centre A', centre_id: 'demo-a' },
    ]);
    vi.mocked(api.fetchExchangePrefs).mockResolvedValue({
      include_national_remarks: false,
      invitation_group_id: 'group-demo-a',
      admin_replay: false,
      sink_scope: 'wis2',
    });
    vi.mocked(api.selectInvitationGroup).mockResolvedValue({
      include_national_remarks: false,
      invitation_group_id: 'group-demo-a',
      admin_replay: false,
      sink_scope: 'wis2',
    });
    vi.mocked(api.setNationalRemarks).mockResolvedValue({
      include_national_remarks: true,
      invitation_group_id: 'group-demo-a',
      admin_replay: false,
      sink_scope: 'wis2',
    });
  });

  it('success: shows read-only allowlist and remarks toggle', async () => {
    const user = userEvent.setup();
    render(<ExchangeAdminPage token="tok" />);
    expect(await screen.findByTestId('exchange-admin-allowlist')).toHaveTextContent(
      'wis2box',
    );
    expect(screen.getByText(/Admin replay is not available/i)).toBeInTheDocument();
    await user.click(screen.getByTestId('exchange-admin-remarks'));
    await waitFor(() => {
      expect(api.setNationalRemarks).toHaveBeenCalledWith('tok', true);
    });
  });

  it('failure: shows load error', async () => {
    vi.mocked(api.fetchExchangeAllowlist).mockRejectedValue(new Error('forbidden'));
    render(<ExchangeAdminPage token="tok" />);
    expect(await screen.findByTestId('exchange-admin-error')).toHaveTextContent(
      'forbidden',
    );
  });

  it('validation: empty allowlist shows closed message', async () => {
    vi.mocked(api.fetchExchangeAllowlist).mockResolvedValue({
      source: 'DISSEMINATION_EGRESS_ALLOWLIST',
      read_only: true,
      fail_closed: true,
      entries: [],
      admin_replay: false,
      sink_scope: 'wis2',
    });
    render(<ExchangeAdminPage token="tok" />);
    expect(
      await screen.findByTestId('exchange-admin-allowlist-empty'),
    ).toBeInTheDocument();
  });

  it('success: group select clears prior error', async () => {
    const user = userEvent.setup();
    vi.mocked(api.fetchInvitationGroups).mockResolvedValue([
      { id: 'group-demo-a', name: 'Demo Centre A', centre_id: 'demo-a' },
      { id: 'group-demo-b', name: 'Demo Centre B', centre_id: 'demo-b' },
    ]);
    vi.mocked(api.selectInvitationGroup).mockResolvedValue({
      include_national_remarks: false,
      invitation_group_id: 'group-demo-b',
      admin_replay: false,
      sink_scope: 'wis2',
    });
    render(<ExchangeAdminPage token="tok" />);
    await screen.findByTestId('exchange-admin-allowlist');
    await user.selectOptions(
      screen.getByTestId('exchange-admin-group'),
      'group-demo-b',
    );
    await waitFor(() => {
      expect(api.selectInvitationGroup).toHaveBeenCalledWith('tok', 'group-demo-b');
    });
    expect(screen.queryByTestId('exchange-admin-error')).not.toBeInTheDocument();
  });

  it('failure: group select surfaces save error', async () => {
    const user = userEvent.setup();
    vi.mocked(api.fetchInvitationGroups).mockResolvedValue([
      { id: 'group-demo-a', name: 'Demo Centre A', centre_id: 'demo-a' },
      { id: 'group-demo-b', name: 'Demo Centre B', centre_id: 'demo-b' },
    ]);
    vi.mocked(api.selectInvitationGroup).mockRejectedValue(
      new Error('group save failed'),
    );
    render(<ExchangeAdminPage token="tok" />);
    await screen.findByTestId('exchange-admin-allowlist');
    await user.selectOptions(
      screen.getByTestId('exchange-admin-group'),
      'group-demo-b',
    );
    expect(await screen.findByTestId('exchange-admin-error')).toHaveTextContent(
      'group save failed',
    );
  });

  it('failure: non-Error group reject uses fallback message', async () => {
    const user = userEvent.setup();
    vi.mocked(api.fetchInvitationGroups).mockResolvedValue([
      { id: 'group-demo-a', name: 'Demo Centre A', centre_id: 'demo-a' },
      { id: 'group-demo-b', name: 'Demo Centre B', centre_id: 'demo-b' },
    ]);
    vi.mocked(api.selectInvitationGroup).mockRejectedValue('boom');
    render(<ExchangeAdminPage token="tok" />);
    await screen.findByTestId('exchange-admin-allowlist');
    await user.selectOptions(
      screen.getByTestId('exchange-admin-group'),
      'group-demo-b',
    );
    expect(await screen.findByTestId('exchange-admin-error')).toHaveTextContent(
      'Could not save group',
    );
  });

  it('failure: remarks toggle rolls back on error', async () => {
    const user = userEvent.setup();
    vi.mocked(api.setNationalRemarks).mockRejectedValue(
      new Error('remarks save failed'),
    );
    render(<ExchangeAdminPage token="tok" />);
    await screen.findByTestId('exchange-admin-allowlist');
    const box = screen.getByTestId('exchange-admin-remarks');
    expect(box).not.toBeChecked();
    await user.click(box);
    expect(await screen.findByTestId('exchange-admin-error')).toHaveTextContent(
      'remarks save failed',
    );
    expect(box).not.toBeChecked();
  });

  it('failure: non-Error remarks reject uses fallback and rolls back', async () => {
    const user = userEvent.setup();
    vi.mocked(api.setNationalRemarks).mockRejectedValue('nope');
    render(<ExchangeAdminPage token="tok" />);
    await screen.findByTestId('exchange-admin-allowlist');
    const box = screen.getByTestId('exchange-admin-remarks');
    await user.click(box);
    expect(await screen.findByTestId('exchange-admin-error')).toHaveTextContent(
      'Could not save preference',
    );
    expect(box).not.toBeChecked();
  });

  it('validation: null prefs group falls back to first invitation group', async () => {
    vi.mocked(api.fetchExchangePrefs).mockResolvedValue({
      include_national_remarks: false,
      invitation_group_id: null,
      admin_replay: false,
      sink_scope: 'wis2',
    });
    render(<ExchangeAdminPage token="tok" />);
    const select = await screen.findByTestId('exchange-admin-group');
    expect(select).toHaveValue('group-demo-a');
  });

  it('validation: empty groups leave the select disabled', async () => {
    vi.mocked(api.fetchInvitationGroups).mockResolvedValue([]);
    vi.mocked(api.fetchExchangePrefs).mockResolvedValue({
      include_national_remarks: false,
      invitation_group_id: null,
      admin_replay: false,
      sink_scope: 'wis2',
    });
    render(<ExchangeAdminPage token="tok" />);
    expect(await screen.findByTestId('exchange-admin-group')).toBeDisabled();
  });

  it('failure: non-Error load reject uses fallback message', async () => {
    vi.mocked(api.fetchExchangeAllowlist).mockRejectedValue('down');
    render(<ExchangeAdminPage token="tok" />);
    expect(await screen.findByTestId('exchange-admin-error')).toHaveTextContent(
      'Could not load exchange admin',
    );
  });

  it('cancels in-flight load on unmount', async () => {
    let resolveAllowlist: (value: AllowlistView) => void = () => undefined;
    vi.mocked(api.fetchExchangeAllowlist).mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveAllowlist = resolve;
        }),
    );
    const { unmount } = render(<ExchangeAdminPage token="tok" />);
    unmount();
    resolveAllowlist({
      source: 'DISSEMINATION_EGRESS_ALLOWLIST',
      read_only: true,
      fail_closed: false,
      entries: ['wis2box'],
      admin_replay: false,
      sink_scope: 'wis2',
    });
    await waitFor(() => {
      expect(screen.queryByTestId('exchange-admin-page')).not.toBeInTheDocument();
    });
  });

  it('ignores load errors after unmount', async () => {
    let rejectAllowlist: (reason?: unknown) => void = () => undefined;
    vi.mocked(api.fetchExchangeAllowlist).mockImplementation(
      () =>
        new Promise((_resolve, reject) => {
          rejectAllowlist = reject;
        }),
    );
    const { unmount } = render(<ExchangeAdminPage token="tok" />);
    unmount();
    rejectAllowlist(new Error('late failure'));
    await waitFor(() => {
      expect(screen.queryByTestId('exchange-admin-error')).not.toBeInTheDocument();
    });
  });
});

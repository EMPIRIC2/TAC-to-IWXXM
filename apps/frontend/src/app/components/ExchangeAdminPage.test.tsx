import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ExchangeAdminPage } from './ExchangeAdminPage';
import * as api from '@/utils/exchangeAdminApi';

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
});

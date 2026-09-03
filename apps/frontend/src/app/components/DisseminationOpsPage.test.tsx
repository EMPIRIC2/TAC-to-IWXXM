import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DisseminationOpsPage } from './DisseminationOpsPage';
import * as opsApi from '@/utils/disseminationOpsApi';
import {
  DISSEMINATION_OPS_LOGIN_REQUIRED,
  DISSEMINATION_OPS_TITLE,
} from '@/utils/disseminationOpsCopy';

vi.mock('@/utils/disseminationOpsApi', () => ({
  fetchGatewayHealth: vi.fn(),
  listDisseminationAudit: vi.fn(),
  upsertDisseminationPlan: vi.fn(),
  executeDisseminationPlan: vi.fn(),
  upsertMappingConfig: vi.fn(),
}));

const mocked = vi.mocked(opsApi);

describe('DisseminationOpsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocked.fetchGatewayHealth.mockResolvedValue({
      items: [
        {
          ok: true,
          gateway: 'file',
          connectivity_ok: true,
          detail: 'local ok',
        },
        {
          ok: false,
          gateway: 'wis2',
          connectivity_ok: false,
        },
      ],
    });
    mocked.listDisseminationAudit.mockResolvedValue({
      items: [
        {
          id: 'a1',
          user_id: 'u1',
          status: 'DELIVERED',
          gateway: 'file',
          station: 'KJFK',
          product: 'metar',
          detail: 'ok',
          destinations: {},
          created_at: '2026-09-03T00:00:00Z',
        },
      ],
      total: 1,
      page: 1,
      limit: 20,
    });
  });

  it('prompts for sign-in when no token', async () => {
    const onRequestLogin = vi.fn();
    const user = userEvent.setup();
    render(<DisseminationOpsPage onRequestLogin={onRequestLogin} />);

    expect(screen.getByText(DISSEMINATION_OPS_TITLE)).toBeInTheDocument();
    expect(screen.getByText(DISSEMINATION_OPS_LOGIN_REQUIRED)).toBeInTheDocument();
    await user.click(screen.getByTestId('dissemination-ops-sign-in'));
    expect(onRequestLogin).toHaveBeenCalled();
    expect(mocked.fetchGatewayHealth).not.toHaveBeenCalled();
  });

  it('renders guest prompt without sign-in button when callback missing', () => {
    render(<DisseminationOpsPage />);
    expect(screen.getByText(DISSEMINATION_OPS_LOGIN_REQUIRED)).toBeInTheDocument();
    expect(screen.queryByTestId('dissemination-ops-sign-in')).not.toBeInTheDocument();
  });

  it('loads health and audit when authenticated', async () => {
    render(<DisseminationOpsPage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('gateway-health-file')).toBeInTheDocument();
    });
    expect(screen.getByTestId('gateway-health-wis2')).toHaveTextContent(/Not OK/);
    expect(screen.getByTestId('audit-row-a1')).toHaveTextContent('DELIVERED');
    expect(screen.getByTestId('audit-row-a1')).toHaveTextContent('KJFK');
  });

  it('shows empty health and audit states', async () => {
    mocked.fetchGatewayHealth.mockResolvedValue({ items: [] });
    mocked.listDisseminationAudit.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      limit: 20,
    });
    render(<DisseminationOpsPage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByText(/No gateway health rows/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/No delivery records yet/i)).toBeInTheDocument();
  });

  it('shows loading indicators while health and audit resolve', async () => {
    let resolveHealth!: (value: opsApi.GatewayHealthListResponse) => void;
    let resolveAudit!: (value: opsApi.AuditListResponse) => void;
    mocked.fetchGatewayHealth.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveHealth = resolve;
        }),
    );
    mocked.listDisseminationAudit.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveAudit = resolve;
        }),
    );

    render(<DisseminationOpsPage accessToken="tok" />);
    expect(await screen.findByText(/Loading gateway health/i)).toBeInTheDocument();
    expect(screen.getByText(/Loading delivery history/i)).toBeInTheDocument();

    resolveHealth({ items: [] });
    resolveAudit({ items: [], total: 0, page: 1, limit: 20 });
    await waitFor(() => {
      expect(screen.getByText(/No gateway health rows/i)).toBeInTheDocument();
    });
  });

  it('renders audit rows without optional fields', async () => {
    mocked.listDisseminationAudit.mockResolvedValue({
      items: [
        {
          id: 'a2',
          user_id: 'u1',
          status: 'FAILED',
          gateway: 'file',
          destinations: {},
          created_at: '2026-09-03T00:00:00Z',
        },
      ],
      total: 1,
      page: 1,
      limit: 20,
    });
    render(<DisseminationOpsPage accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('audit-row-a2')).toHaveTextContent('FAILED');
    });
    expect(screen.getByTestId('audit-row-a2')).not.toHaveTextContent('KJFK');
  });

  it('shows load error', async () => {
    mocked.fetchGatewayHealth.mockRejectedValue(new Error('boom'));
    render(<DisseminationOpsPage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-ops-error')).toHaveTextContent('boom');
    });
  });

  it('shows non-Error load failure message', async () => {
    mocked.fetchGatewayHealth.mockRejectedValue('fail-string');
    render(<DisseminationOpsPage accessToken="tok" />);

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-ops-error')).toHaveTextContent(
        'Unknown error',
      );
    });
  });

  it('saves plan, dry-runs, and saves mapping', async () => {
    const user = userEvent.setup();
    mocked.upsertDisseminationPlan.mockResolvedValue({
      id: 'plan-1',
      user_id: 'u1',
      slug: 'default',
      validity_policy: 'valid-only',
      destination_refs: ['file'],
      transforms: [],
      created_at: '2026-09-03T00:00:00Z',
      updated_at: '2026-09-03T00:00:00Z',
    });
    mocked.executeDisseminationPlan.mockResolvedValue({
      plan_id: 'plan-1',
      receipts: [{ status: 'SKIPPED', gateway: 'file' }],
    });
    mocked.upsertMappingConfig.mockResolvedValue({
      id: 'map-1',
      user_id: 'u1',
      name: 'default',
      mode: 'source',
      config: {},
      created_at: '2026-09-03T00:00:00Z',
      updated_at: '2026-09-03T00:00:00Z',
    });

    render(<DisseminationOpsPage accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('plan-save')).toBeInTheDocument();
    });

    await user.clear(screen.getByTestId('plan-slug-input'));
    await user.type(screen.getByTestId('plan-slug-input'), 'nightly');
    await user.selectOptions(screen.getByTestId('plan-policy-select'), 'warn-ok');
    await user.clear(screen.getByTestId('plan-dests-input'));
    await user.type(screen.getByTestId('plan-dests-input'), 'file, wis2');
    await user.clear(screen.getByTestId('mapping-name-input'));
    await user.type(screen.getByTestId('mapping-name-input'), 'station-map');
    await user.click(screen.getByTestId('plan-save'));

    await waitFor(() => {
      expect(screen.getByTestId('plan-saved-id')).toHaveTextContent('plan-1');
    });
    expect(mocked.upsertDisseminationPlan).toHaveBeenCalledWith(
      'tok',
      'nightly',
      expect.objectContaining({
        validity_policy: 'warn-ok',
        destination_refs: ['file', 'wis2'],
      }),
    );

    await user.click(screen.getByTestId('plan-dry-run'));
    await waitFor(() => {
      expect(screen.getByTestId('plan-execute-note')).toHaveTextContent(/Dry-run/);
    });

    await user.selectOptions(screen.getByTestId('mapping-mode-select'), 'sink');
    await user.click(screen.getByTestId('mapping-save'));
    await waitFor(() => {
      expect(screen.getByTestId('mapping-saved-id')).toHaveTextContent('map-1');
    });
    expect(mocked.upsertMappingConfig).toHaveBeenCalledWith(
      'tok',
      'station-map',
      expect.objectContaining({ mode: 'sink' }),
    );
  });

  it('shows plan save and dry-run errors', async () => {
    const user = userEvent.setup();
    mocked.upsertDisseminationPlan.mockRejectedValue(new Error('plan fail'));
    render(<DisseminationOpsPage accessToken="tok" />);
    await waitFor(() => expect(screen.getByTestId('plan-save')).toBeEnabled());

    await user.click(screen.getByTestId('plan-save'));
    await waitFor(() => {
      expect(screen.getByTestId('dissemination-ops-error')).toHaveTextContent(
        'plan fail',
      );
    });

    mocked.upsertDisseminationPlan.mockResolvedValue({
      id: 'plan-1',
      user_id: 'u1',
      slug: 'default',
      validity_policy: 'valid-only',
      destination_refs: [],
      transforms: [],
      created_at: '2026-09-03T00:00:00Z',
      updated_at: '2026-09-03T00:00:00Z',
    });
    mocked.executeDisseminationPlan.mockRejectedValue(new Error('exec fail'));
    await user.click(screen.getByTestId('plan-save'));
    await waitFor(() =>
      expect(screen.getByTestId('plan-saved-id')).toBeInTheDocument(),
    );
    await user.click(screen.getByTestId('plan-dry-run'));
    await waitFor(() => {
      expect(screen.getByTestId('dissemination-ops-error')).toHaveTextContent(
        'exec fail',
      );
    });
  });

  it('shows mapping save error', async () => {
    const user = userEvent.setup();
    mocked.upsertMappingConfig.mockRejectedValue(new Error('map fail'));
    render(<DisseminationOpsPage accessToken="tok" />);
    await waitFor(() => expect(screen.getByTestId('mapping-save')).toBeEnabled());
    await user.click(screen.getByTestId('mapping-save'));
    await waitFor(() => {
      expect(screen.getByTestId('dissemination-ops-error')).toHaveTextContent(
        'map fail',
      );
    });
  });

  it('dry-run with empty receipts still notes completion', async () => {
    const user = userEvent.setup();
    mocked.upsertDisseminationPlan.mockResolvedValue({
      id: 'plan-1',
      user_id: 'u1',
      slug: 'default',
      validity_policy: 'valid-only',
      destination_refs: [],
      transforms: [],
      created_at: '2026-09-03T00:00:00Z',
      updated_at: '2026-09-03T00:00:00Z',
    });
    mocked.executeDisseminationPlan.mockResolvedValue({
      plan_id: 'plan-1',
      receipts: [],
    });
    render(<DisseminationOpsPage accessToken="tok" />);
    await waitFor(() => expect(screen.getByTestId('plan-save')).toBeEnabled());
    await user.click(screen.getByTestId('plan-save'));
    await waitFor(() =>
      expect(screen.getByTestId('plan-saved-id')).toBeInTheDocument(),
    );
    await user.click(screen.getByTestId('plan-dry-run'));
    await waitFor(() => {
      expect(screen.getByTestId('plan-execute-note')).toHaveTextContent(/none/);
    });
  });

  it('dry-run no-ops when plan is not yet saved', async () => {
    const user = userEvent.setup();
    render(<DisseminationOpsPage accessToken="tok" />);
    await waitFor(() => expect(screen.getByTestId('plan-dry-run')).toBeEnabled());
    await user.click(screen.getByTestId('plan-dry-run'));
    expect(mocked.executeDisseminationPlan).not.toHaveBeenCalled();
  });
});

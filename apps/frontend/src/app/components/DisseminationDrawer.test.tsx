/**
 * T6.1 — Vitest: drawer sink chooser + preflight diff + block Send (TC-F16-001/004; UJ-027).
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { DisseminationDrawer } from './DisseminationDrawer';
import { DRAWER_SINK_TYPES, isPreflightGreen } from '/utils/dissemination';

vi.mock('/utils/apiBase', () => ({
  apiUrl: (path: string) =>
    `http://api.test/api/v1${path.startsWith('/') ? path : `/${path}`}`,
  getApiBaseUrl: () => 'http://api.test',
}));

const defaultProps = {
  open: true,
  onOpenChange: vi.fn(),
  accessToken: 'drawer-token',
  iwxxmXml: '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>',
  product: 'metar',
};

describe('isPreflightGreen', () => {
  it('blocks Send when preflight is missing, failed, or has diffs', () => {
    expect(isPreflightGreen(null)).toBe(false);
    expect(
      isPreflightGreen({
        ok: false,
        connectivity_ok: false,
        diffs: [],
        handle: null,
      }),
    ).toBe(false);
    expect(
      isPreflightGreen({
        ok: true,
        connectivity_ok: true,
        diffs: [
          {
            kind: 'missing_column',
            table: 'iwxxm_reports',
            detail: 'need created_at',
            column: 'created_at',
          },
        ],
        handle: 'h1',
      }),
    ).toBe(false);
    expect(
      isPreflightGreen({
        ok: true,
        connectivity_ok: true,
        diffs: [],
        handle: null,
      }),
    ).toBe(false);
  });

  it('allows Send only when ok, connectivity_ok, empty diffs, and handle present', () => {
    expect(
      isPreflightGreen({
        ok: true,
        connectivity_ok: true,
        diffs: [],
        handle: 'mem-handle-1',
      }),
    ).toBe(true);
  });
});

describe('DisseminationDrawer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(global, 'fetch');
  });

  it('renders nothing when closed', () => {
    const { container } = render(
      <DisseminationDrawer {...defaultProps} open={false} />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it('exposes sink chooser with all drawer-ready sink types (F16–F19)', () => {
    render(<DisseminationDrawer {...defaultProps} />);

    expect(screen.getByTestId('dissemination-drawer')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /dissemination/i })).toBeInTheDocument();

    const chooser = screen.getByTestId('dissemination-sink-chooser');
    expect(chooser).toBeInTheDocument();

    for (const sink of DRAWER_SINK_TYPES) {
      expect(
        screen.getByTestId(`dissemination-sink-option-${sink}`),
      ).toBeInTheDocument();
    }
    expect(DRAWER_SINK_TYPES).toHaveLength(9);
  });

  it('blocks Send until preflight is green (TC-F16-001)', async () => {
    const user = userEvent.setup();
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => ({
        ok: false,
        connectivity_ok: true,
        diffs: [
          {
            kind: 'missing_column',
            table: 'iwxxm_reports',
            column: 'iwxxm_xml',
            detail: 'column missing — run DDL or alter table',
          },
        ],
        handle: null,
        detail: 'schema mismatch',
      }),
    } as Response);

    render(<DisseminationDrawer {...defaultProps} />);

    const sendBtn = screen.getByTestId('dissemination-send-button');
    expect(sendBtn).toBeDisabled();

    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'postgresql://u:p@db.example.com/wx',
    );
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-preflight-diffs')).toBeInTheDocument();
    });
    expect(screen.getByTestId('dissemination-diff-item')).toHaveTextContent(
      /missing_column/,
    );
    expect(screen.getByTestId('dissemination-diff-item')).toHaveTextContent(
      /iwxxm_xml/,
    );
    expect(sendBtn).toBeDisabled();
    expect(global.fetch).toHaveBeenCalledWith(
      'http://api.test/api/v1/dissemination/preflight',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          Authorization: 'Bearer drawer-token',
        }),
      }),
    );
  });

  it('enables Send after green preflight and posts handle (TC-F16-001)', async () => {
    const user = userEvent.setup();
    vi.mocked(global.fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          ok: true,
          connectivity_ok: true,
          diffs: [],
          handle: 'opaque-handle-abc',
          detail: null,
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          ok: true,
          kv_upload_key: 'kv:upload:1',
          detail: null,
        }),
      } as Response);

    render(<DisseminationDrawer {...defaultProps} />);

    await user.selectOptions(
      screen.getByTestId('dissemination-sink-chooser'),
      'sqlite',
    );
    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/wx.db',
    );
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-preflight-green')).toBeInTheDocument();
    });

    const sendBtn = screen.getByTestId('dissemination-send-button');
    expect(sendBtn).toBeEnabled();

    await user.click(sendBtn);

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-send-success')).toHaveTextContent(
        /kv:upload:1/,
      );
    });

    expect(global.fetch).toHaveBeenNthCalledWith(
      2,
      'http://api.test/api/v1/dissemination/send',
      expect.objectContaining({
        method: 'POST',
        body: expect.stringContaining('opaque-handle-abc'),
      }),
    );
  });

  it('accepts drag-drop / file payload on the same preflight→send path (TC-F16-004)', async () => {
    const user = userEvent.setup();
    vi.mocked(global.fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          ok: true,
          connectivity_ok: true,
          diffs: [],
          handle: 'drop-handle',
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          ok: true,
          kv_upload_key: 'kv:drop:1',
        }),
      } as Response);

    render(
      <DisseminationDrawer
        {...defaultProps}
        iwxxmXml={undefined}
        tacText={undefined}
      />,
    );

    const file = new File(['METAR KJFK 010000Z ...='], 'sample.tac', {
      type: 'text/plain',
    });
    const input = screen.getByTestId('dissemination-file-input');
    await user.upload(input, file);

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-payload-status')).toHaveTextContent(
        /TAC/,
      );
    });

    expect(screen.getByTestId('dissemination-send-button')).toBeDisabled();

    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/drop.db',
    );
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-send-button')).toBeEnabled();
    });

    await user.click(screen.getByTestId('dissemination-send-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-send-success')).toBeInTheDocument();
    });

    const sendBody = JSON.parse(
      (
        global.fetch as unknown as {
          mock: { calls: [unknown, [string, { body: string }]] };
        }
      ).mock.calls[1][1].body,
    );
    expect(sendBody.handle).toBe('drop-handle');
    expect(sendBody.tac_text).toContain('METAR KJFK');
  });

  it('keeps Send disabled without auth token even after typing URI', async () => {
    const user = userEvent.setup();
    render(<DisseminationDrawer {...defaultProps} accessToken={undefined} />);

    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/x.db',
    );
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-error')).toHaveTextContent(
        /authentication/i,
      );
    });
    expect(screen.getByTestId('dissemination-send-button')).toBeDisabled();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('shows BYOC JSON params for non-DB sinks and includes them in preflight (T6.2)', async () => {
    const user = userEvent.setup();
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => ({
        ok: true,
        connectivity_ok: true,
        diffs: [],
        handle: 'wis2-handle',
      }),
    } as Response);

    render(<DisseminationDrawer {...defaultProps} />);

    await user.selectOptions(screen.getByTestId('dissemination-sink-chooser'), 'wis2');
    expect(screen.getByTestId('dissemination-byoc-params')).toBeInTheDocument();
    expect(screen.queryByTestId('dissemination-uri-input')).not.toBeInTheDocument();

    fireEvent.change(screen.getByTestId('dissemination-byoc-params'), {
      target: {
        value: JSON.stringify({
          broker: 'mqtt://wis2.example',
          topic: 'origin/a/wis2',
        }),
      },
    });
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
    const body = JSON.parse(
      (global.fetch as unknown as { mock: { calls: [[string, { body: string }]] } })
        .mock.calls[0][1].body,
    );
    expect(body.sink_type).toBe('wis2');
    expect(body.params).toEqual({
      broker: 'mqtt://wis2.example',
      topic: 'origin/a/wis2',
    });
  });
});

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
          'Content-Type': 'application/json',
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

  it('allows preflight without auth token (F21 public)', async () => {
    const user = userEvent.setup();
    vi.mocked(global.fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ok: true,
        connectivity_ok: true,
        diffs: [],
        handle: 'h1',
      }),
    } as Response);

    render(<DisseminationDrawer {...defaultProps} />);

    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/x.db',
    );
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
    const init = vi.mocked(global.fetch).mock.calls[0][1] as RequestInit;
    expect(
      (init.headers as Record<string, string> | undefined)?.Authorization,
    ).toBeUndefined();
  });

  it('rejects invalid BYOC JSON before calling preflight', async () => {
    const user = userEvent.setup();
    render(<DisseminationDrawer {...defaultProps} />);

    await user.selectOptions(screen.getByTestId('dissemination-sink-chooser'), 'edis');
    fireEvent.change(screen.getByTestId('dissemination-byoc-params'), {
      target: { value: 'not-json' },
    });
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    expect(screen.getByTestId('dissemination-error')).toHaveTextContent(/invalid/i);
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('blocks Send when payload is empty even after green preflight', async () => {
    const user = userEvent.setup();
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => ({
        ok: true,
        connectivity_ok: true,
        diffs: [],
        handle: 'no-payload-handle',
      }),
    } as Response);

    render(
      <DisseminationDrawer
        {...defaultProps}
        iwxxmXml={undefined}
        tacText={undefined}
      />,
    );

    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/empty.db',
    );
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-preflight-green')).toBeInTheDocument();
    });
    expect(screen.getByTestId('dissemination-send-button')).toBeDisabled();
  });

  it('closes via close control', async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    render(<DisseminationDrawer {...defaultProps} onOpenChange={onOpenChange} />);

    await user.click(screen.getByTestId('dissemination-drawer-close'));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it('toggles DDL and accepts drag-drop IWXXM on the dropzone', async () => {
    const user = userEvent.setup();
    render(
      <DisseminationDrawer
        {...defaultProps}
        iwxxmXml={undefined}
        tacText={undefined}
      />,
    );

    const ddl = screen.getByTestId('dissemination-ddl-toggle');
    expect(ddl).not.toBeChecked();
    await user.click(ddl);
    expect(ddl).toBeChecked();

    const dropzone = screen.getByTestId('dissemination-dropzone');
    const file = new File(['<iwxxm:METAR/>'], 'report.xml', { type: 'text/xml' });
    fireEvent.dragOver(dropzone, {
      dataTransfer: { files: [file] },
    });
    fireEvent.drop(dropzone, {
      dataTransfer: { files: [file] },
    });

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-payload-status')).toHaveTextContent(
        /IWXXM/,
      );
    });
  });

  it('rejects non-object BYOC JSON arrays', async () => {
    const user = userEvent.setup();
    render(<DisseminationDrawer {...defaultProps} />);

    await user.selectOptions(screen.getByTestId('dissemination-sink-chooser'), 'amhs');
    fireEvent.change(screen.getByTestId('dissemination-byoc-params'), {
      target: { value: '[]' },
    });
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    expect(screen.getByTestId('dissemination-error')).toHaveTextContent(/JSON object/i);
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('surfaces send API errors after green preflight', async () => {
    const user = userEvent.setup();
    vi.mocked(global.fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          ok: true,
          connectivity_ok: true,
          diffs: [],
          handle: 'send-fail-handle',
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Server Error',
        json: async () => ({ detail: 'sink unavailable' }),
      } as Response);

    render(<DisseminationDrawer {...defaultProps} />);

    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/s.db',
    );
    await user.click(screen.getByTestId('dissemination-preflight-button'));
    await waitFor(() => {
      expect(screen.getByTestId('dissemination-send-button')).toBeEnabled();
    });
    await user.click(screen.getByTestId('dissemination-send-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-error')).toHaveTextContent(
        /sink unavailable/,
      );
    });
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

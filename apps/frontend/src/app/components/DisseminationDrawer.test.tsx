/**
 * Dissemination drawer Vitest — F16 / TC-F16-001/004/005; UJ-027; EV-018; EV-091.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { DisseminationDrawer } from './DisseminationDrawer';
import { DRAWER_SINK_TYPES, isPreflightGreen } from '/utils/dissemination';

const mockRunDisseminationQueue = vi.hoisted(() => vi.fn());
const actualRunDisseminationQueue = vi.hoisted(() => ({
  fn: null as typeof import('/utils/disseminationQueue').runDisseminationQueue | null,
}));
const mockConvertMetarToIwxxm = vi.hoisted(() => vi.fn());

vi.mock('/utils/disseminationQueue', async (importOriginal) => {
  const actual = await importOriginal<typeof import('/utils/disseminationQueue')>();
  actualRunDisseminationQueue.fn = actual.runDisseminationQueue;
  mockRunDisseminationQueue.mockImplementation(actual.runDisseminationQueue);
  return {
    ...actual,
    runDisseminationQueue: (...args: unknown[]) => mockRunDisseminationQueue(...args),
  };
});

vi.mock('/utils/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('/utils/api')>();
  return {
    ...actual,
    convertMetarToIwxxm: (...args: unknown[]) => mockConvertMetarToIwxxm(...args),
  };
});

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
    mockRunDisseminationQueue.mockClear();
    mockRunDisseminationQueue.mockImplementation(actualRunDisseminationQueue.fn!);
    mockConvertMetarToIwxxm.mockReset();
    mockConvertMetarToIwxxm.mockResolvedValue({
      results: [{ iwxxm_xml: '<iwxxm>from-convert</iwxxm>' }],
    });
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    mockRunDisseminationQueue.mockImplementation(actualRunDisseminationQueue.fn!);
    vi.unstubAllGlobals();
  });

  it('renders exchange profile select defaulting to GLOBAL_AFS (TC-EV091-002 / #1089)', () => {
    render(<DisseminationDrawer {...defaultProps} />);
    const select = screen.getByTestId('dissemination-exchange-profile');
    expect(select).toHaveValue('GLOBAL_AFS');
    expect(
      screen.getByTestId('dissemination-exchange-profile-help'),
    ).toBeInTheDocument();
  });

  it('hydrates exchange profile from workbench prop when drawer opens', () => {
    const { rerender } = render(
      <DisseminationDrawer
        key="closed"
        {...defaultProps}
        open={false}
        exchangeProfile="EUR_RODEX"
      />,
    );
    rerender(
      <DisseminationDrawer
        key="open-EUR_RODEX"
        {...defaultProps}
        open
        exchangeProfile="EUR_RODEX"
      />,
    );
    expect(screen.getByTestId('dissemination-exchange-profile')).toHaveValue(
      'EUR_RODEX',
    );
  });

  it('renders nothing when closed', () => {
    const { container } = render(
      <DisseminationDrawer {...defaultProps} open={false} />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it('renders sink chooser for all drawer sink types', () => {
    render(<DisseminationDrawer {...defaultProps} />);
    expect(screen.getByTestId('dissemination-sink-chooser')).toBeInTheDocument();
    expect(DRAWER_SINK_TYPES).toHaveLength(9);
  });

  it('shows red progress fail when Disseminate preflight is not green (TC-F16-001)', async () => {
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

    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'postgresql://u:p@db.example.com/wx',
    );
    await user.click(screen.getByTestId('dissemination-send-button'));

    await waitFor(() => {
      expect(
        screen.getByTestId('dissemination-progress-row-session-primary'),
      ).toHaveAttribute('data-status', 'failed');
    });
    expect(global.fetch).toHaveBeenCalledWith(
      'http://api.test/api/v1/dissemination/preflight',
      expect.objectContaining({ method: 'POST' }),
    );
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  it('Disseminate runs interleaved preflight→send and shows success (TC-F16-001)', async () => {
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
    await user.click(screen.getByTestId('dissemination-send-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-send-success')).toBeInTheDocument();
    });
    expect(
      screen.getByTestId('dissemination-progress-row-session-primary'),
    ).toHaveAttribute('data-status', 'success');

    expect(global.fetch).toHaveBeenNthCalledWith(
      2,
      'http://api.test/api/v1/dissemination/send',
      expect.objectContaining({
        method: 'POST',
        body: expect.stringContaining('opaque-handle-abc'),
      }),
    );
  });

  it('accepts drag-drop / file payload on Disseminate path (TC-F16-004)', async () => {
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
        /1 candidate/,
      );
    });

    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/drop.db',
    );
    await user.click(screen.getByTestId('dissemination-send-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-send-success')).toBeInTheDocument();
    });

    expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        manualText: expect.stringContaining('METAR KJFK'),
        exchangeProfile: 'GLOBAL_AFS',
      }),
    );

    const sendBody = JSON.parse(
      (
        global.fetch as unknown as {
          mock: { calls: [unknown, [string, { body: string }]] };
        }
      ).mock.calls[1][1].body,
    );
    expect(sendBody.handle).toBe('drop-handle');
    expect(sendBody.iwxxm_xml).toContain('from-convert');
    expect(sendBody.tac_text).toContain('METAR KJFK');
  });

  it('TC-EV091-002: selected exchange overlay is sent on convert-before-send (#1089)', async () => {
    const user = userEvent.setup();
    vi.mocked(global.fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          ok: true,
          connectivity_ok: true,
          diffs: [],
          handle: 'overlay-handle',
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          ok: true,
          kv_upload_key: 'kv:overlay:1',
        }),
      } as Response);

    render(
      <DisseminationDrawer
        {...defaultProps}
        iwxxmXml={undefined}
        tacText="METAR KJFK 010000Z 18004KT="
      />,
    );

    await user.selectOptions(
      screen.getByTestId('dissemination-exchange-profile'),
      'APAC_ROBEX',
    );
    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'postgresql://u:p@db.example.com/wx',
    );
    await user.click(screen.getByTestId('dissemination-send-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-send-success')).toBeInTheDocument();
    });

    expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        exchangeProfile: 'APAC_ROBEX',
        manualText: expect.stringContaining('METAR KJFK'),
      }),
    );
    const sendBody = JSON.parse(
      (
        global.fetch as unknown as {
          mock: { calls: [unknown, [string, { body: string }]] };
        }
      ).mock.calls[1][1].body,
    );
    expect(sendBody.iwxxm_xml).toContain('from-convert');
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
    const init = vi.mocked(global.fetch).mock.calls[0]![1] as RequestInit;
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

  it('disables Disseminate when there is no payload (TC-F16-001)', async () => {
    const user = userEvent.setup();
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
    expect(screen.getByTestId('dissemination-send-button')).toBeDisabled();
    expect(screen.getByTestId('dissemination-preflight-button')).toBeDisabled();
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
        /1 candidate/,
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

  it('surfaces send API errors during Disseminate', async () => {
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
    await user.click(screen.getByTestId('dissemination-send-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-error')).toHaveTextContent(
        /failed|sink unavailable/i,
      );
    });
    expect(
      screen.getByTestId('dissemination-progress-row-session-primary'),
    ).toHaveAttribute('data-status', 'failed');
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

  it('shows export selection for multiple candidates; empty disables actions (TC-F16-005)', async () => {
    const user = userEvent.setup();
    render(
      <DisseminationDrawer
        {...defaultProps}
        sessionOutputs={[
          {
            id: 'extra-1',
            name: 'extra.xml',
            source: 'session',
            product: 'metar',
            iwxxmXml: '<extra/>',
          },
        ]}
      />,
    );

    expect(screen.getByTestId('dissemination-export-selection')).toBeInTheDocument();
    await user.click(screen.getByTestId('dissemination-clear-selection'));
    expect(screen.getByTestId('dissemination-empty-selection')).toBeInTheDocument();
    expect(screen.getByTestId('dissemination-send-button')).toBeDisabled();

    await user.click(screen.getByTestId('dissemination-select-all'));
    expect(screen.getByTestId('dissemination-send-button')).toBeDisabled(); // still need URI

    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/multi.db',
    );
    expect(screen.getByTestId('dissemination-send-button')).toBeEnabled();

    // Toggle one candidate off via checkbox (covers per-row onChange).
    await user.click(screen.getByTestId('dissemination-candidate-extra-1'));
    expect(screen.getByTestId('dissemination-send-button')).toBeEnabled();
  });

  it('expands collapsed sole-candidate selection (E18-9)', async () => {
    const user = userEvent.setup();
    render(<DisseminationDrawer {...defaultProps} />);

    expect(
      screen.queryByTestId('dissemination-export-selection'),
    ).not.toBeInTheDocument();
    await user.click(screen.getByTestId('dissemination-selection-expand'));
    expect(screen.getByTestId('dissemination-export-selection')).toBeInTheDocument();
  });

  it('continues Disseminate after one file fails (TC-F16-005)', async () => {
    const user = userEvent.setup();
    vi.mocked(global.fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          ok: false,
          connectivity_ok: false,
          diffs: [],
          detail: 'first fail',
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          ok: true,
          connectivity_ok: true,
          diffs: [],
          handle: 'h2',
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ok: true, kv_upload_key: 'kv:2' }),
      } as Response);

    render(
      <DisseminationDrawer
        {...defaultProps}
        sessionOutputs={[
          {
            id: 'extra-1',
            name: 'extra.xml',
            source: 'session',
            product: 'metar',
            iwxxmXml: '<extra/>',
          },
        ]}
      />,
    );

    await user.click(screen.getByTestId('dissemination-select-all'));
    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/multi.db',
    );
    await user.click(screen.getByTestId('dissemination-send-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-send-success')).toHaveTextContent(
        /1 file/,
      );
    });
    expect(global.fetch).toHaveBeenCalledTimes(3);
  });

  it('uses a TAC-only primary candidate and reports a failed preflight', async () => {
    const user = userEvent.setup();
    vi.mocked(global.fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ok: false,
        connectivity_ok: false,
        diffs: [],
        handle: null,
      }),
    } as Response);
    render(
      <DisseminationDrawer
        {...defaultProps}
        iwxxmXml="  "
        tacText="METAR KJFK 010000Z"
      />,
    );

    expect(screen.getByTestId('dissemination-selection-expand')).toHaveTextContent(
      '1 file selected',
    );
    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/tac.db',
    );
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-error')).toHaveTextContent(
        /1 of 1 file\(s\) failed: Preflight not green/i,
      );
    });
    expect(
      screen.getByTestId('dissemination-progress-row-session-primary'),
    ).toHaveAttribute('data-status', 'failed');
  });

  it('closes and resets via the drawer backdrop', async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    render(<DisseminationDrawer {...defaultProps} onOpenChange={onOpenChange} />);

    await user.click(screen.getByTestId('dissemination-drawer-backdrop'));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it('shows selection cap error when select-all exceeds 20 files (TC-F16-005)', async () => {
    const user = userEvent.setup();
    const manyOutputs = Array.from({ length: 21 }, (_, index) => ({
      id: `extra-${index}`,
      name: `extra-${index}.xml`,
      source: 'session' as const,
      product: 'metar',
      iwxxmXml: `<extra id="${index}"/>`,
    }));

    render(<DisseminationDrawer {...defaultProps} sessionOutputs={manyOutputs} />);

    await user.click(screen.getByTestId('dissemination-select-all'));
    expect(screen.getByTestId('dissemination-selection-cap-error')).toHaveTextContent(
      /limited to 20 files/i,
    );
  });

  it('ignores drag-drop when the file list is empty', () => {
    render(
      <DisseminationDrawer
        {...defaultProps}
        iwxxmXml={undefined}
        tacText={undefined}
      />,
    );

    const dropzone = screen.getByTestId('dissemination-dropzone');
    fireEvent.drop(dropzone, { dataTransfer: { files: [] } });
    expect(
      screen.queryByTestId('dissemination-payload-status'),
    ).not.toBeInTheDocument();
  });

  it('names dropped TAC files without extensions using drop.tac', async () => {
    const user = userEvent.setup();
    render(
      <DisseminationDrawer
        {...defaultProps}
        iwxxmXml={undefined}
        tacText={undefined}
      />,
    );

    const file = new File(['METAR KORD 010000Z ...='], '', { type: 'text/plain' });
    await user.upload(screen.getByTestId('dissemination-file-input'), file);

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-payload-status')).toHaveTextContent(
        /1 candidate/,
      );
    });
    await user.click(screen.getByTestId('dissemination-selection-expand'));
    expect(screen.getByText('drop.tac')).toBeInTheDocument();
  });

  it('names dropped XML payloads without filenames using drop.xml', async () => {
    const user = userEvent.setup();
    render(
      <DisseminationDrawer
        {...defaultProps}
        iwxxmXml={undefined}
        tacText={undefined}
      />,
    );

    const file = new File(['<iwxxm:METAR/>'], '', { type: 'text/xml' });
    await user.upload(screen.getByTestId('dissemination-file-input'), file);

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-payload-status')).toHaveTextContent(
        /1 candidate/,
      );
    });
    await user.click(screen.getByTestId('dissemination-selection-expand'));
    expect(screen.getByText('drop.xml')).toBeInTheDocument();
  });

  it('rejects null BYOC JSON before calling preflight', async () => {
    const user = userEvent.setup();
    render(<DisseminationDrawer {...defaultProps} />);

    await user.selectOptions(screen.getByTestId('dissemination-sink-chooser'), 'wis2');
    fireEvent.change(screen.getByTestId('dissemination-byoc-params'), {
      target: { value: 'null' },
    });
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    expect(screen.getByTestId('dissemination-error')).toHaveTextContent(/JSON object/i);
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('surfaces aggregate failure without per-file detail', async () => {
    const user = userEvent.setup();
    mockRunDisseminationQueue.mockImplementation(async function* () {
      yield {
        type: 'file_done',
        result: {
          candidateId: 'session-primary',
          status: 'failed',
          phase: 'preflight',
        },
      };
    });

    render(<DisseminationDrawer {...defaultProps} />);

    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/no-detail.db',
    );
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-error')).toHaveTextContent(
        /1 of 1 file\(s\) failed — see progress below/i,
      );
    });
  });

  it('uses drawer product when session output omits product', async () => {
    const user = userEvent.setup();
    vi.mocked(global.fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ok: true,
        connectivity_ok: true,
        diffs: [],
        handle: 'h-product',
      }),
    } as Response);

    render(
      <DisseminationDrawer
        {...defaultProps}
        product="taf"
        sessionOutputs={[
          {
            id: 'no-product',
            name: 'orphan.xml',
            source: 'session',
            iwxxmXml: '<taf/>',
          },
        ]}
      />,
    );

    await user.click(screen.getByTestId('dissemination-select-all'));
    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/product.db',
    );
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
    const body = JSON.parse(
      (global.fetch as unknown as { mock: { calls: [[string, { body: string }]] } })
        .mock.calls[0][1].body,
    );
    expect(body.product).toBe('taf');
  });

  it('shows generic dissemination error for non-Error queue failures', async () => {
    const user = userEvent.setup();
    mockRunDisseminationQueue.mockImplementation(() => {
      throw 'queue exploded';
    });

    render(<DisseminationDrawer {...defaultProps} />);

    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/queue.db',
    );
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-error')).toHaveTextContent(
        'Dissemination failed',
      );
    });
  });

  it('shows Error.message for Error queue failures', async () => {
    const user = userEvent.setup();
    mockRunDisseminationQueue.mockImplementation(() => {
      throw new Error('queue boom');
    });

    render(<DisseminationDrawer {...defaultProps} />);

    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/queue-err.db',
    );
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-error')).toHaveTextContent('queue boom');
    });
  });

  it('shows pending progress rows when results exist without row state', async () => {
    const user = userEvent.setup();
    mockRunDisseminationQueue.mockImplementation(async function* () {
      yield {
        type: 'file_done',
        result: {
          candidateId: 'session-primary',
          status: 'success',
          phase: 'preflight',
        },
      };
    });

    render(
      <DisseminationDrawer
        {...defaultProps}
        sessionOutputs={[
          {
            id: 'extra-1',
            name: 'extra.xml',
            source: 'session',
            product: 'metar',
            iwxxmXml: '<extra/>',
          },
        ]}
      />,
    );

    await user.click(screen.getByTestId('dissemination-select-all'));
    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/pending.db',
    );
    await user.click(screen.getByTestId('dissemination-preflight-button'));

    await waitFor(() => {
      expect(screen.getByTestId('dissemination-progress-list')).toBeInTheDocument();
    });
    expect(screen.getByTestId('dissemination-progress-row-extra-1')).toHaveAttribute(
      'data-status',
      'pending',
    );
  });

  it('parses empty BYOC params JSON as an empty object', async () => {
    const user = userEvent.setup();
    render(<DisseminationDrawer {...defaultProps} />);
    await user.selectOptions(screen.getByTestId('dissemination-sink-chooser'), 'wis2');
    fireEvent.change(screen.getByTestId('dissemination-byoc-params'), {
      target: { value: '' },
    });
    await user.click(screen.getByTestId('dissemination-preflight-button'));
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });

  it('reports failures without detail using the generic progress copy', async () => {
    const user = userEvent.setup();
    mockRunDisseminationQueue.mockImplementation(async function* () {
      yield {
        type: 'file_done',
        result: {
          candidateId: 'session-primary',
          status: 'failed',
          phase: 'send',
        },
      };
    });

    render(<DisseminationDrawer {...defaultProps} />);
    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/nodetail.db',
    );
    await user.click(screen.getByTestId('dissemination-send-button'));
    await waitFor(() => {
      expect(screen.getByTestId('dissemination-error')).toHaveTextContent(
        /see progress below/i,
      );
    });
  });

  it('covers drop/progress helper branches', async () => {
    const { dropReaderText, hasDropFiles, progressRowState } =
      await import('./DisseminationDrawer');
    expect(hasDropFiles(null)).toBe(false);
    expect(hasDropFiles(undefined)).toBe(false);
    expect(dropReaderText(null)).toBe('');
    expect(dropReaderText('hi')).toBe('hi');
    expect(progressRowState({}, 'x')).toEqual({ status: 'pending' });
    expect(progressRowState({ x: { status: 'send', detail: 'd' } }, 'x')).toEqual({
      status: 'send',
      detail: 'd',
    });
  });

  it('send path uses drawer product when candidate product is missing', async () => {
    const { resolveDisseminationProduct } = await import('./DisseminationDrawer');
    expect(resolveDisseminationProduct(undefined, 'taf')).toBe('taf');
    expect(resolveDisseminationProduct('metar', 'taf')).toBe('metar');

    const user = userEvent.setup();
    let sawMissingProduct = false;
    mockRunDisseminationQueue.mockImplementation(async function* (opts: {
      send: (c: { product?: string }, h: string) => Promise<unknown>;
      candidates: Array<{ id: string; product?: string }>;
    }) {
      for (const c of opts.candidates) {
        if (c.product === undefined) {
          sawMissingProduct = true;
        }
        await opts.send(c, 'h-fallback');
        yield {
          type: 'result' as const,
          result: {
            candidateId: c.id,
            status: 'success' as const,
          },
        };
      }
    });

    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ ok: true }),
    } as Response);

    render(
      <DisseminationDrawer
        {...defaultProps}
        product="taf"
        sessionOutputs={[
          {
            id: 'no-product-send',
            name: 'orphan.xml',
            source: 'session',
            iwxxmXml: '<taf/>',
          },
        ]}
      />,
    );

    await user.click(screen.getByTestId('dissemination-select-all'));
    await user.type(
      screen.getByTestId('dissemination-uri-input'),
      'sqlite:////tmp/send-product.db',
    );
    await user.click(screen.getByTestId('dissemination-send-button'));
    await waitFor(() => {
      expect(mockRunDisseminationQueue).toHaveBeenCalled();
    });
    expect(sawMissingProduct).toBe(true);
  });

  it('ignores drop FileList with empty first slot', () => {
    render(<DisseminationDrawer {...defaultProps} />);
    const dropzone = screen.getByTestId('dissemination-dropzone');
    fireEvent.drop(dropzone, {
      dataTransfer: {
        files: { length: 1, 0: undefined } as unknown as FileList,
      },
    });
    expect(screen.queryByText(/drop\.xml|drop\.tac/i)).not.toBeInTheDocument();
  });
});

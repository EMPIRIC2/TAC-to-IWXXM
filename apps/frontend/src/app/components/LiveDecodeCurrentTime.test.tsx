/**
 * Live decode current-time clock UI — combinatorial success / mutation / toggle.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { LiveDecodeCurrentTime } from './LiveDecodeCurrentTime';
import { LIVE_DECODE_SHOW_CURRENT_TIME_KEY } from '../../utils/liveDecodeCurrentTime';

describe('LiveDecodeCurrentTime', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });

  afterEach(() => {
    vi.useRealTimers();
    localStorage.clear();
  });

  it('shows Now label with UTC and local marker by default (success)', () => {
    const fixed = new Date('2026-11-13T20:23:00.000Z');
    render(<LiveDecodeCurrentTime now={() => fixed} timeZone="America/New_York" />);
    const clock = screen.getByTestId('live-decode-current-time');
    expect(clock.textContent).toMatch(/^Now: /);
    expect(clock.textContent).toContain('UTC');
    expect(clock.textContent).toMatch(/EST|EDT|GMT|UTC|−|-|\+/);
    expect(screen.getByTestId('live-decode-current-time-toggle')).toBeChecked();
  });

  it('hides clock when toggle turned off and persists (update mutation)', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(<LiveDecodeCurrentTime now={() => new Date('2026-11-13T12:00:00Z')} />);
    expect(screen.getByTestId('live-decode-current-time')).toBeInTheDocument();
    await user.click(screen.getByTestId('live-decode-current-time-toggle'));
    expect(screen.queryByTestId('live-decode-current-time')).not.toBeInTheDocument();
    expect(localStorage.getItem(LIVE_DECODE_SHOW_CURRENT_TIME_KEY)).toBe('false');
  });

  it('restores hidden preference on remount (read after update)', () => {
    localStorage.setItem(LIVE_DECODE_SHOW_CURRENT_TIME_KEY, 'false');
    render(<LiveDecodeCurrentTime />);
    expect(screen.getByTestId('live-decode-current-time-toggle')).not.toBeChecked();
    expect(screen.queryByTestId('live-decode-current-time')).not.toBeInTheDocument();
  });

  it('ticks at least every second while visible (create/update of label)', () => {
    let minute = 20;
    const now = () =>
      new Date(`2026-11-13T20:${String(minute).padStart(2, '0')}:00.000Z`);
    render(<LiveDecodeCurrentTime now={now} timeZone="UTC" />);
    expect(screen.getByTestId('live-decode-current-time').textContent).toContain(
      '20:20',
    );
    minute = 21;
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(screen.getByTestId('live-decode-current-time').textContent).toContain(
      '20:21',
    );
  });

  it('rejects turning clock back on only via toggle (create after delete)', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    localStorage.setItem(LIVE_DECODE_SHOW_CURRENT_TIME_KEY, 'false');
    render(
      <LiveDecodeCurrentTime
        now={() => new Date('2026-11-13T01:02:00Z')}
        timeZone="UTC"
      />,
    );
    expect(screen.queryByTestId('live-decode-current-time')).not.toBeInTheDocument();
    await user.click(screen.getByTestId('live-decode-current-time-toggle'));
    const clock = screen.getByTestId('live-decode-current-time');
    expect(clock.textContent).toContain('UTC');
    expect(clock.textContent).toContain('01:02');
    expect(localStorage.getItem(LIVE_DECODE_SHOW_CURRENT_TIME_KEY)).toBe('true');
  });
});

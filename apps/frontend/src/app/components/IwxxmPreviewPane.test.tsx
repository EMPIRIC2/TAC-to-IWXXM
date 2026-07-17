/**
 * T3.3 / TC-F10-001 — IWXXM preview pane (S013 / EV-009, F10).
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { IwxxmPreviewPane } from './IwxxmPreviewPane';

const SAMPLE_XML =
  '<?xml version="1.0"?><iwxxm:METAR><iwxxm:observation/></iwxxm:METAR>';

describe('IwxxmPreviewPane', () => {
  it('pretty-prints XML in the pane', () => {
    render(<IwxxmPreviewPane xml={SAMPLE_XML} status="passed" mode="soft-preview" />);
    const pre = screen.getByTestId('iwxxm-preview-xml');
    expect(pre.textContent).toMatch(/<iwxxm:METAR>/);
    expect(pre.textContent).toMatch(/\n/);
  });

  it('shows Soft preview — not for publish badge with plain-language soft-fail copy', () => {
    render(
      <IwxxmPreviewPane
        xml={SAMPLE_XML}
        status="soft-fail"
        mode="soft-preview"
        softFailDetail="Some groups could not be converted. Fix highlighted spans, then retry."
      />,
    );
    expect(screen.getByTestId('iwxxm-preview-badge')).toHaveTextContent(
      /Soft preview — not for publish/i,
    );
    expect(screen.queryByText(/LAYER12_SOFT_FAIL/)).not.toBeInTheDocument();
    expect(screen.getByTestId('iwxxm-preview-soft-fail')).toHaveTextContent(
      /could not be converted/i,
    );
  });

  it('shows Passed badge when preview succeeds', () => {
    render(<IwxxmPreviewPane xml={SAMPLE_XML} status="passed" mode="live" />);
    expect(screen.getByTestId('iwxxm-preview-badge')).toHaveTextContent(/^Passed$/);
  });

  it('links failed-span count to onFailedSpanFocus callback', async () => {
    const user = userEvent.setup();
    const onFocus = vi.fn();
    render(
      <IwxxmPreviewPane
        xml={SAMPLE_XML}
        status="soft-fail"
        mode="soft-preview"
        failedSpanCount={3}
        onFailedSpanFocus={onFocus}
      />,
    );
    await user.click(screen.getByTestId('iwxxm-preview-failed-count'));
    expect(onFocus).toHaveBeenCalledTimes(1);
    expect(screen.getByTestId('iwxxm-preview-failed-count')).toHaveTextContent('3');
  });

  it('shows most recent XML only (replaces prior content)', () => {
    const { rerender } = render(
      <IwxxmPreviewPane xml="<a/>" status="passed" mode="live" />,
    );
    expect(screen.getByTestId('iwxxm-preview-xml')).toHaveTextContent('<a/>');
    rerender(<IwxxmPreviewPane xml="<b/>" status="passed" mode="live" />);
    expect(screen.getByTestId('iwxxm-preview-xml')).toHaveTextContent('<b/>');
    expect(screen.getByTestId('iwxxm-preview-xml')).not.toHaveTextContent('<a/>');
  });

  it('uses responsive stacking classes (side-by-side from lg)', () => {
    const { container } = render(
      <IwxxmPreviewPane xml={SAMPLE_XML} status="passed" mode="soft-preview" />,
    );
    const root = container.querySelector('[data-testid="iwxxm-preview-pane"]');
    expect(root?.className).toMatch(/lg:/);
  });

  it('shows empty placeholder when no XML yet', () => {
    render(<IwxxmPreviewPane xml="" status="empty" mode="idle" />);
    expect(screen.getByTestId('iwxxm-preview-empty')).toBeInTheDocument();
  });
});

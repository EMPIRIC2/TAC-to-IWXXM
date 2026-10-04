/**
 * Wide Convert pane resize handles.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { LiveConvertPaneGrid } from './LiveConvertPaneGrid';

const widths: [number, number, number] = [34, 27, 39];

describe('LiveConvertPaneGrid', () => {
  it('stacks the panes when the screen is narrow', () => {
    const onWidthsChange = vi.fn();
    const { unmount } = render(
      <LiveConvertPaneGrid wide={false} widths={widths} onWidthsChange={onWidthsChange}>
        <div>TAC</div>
        <div>Decode</div>
        <div>XML</div>
      </LiveConvertPaneGrid>,
    );
    expect(screen.queryByRole('separator')).not.toBeInTheDocument();
    expect(screen.getByTestId('live-convert-panes')).toHaveAttribute(
      'data-fit',
      'roomy',
    );
    expect(screen.getByTestId('live-convert-panes').className).toContain(
      'min-h-[24rem]',
    );
    expect(screen.getByTestId('live-convert-panes').className).not.toContain('h-full');
    expect(screen.getByText('TAC')).toBeInTheDocument();
    unmount();
    render(
      <LiveConvertPaneGrid
        wide={false}
        roomy={false}
        widths={widths}
        onWidthsChange={onWidthsChange}
      >
        <div>Tight</div>
      </LiveConvertPaneGrid>,
    );
    expect(screen.getByTestId('live-convert-panes')).toHaveAttribute(
      'data-fit',
      'tight',
    );
    expect(screen.getByTestId('live-convert-panes').className).not.toContain(
      'min-h-[20rem]',
    );
  });

  it('drags using a unit width when the pane row has no measured size', () => {
    const onWidthsChange = vi.fn();
    render(
      <LiveConvertPaneGrid
        wide
        roomy={false}
        widths={widths}
        onWidthsChange={onWidthsChange}
      >
        <div>TAC</div>
        <div>Decode</div>
        <div>XML</div>
      </LiveConvertPaneGrid>,
    );
    expect(screen.getByTestId('live-convert-panes')).toHaveAttribute(
      'data-fit',
      'tight',
    );
    expect(screen.getByTestId('live-convert-panes').className).toContain('h-full');
    const first = screen.getByRole('separator', {
      name: 'Resize TAC and decode panes',
    });
    fireEvent.pointerDown(first, { clientX: 0 });
    fireEvent.pointerMove(window, { clientX: 40 });
    fireEvent.pointerUp(window);
    expect(onWidthsChange).toHaveBeenCalled();
  });

  it('nudges and drags the boundaries on a wide screen', () => {
    const onWidthsChange = vi.fn();
    vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue({
      width: 1000,
      height: 40,
      top: 0,
      left: 0,
      bottom: 40,
      right: 1000,
      x: 0,
      y: 0,
      toJSON: () => ({}),
    });
    const { unmount } = render(
      <LiveConvertPaneGrid wide widths={widths} onWidthsChange={onWidthsChange}>
        <div>TAC</div>
        <div>Decode</div>
        <div>XML</div>
      </LiveConvertPaneGrid>,
    );
    const first = screen.getByRole('separator', {
      name: 'Resize TAC and decode panes',
    });
    fireEvent.keyDown(first, { key: 'ArrowRight' });
    expect(onWidthsChange).toHaveBeenCalledWith([36, 25, 39]);
    fireEvent.keyDown(first, { key: 'Enter' });
    fireEvent.pointerDown(first, { clientX: 100 });
    fireEvent.pointerMove(window, { clientX: 150 });
    expect(onWidthsChange).toHaveBeenCalledWith([39, 22, 39]);
    fireEvent.pointerUp(window);

    const second = screen.getByRole('separator', {
      name: 'Resize decode and IWXXM panes',
    });
    fireEvent.keyDown(second, { key: 'ArrowLeft' });
    expect(onWidthsChange).toHaveBeenCalledWith([34, 25, 41]);
    fireEvent.pointerDown(second, { clientX: 10 });
    unmount();
    vi.restoreAllMocks();
  });
});

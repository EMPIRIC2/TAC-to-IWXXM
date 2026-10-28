import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { VerticalResizeHandle } from './VerticalResizeHandle';

describe('VerticalResizeHandle', () => {
  it('nudges height with arrow keys', () => {
    const onHeightChange = vi.fn();
    render(
      <VerticalResizeHandle
        height={240}
        onHeightChange={onHeightChange}
        label="Resize converter box"
      />,
    );
    const handle = screen.getByRole('separator', { name: 'Resize converter box' });
    fireEvent.keyDown(handle, { key: 'ArrowDown' });
    expect(onHeightChange).toHaveBeenCalledWith(256);
    fireEvent.keyDown(handle, { key: 'ArrowUp' });
    expect(onHeightChange).toHaveBeenCalledWith(224);
    fireEvent.keyDown(handle, { key: 'Enter' });
    expect(onHeightChange).toHaveBeenCalledTimes(2);
  });

  it('drags with pointer events and cleans up listeners on unmount', () => {
    const onHeightChange = vi.fn();
    const { unmount } = render(
      <VerticalResizeHandle
        height={240}
        onHeightChange={onHeightChange}
        label="Resize IWXXM results box"
        testId="iwxxm-vertical-resize"
      />,
    );
    const handle = screen.getByTestId('iwxxm-vertical-resize');
    fireEvent.pointerDown(handle, { clientY: 100 });
    fireEvent.pointerMove(window, { clientY: 140 });
    expect(onHeightChange).toHaveBeenCalledWith(280);
    fireEvent.pointerUp(window);
    unmount();
  });
});

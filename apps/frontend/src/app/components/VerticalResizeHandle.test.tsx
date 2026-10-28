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
  });
});

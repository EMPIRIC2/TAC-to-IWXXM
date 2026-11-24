/**
 * Drop-guard: soft-preview control off by default (FR-043 / M1).
 *
 * [Corpus: fr] epic #1688
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { softPreviewUiConfig } from '@/utils/softPreviewUi';
import { SoftPreviewControl } from './SoftPreviewControl';

describe('SoftPreviewControl (FR-043 drop)', () => {
  afterEach(() => {
    softPreviewUiConfig.enabled = false;
  });

  it('does not render the soft-preview toggle by default', () => {
    softPreviewUiConfig.enabled = false;
    render(<SoftPreviewControl checked={false} onChange={vi.fn()} />);
    expect(screen.queryByTestId('soft-preview-toggle')).not.toBeInTheDocument();
  });

  it('renders when explicitly re-enabled for harnesses', () => {
    softPreviewUiConfig.enabled = true;
    render(<SoftPreviewControl checked={false} onChange={vi.fn()} />);
    expect(screen.getByTestId('soft-preview-toggle')).toBeInTheDocument();
  });
});

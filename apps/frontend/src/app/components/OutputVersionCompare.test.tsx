/**
 * Re-convert diff between the last two stored versions.
 */

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OutputVersionCompare } from './OutputVersionCompare';
import type { OutputVersion } from '/utils/outputVersions';

const row = (xml: string): OutputVersion => ({
  at: 1,
  tac: 'METAR',
  xml,
  conversionProfile: 'conversion · ICAO_2025',
  decodingProfile: 'decoding · ICAO_2025',
});

describe('OutputVersionCompare', () => {
  it('renders nothing until two versions exist', () => {
    const { container } = render(<OutputVersionCompare versions={[row('<a/>')]} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('lists added and removed lines and an unchanged result', () => {
    const { rerender } = render(
      <OutputVersionCompare versions={[row('<a/>\n<b/>'), row('<a/>\n<c/>')]} />,
    );
    expect(screen.getByTestId('output-version-compare')).toHaveTextContent(
      'Version 2 against version 1',
    );
    expect(screen.getByText('Removed')).toBeInTheDocument();
    expect(screen.getByText('<b/>')).toBeInTheDocument();
    expect(screen.getByText('Added')).toBeInTheDocument();
    expect(screen.getByText('<c/>')).toBeInTheDocument();

    rerender(
      <OutputVersionCompare
        versions={[
          { ...row('<same/>'), conversionProfile: '' },
          { ...row('<same/>'), conversionProfile: '' },
        ]}
      />,
    );
    expect(screen.getByText('No XML line changes.')).toBeInTheDocument();
    expect(screen.queryByText(/Conversion profile/)).not.toBeInTheDocument();
  });
});

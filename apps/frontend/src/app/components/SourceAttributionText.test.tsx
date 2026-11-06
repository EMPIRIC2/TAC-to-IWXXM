/**
 * Shared Source attribution renderer (Issue details + other Source lines).
 */
import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SourceAttributionText } from './SourceAttributionText';

describe('SourceAttributionText', () => {
  it('renders plain text without a link', () => {
    render(<SourceAttributionText value="WMO code list" />);
    expect(screen.getByText('WMO code list')).toBeInTheDocument();
    expect(screen.queryByRole('link')).not.toBeInTheDocument();
  });

  it('links http(s) URLs and keeps the label', () => {
    render(
      <SourceAttributionText value="icao-eur-doc-014 - https://www.icao.int/doc.pdf" />,
    );
    expect(screen.getByText(/icao-eur-doc-014/)).toBeInTheDocument();
    const link = screen.getByRole('link', {
      name: 'https://www.icao.int/doc.pdf',
    });
    expect(link).toHaveAttribute('href', 'https://www.icao.int/doc.pdf');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    expect(link.className).toMatch(/break-all/);
  });

  it('scrubs planning ids from the attribution line before split', () => {
    render(<SourceAttributionText value="WMO list EV-048 — https://example.com/a" />);
    expect(screen.queryByText(/EV-048/)).not.toBeInTheDocument();
    expect(
      screen.getByRole('link', { name: 'https://example.com/a' }),
    ).toBeInTheDocument();
  });
});

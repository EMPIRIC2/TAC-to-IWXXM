/**
 * TC-F38-003 — IWXXM preview stays glossary-excluded.
 */

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { IwxxmPreviewPane } from '../IwxxmPreviewPane';

const SAMPLE_XML =
  '<?xml version="1.0"?><iwxxm:METAR><iwxxm:observation/></iwxxm:METAR>';

describe('glossary editor exclusion (TC-F38-003)', () => {
  it('marks IWXXM preview as glossary-excluded', () => {
    render(<IwxxmPreviewPane xml={SAMPLE_XML} status="passed" mode="live" />);
    expect(screen.getByTestId('iwxxm-preview-pane')).toHaveAttribute(
      'data-glossary-exclude',
      'true',
    );
  });
});

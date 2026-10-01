/**
 * Convert progress strip labels.
 */

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LiveConvertStatusStrip } from './LiveConvertStatusStrip';

describe('LiveConvertStatusStrip', () => {
  it('names each stage in text', () => {
    render(
      <LiveConvertStatusStrip
        hasTac
        decodeReady={false}
        decodeLoading
        previewState="incomplete"
        lintStatus="failed"
        schemaStatus="not run"
        schematronStatus="not run"
      />,
    );
    const strip = screen.getByTestId('convert-status-strip');
    expect(strip).toHaveTextContent('TAC entered');
    expect(strip).toHaveTextContent('TAC lint: failed');
    expect(strip).toHaveTextContent('Decode running');
    expect(strip).toHaveTextContent('Preview incomplete');
    expect(strip).toHaveTextContent('XML schema: not run');
    expect(strip).toHaveTextContent('Schematron: not run');
  });

  it('reports an empty TAC, a ready decode, and a current preview', () => {
    render(
      <LiveConvertStatusStrip
        hasTac={false}
        decodeReady
        decodeLoading={false}
        previewState="current"
        lintStatus="passed"
        schemaStatus="passed"
        schematronStatus="failed"
      />,
    );
    const strip = screen.getByTestId('convert-status-strip');
    expect(strip).toHaveTextContent('TAC empty');
    expect(strip).toHaveTextContent('TAC lint: passed');
    expect(strip).toHaveTextContent('Decode ready');
    expect(strip).toHaveTextContent('Preview up to date');
    expect(strip).toHaveTextContent('XML schema: passed');
    expect(strip).toHaveTextContent('Schematron: failed');
  });

  it('reports preview waiting before XML exists', () => {
    render(
      <LiveConvertStatusStrip
        hasTac
        decodeReady={false}
        decodeLoading={false}
        previewState="waiting"
        lintStatus="waiting"
        schemaStatus="not run"
        schematronStatus="passed"
      />,
    );
    expect(screen.getByTestId('convert-status-strip')).toHaveTextContent(
      'Preview waiting',
    );
    expect(screen.getByTestId('convert-status-strip')).toHaveTextContent(
      'Decode waiting',
    );
    expect(screen.getByTestId('convert-status-strip')).toHaveTextContent(
      'TAC lint: waiting',
    );
    expect(screen.getByTestId('convert-status-strip')).toHaveTextContent(
      'Schematron: passed',
    );
  });
});

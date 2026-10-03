/**
 * Convert progress strip labels.
 */

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LiveConvertStatusStrip } from './LiveConvertStatusStrip';

function tones(): Record<string, string> {
  const strip = screen.getByTestId('convert-status-strip');
  return Object.fromEntries(
    [...strip.querySelectorAll('li')].map((item) => [
      item.textContent ?? '',
      item.getAttribute('data-tone') ?? '',
    ]),
  );
}

describe('LiveConvertStatusStrip', () => {
  it('names each check and points at the text area', () => {
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
    expect(strip).toHaveTextContent('text area below');
    expect(strip).toHaveTextContent('Report: entered in the text area below');
    expect(strip).toHaveTextContent('TAC lint: failed');
    expect(strip).toHaveTextContent('Decode: running');
    expect(strip).toHaveTextContent('Preview: incomplete');
    expect(strip).toHaveTextContent(
      'XML schema: not run yet. It runs when you validate.',
    );
    expect(strip).toHaveTextContent(
      'Schematron: not run yet. It runs when you validate.',
    );
    const byTone = tones();
    expect(byTone['TAC lint: failed']).toBe('problem');
    expect(byTone['Preview: incomplete']).toBe('caution');
    expect(byTone['XML schema: not run yet. It runs when you validate.']).toBe('idle');
    expect(byTone['Report: entered in the text area below']).toBe('ready');
  });

  it('reports an empty text area, a ready decode, and a current preview', () => {
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
    expect(strip).toHaveTextContent('Report: the text area below is empty');
    expect(strip).toHaveTextContent('TAC lint: passed');
    expect(strip).toHaveTextContent('Decode: ready');
    expect(strip).toHaveTextContent('Preview: up to date');
    expect(strip).toHaveTextContent('XML schema: passed');
    expect(strip).toHaveTextContent('Schematron: failed');
    const byTone = tones();
    expect(byTone['TAC lint: passed']).toBe('ready');
    expect(byTone['Schematron: failed']).toBe('problem');
    expect(byTone['XML schema: passed']).toBe('ready');
  });

  it('reports checks that have not run yet', () => {
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
    const strip = screen.getByTestId('convert-status-strip');
    expect(strip).toHaveTextContent('Preview: not run yet');
    expect(strip).toHaveTextContent('Decode: not run yet');
    expect(strip).toHaveTextContent('TAC lint: not run yet');
    expect(strip).toHaveTextContent('Schematron: passed');
    expect(tones()['TAC lint: not run yet']).toBe('idle');
  });

  it('shows lint warnings and a schema failure as different from a check in progress', () => {
    render(
      <LiveConvertStatusStrip
        hasTac
        decodeReady={false}
        decodeLoading={false}
        previewState="waiting"
        lintStatus="warnings"
        schemaStatus="failed"
        schematronStatus="not run"
      />,
    );
    const byTone = tones();
    expect(byTone['TAC lint: warnings']).toBe('caution');
    expect(byTone['XML schema: failed']).toBe('problem');
    expect(byTone['Schematron: not run yet. It runs when you validate.']).toBe('idle');
  });

  it('shows an info-level TAC note separately from a warning', () => {
    render(
      <LiveConvertStatusStrip
        hasTac
        decodeReady={false}
        decodeLoading={false}
        previewState="waiting"
        lintStatus="notes"
        schemaStatus="not run"
        schematronStatus="not run"
      />,
    );
    expect(tones()['TAC lint: notes']).toBe('caution');
  });

  it('says when TAC lint is still checking the report', () => {
    render(
      <LiveConvertStatusStrip
        hasTac
        decodeReady={false}
        decodeLoading={false}
        previewState="waiting"
        lintStatus="running"
        schemaStatus="not run"
        schematronStatus="not run"
      />,
    );
    expect(tones()['TAC lint: checking the report']).toBe('idle');
  });
});

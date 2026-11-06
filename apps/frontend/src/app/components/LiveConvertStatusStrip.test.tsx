/**
 * Convert progress strip labels.
 */

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LiveConvertStatusStrip } from './LiveConvertStatusStrip';

/**
 *
 */
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
    expect(strip).toHaveTextContent('TAC input: failed');
    expect(strip).toHaveTextContent('Decode: running');
    expect(strip).toHaveTextContent('Preview: incomplete');
    expect(strip).toHaveTextContent('XML schema: not run yet');
    expect(strip).toHaveTextContent('Schematron: not run yet');
    expect(strip).not.toHaveTextContent('It runs when you validate.');
    const byTone = tones();
    expect(byTone['TAC input: failed']).toBe('problem');
    expect(byTone['Preview: incomplete']).toBe('caution');
    expect(byTone['XML schema: not run yet']).toBe('idle');
    expect(screen.getByText('XML schema: not run yet')).toHaveAttribute(
      'title',
      'It runs when you validate.',
    );
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
    expect(strip).toHaveTextContent('TAC input: clear');
    expect(strip).toHaveTextContent('Decode: ready');
    expect(strip).toHaveTextContent('Preview: up to date');
    expect(strip).toHaveTextContent('XML schema: passed');
    expect(strip).toHaveTextContent('Schematron: failed');
    const byTone = tones();
    expect(byTone['TAC input: clear']).toBe('ready');
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
    expect(strip).toHaveTextContent('TAC input: not checked yet');
    expect(strip).toHaveTextContent('Schematron: passed');
    expect(tones()['TAC input: not checked yet']).toBe('idle');
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
    expect(byTone['warnings on TAC input']).toBe('caution');
    expect(byTone['XML schema: failed']).toBe('problem');
    expect(byTone['Schematron: not run yet']).toBe('idle');
    expect(screen.getByText('Schematron: not run yet')).toHaveAttribute(
      'title',
      'It runs when you validate.',
    );
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
    expect(tones()['notes on TAC input']).toBe('idle');
  });

  it('says when TAC input is still being checked', () => {
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
    expect(tones()['checking TAC input']).toBe('idle');
  });
});

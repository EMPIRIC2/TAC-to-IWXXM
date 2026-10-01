import { describe, expect, it } from 'vitest';
import {
  errorLayerNames,
  layerKey,
  lintIssueCounts,
  outputLayerStatus,
  strictConvertRan,
  tacLintLayerStatus,
} from './checkLayers';

describe('checkLayers', () => {
  it('folds layer ids to letters', () => {
    expect(layerKey(' XML_SCHEMA ')).toBe('xmlschema');
    expect(layerKey('schematron')).toBe('schematron');
  });

  it('detects a finished strict convert', () => {
    expect(
      strictConvertRan({
        strict: false,
        softPreview: false,
        convertedCount: 1,
        status: 'idle',
      }),
    ).toBe(false);
    expect(
      strictConvertRan({
        strict: true,
        softPreview: true,
        convertedCount: 1,
        status: 'idle',
      }),
    ).toBe(false);
    expect(
      strictConvertRan({
        strict: true,
        softPreview: false,
        convertedCount: 0,
        status: 'idle',
      }),
    ).toBe(false);
    expect(
      strictConvertRan({
        strict: true,
        softPreview: false,
        convertedCount: 1,
        status: 'error',
      }),
    ).toBe(false);
    expect(
      strictConvertRan({
        strict: true,
        softPreview: false,
        convertedCount: 2,
        status: 'send_error',
      }),
    ).toBe(true);
  });

  it('keeps error layers and skips warnings and blanks', () => {
    expect(errorLayerNames(null)).toEqual([]);
    expect(errorLayerNames({})).toEqual([]);
    expect(errorLayerNames({ issues: null })).toEqual([]);
    expect(
      errorLayerNames({
        issues: [
          { layer: '', severity: 'error' },
          { layer: 'xml_schema', severity: 'warning' },
          { severity: 'error' },
          { layer: 'schematron' },
          { layer: 'xml_schema', severity: 'error' },
        ],
      }),
    ).toEqual(['schematron', 'xml_schema']);
  });

  it('marks schema and Schematron from validate, issues, or a strict convert', () => {
    expect(outputLayerStatus('schema', null, [])).toBe('not run');
    expect(
      outputLayerStatus('schematron', { layers_passed: null, layers_failed: null }, []),
    ).toBe('not run');
    expect(outputLayerStatus('schema', { layers_passed: ['XML_SCHEMA'] }, [])).toBe(
      'passed',
    );
    expect(outputLayerStatus('schematron', { layers_passed: ['XML_SCHEMA'] }, [])).toBe(
      'not run',
    );
    expect(outputLayerStatus('schematron', { layers_failed: ['SCHEMATRON'] }, [])).toBe(
      'failed',
    );
    expect(
      outputLayerStatus(
        'schema',
        { layers_passed: ['xml_schema'], layers_failed: [] },
        ['xml_schema'],
      ),
    ).toBe('failed');
    expect(outputLayerStatus('schema', null, [])).toBe('not run');
    expect(outputLayerStatus('schematron', null, [])).toBe('not run');
  });

  it('counts error issues', () => {
    expect(lintIssueCounts([])).toEqual({ errorCount: 0, issueCount: 0 });
    expect(
      lintIssueCounts([{ severity: 'error' }, { severity: 'warning' }, {}]),
    ).toEqual({ errorCount: 1, issueCount: 3 });
  });

  it('describes live TAC lint', () => {
    expect(
      tacLintLayerStatus({
        hasTac: false,
        loading: true,
        errorCount: 1,
        issueCount: 1,
      }),
    ).toBe('waiting');
    expect(
      tacLintLayerStatus({
        hasTac: true,
        loading: false,
        errorCount: 1,
        issueCount: 2,
      }),
    ).toBe('failed');
    expect(
      tacLintLayerStatus({
        hasTac: true,
        loading: false,
        errorCount: 0,
        issueCount: 1,
      }),
    ).toBe('warnings');
    expect(
      tacLintLayerStatus({
        hasTac: true,
        loading: true,
        errorCount: 0,
        issueCount: 0,
      }),
    ).toBe('running');
    expect(
      tacLintLayerStatus({
        hasTac: true,
        loading: false,
        errorCount: 0,
        issueCount: 0,
      }),
    ).toBe('passed');
  });
});

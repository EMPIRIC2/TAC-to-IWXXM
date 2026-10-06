/**
 * Live Convert trace helpers: lint wording, incomplete preview, XML line hits.
 */

import { describe, expect, it } from 'vitest';
import {
  editorOffsetFromFormField,
  formFieldSpanInEditor,
  lintErrorCount,
  lintSummaryLabel,
  lintWarningCount,
  previewIsIncomplete,
  readGroupTrace,
  spansWithSelection,
  xmlLinesForElement,
  xmlLinesForGroup,
  xmlLinesForSelection,
  xmlLinesMatchingToken,
} from './liveConvertTrace';

describe('liveConvertTrace', () => {
  it('counts errors and warnings and writes them into the summary', () => {
    const issues = [
      { severity: 'error' },
      { severity: 'warning' },
      { severity: 'warn' },
      { severity: 'info' },
    ];
    expect(lintErrorCount(issues)).toBe(1);
    expect(lintWarningCount(issues)).toBe(2);
    expect(lintSummaryLabel(issues)).toBe('1 error in the TAC');
    expect(lintSummaryLabel([{ severity: 'error' }, { severity: 'error' }])).toBe(
      '2 errors in the TAC',
    );
    expect(lintSummaryLabel([{ severity: 'warning' }])).toBe('TAC lint: 1 warning');
    expect(lintSummaryLabel([{ severity: 'warn' }, { severity: 'warning' }])).toBe(
      'TAC lint: 2 warnings',
    );
    expect(lintSummaryLabel([{ severity: 'info' }])).toBe('TAC lint: 1 note');
    expect(lintSummaryLabel([{ severity: 'info' }, { severity: 'info' }])).toBe(
      'TAC lint: 2 notes',
    );
    expect(lintSummaryLabel([])).toBe('TAC lint: passed');
  });

  it('marks the preview incomplete when TAC still has a problem', () => {
    expect(previewIsIncomplete(0, 0, 0)).toBe(false);
    expect(previewIsIncomplete(1, 0, 0)).toBe(true);
    expect(previewIsIncomplete(0, 1, 0)).toBe(true);
    expect(previewIsIncomplete(0, 0, 1)).toBe(true);
  });

  it('highlights converter elements for a wind group that is not copied into the XML', () => {
    const xml = [
      '<iwxxm:METAR>',
      '  <iwxxm:aerodrome>TTPP</iwxxm:aerodrome>',
      '  <iwxxm:windSpeed uom="[kn_i]">12</iwxxm:windSpeed>',
      '</iwxxm:METAR>',
    ].join('\n');
    expect(xmlLinesForGroup(xml, '09012KT')).toEqual([3]);
    expect(xmlLinesForGroup(xml, 'TTPP')).toEqual([2]);
    expect(xmlLinesForGroup(xml, '')).toEqual([]);
    expect(xmlLinesForGroup('   ', '09012KT')).toEqual([]);
    expect(xmlLinesForGroup('<note>09012KT</note>', '09012KT')).toEqual([1]);
    expect(xmlLinesForGroup('<note>XX</note>', 'XX')).toEqual([1]);
  });

  it('finds preview lines that contain the selected group', () => {
    const xml = '<root>\n  <station>TTPP</station>\n</root>';
    expect(xmlLinesMatchingToken(xml, 'TTPP')).toEqual([2]);
    expect(xmlLinesMatchingToken(xml, '   ')).toEqual([]);
    expect(xmlLinesMatchingToken('   ', 'TTPP')).toEqual([]);
    expect(xmlLinesMatchingToken(xml, 'ZZ')).toEqual([]);
    expect(xmlLinesMatchingToken('<a>-</a>\n<b>-</b>', '-')).toEqual([]);
    expect(xmlLinesMatchingToken('<a>S</a>\n<b>S</b>', 'S')).toEqual([]);
  });

  it('replaces overlapping issue marks with the selection', () => {
    const issues = [
      { start: 0, end: 5, message: 'lint' },
      { start: 6, end: 10, message: 'other' },
    ];
    expect(spansWithSelection(issues, null)).toEqual(issues);
    expect(spansWithSelection(issues, { start: 4, end: 4, code: 'X' })).toEqual(issues);
    const painted = spansWithSelection(issues, { start: 0, end: 5, code: 'METAR' });
    expect(painted).toEqual([
      { start: 6, end: 10, message: 'other' },
      {
        start: 0,
        end: 5,
        code: 'METAR',
        message: 'Selected group',
        severity: 'selected',
      },
    ]);
  });

  it('keeps only complete pairing rows', () => {
    expect(readGroupTrace({})).toEqual([]);
    expect(readGroupTrace({ group_trace: null })).toEqual([]);
    expect(
      readGroupTrace({
        group_trace: [
          null,
          'nope',
          {
            start: 1,
            end: 2,
            token: 'X',
            element: 'qnh',
            occurrence: 0,
            scope: 'nope',
          },
          {
            start: 0,
            end: 5,
            token: 'METAR',
            element: 'METAR',
            occurrence: 0,
            scope: 'line',
          },
          {
            start: 6,
            end: 10,
            token: 'FEW250',
            element: 'CloudLayer',
            occurrence: 0,
            scope: 'block',
          },
        ],
      }),
    ).toEqual([
      {
        start: 0,
        end: 5,
        token: 'METAR',
        element: 'METAR',
        occurrence: 0,
        scope: 'line',
      },
      {
        start: 6,
        end: 10,
        token: 'FEW250',
        element: 'CloudLayer',
        occurrence: 0,
        scope: 'block',
      },
    ]);
  });

  it('marks one element occurrence, including a dotted name and a self-closing tag', () => {
    const xml = [
      '<iwxxm:cloud>',
      '<iwxxm:CloudLayer>FEW</iwxxm:CloudLayer>',
      '<iwxxm:CloudLayer>SCT</iwxxm:CloudLayer>',
      '<iwxxm:trendForecast/>',
      '<a.b>kept</a.b>',
      '<axb>other</axb>',
      '<iwxxm:open>',
    ].join('\n');
    expect(xmlLinesForElement('', 'CloudLayer', 0, 'line')).toEqual([]);
    expect(xmlLinesForElement(xml, '', 0, 'line')).toEqual([]);
    expect(xmlLinesForElement(xml, 'CloudLayer', -1, 'line')).toEqual([]);
    expect(xmlLinesForElement(xml, 'CloudLayer', 1, 'line')).toEqual([3]);
    expect(xmlLinesForElement(xml, 'CloudLayer', 0, 'block')).toEqual([2]);
    expect(xmlLinesForElement(xml, 'trendForecast', 0, 'block')).toEqual([4]);
    expect(xmlLinesForElement(xml, 'a.b', 0, 'line')).toEqual([5]);
    expect(xmlLinesForElement(xml, 'missing', 0, 'block')).toEqual([]);
    expect(xmlLinesForElement(xml, 'open', 0, 'block')).toEqual([7]);
    expect(
      xmlLinesForElement(
        '<iwxxm:CloudLayer/><iwxxm:CloudLayer/>',
        'CloudLayer',
        1,
        'line',
      ),
    ).toEqual([1]);
  });

  it('maps multipart line breaks back onto the editor text', () => {
    const editor = 'WSPSZ1 NZKL 050806\nNZZO SIGMET 2 VALID 050811/051211 NZKL-\nNZZO';
    const wire = editor.replace(/\n/g, '\r\n');
    const token = 'NZZO';
    const wireStart = wire.lastIndexOf(token);
    expect(editorOffsetFromFormField(editor, wireStart)).toBe(
      editor.lastIndexOf(token),
    );
    expect(editorOffsetFromFormField(editor, wireStart + token.length)).toBe(
      editor.lastIndexOf(token) + token.length,
    );
    expect(editorOffsetFromFormField(editor, 0)).toBe(0);
    expect(editorOffsetFromFormField('AB\nC', 4)).toBe(3);
    expect(editorOffsetFromFormField('AB\r\nC', 4)).toBe(4);
    expect(editorOffsetFromFormField('AB\rC', 4)).toBe(3);
    expect(formFieldSpanInEditor('  AB\nC', 'AB\nC', 0, 4)).toEqual({
      start: 2,
      end: 5,
    });
    expect(formFieldSpanInEditor('ABC', '', 0, 1)).toEqual({ start: 0, end: 0 });
    expect(formFieldSpanInEditor('ABC', 'ZZ', 0, 1)).toEqual({ start: 0, end: 1 });
  });

  it('uses the pairing for the selected offsets and falls back otherwise', () => {
    const xml =
      '<iwxxm:surfaceWind>\n  <iwxxm:windSpeed>12</iwxxm:windSpeed>\n</iwxxm:surfaceWind>';
    const traces = [
      {
        start: 10,
        end: 17,
        token: '18004KT',
        element: 'surfaceWind',
        occurrence: 0,
        scope: 'block' as const,
      },
      {
        start: 20,
        end: 24,
        token: 'ZZ',
        element: 'notInXml',
        occurrence: 0,
        scope: 'line' as const,
      },
    ];
    expect(xmlLinesForSelection(xml, '18004KT', undefined, 17, traces)).toEqual([2]);
    expect(xmlLinesForSelection(xml, '18004KT', 10, 17, traces)).toEqual([1, 2, 3]);
    expect(xmlLinesForSelection(xml, 'ZZ', 20, 24, traces)).toEqual([]);
  });
});

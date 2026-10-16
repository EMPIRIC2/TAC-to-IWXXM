import { describe, expect, it } from 'vitest';

import {
  DO_NOT_PUBLISH_LABEL,
  PAGE_TITLE,
  RESULT_STATUS_ATTENTION,
  RESULT_STATUS_NOTES,
  RESULT_STATUS_VALID,
  assessConvertedFile,
  assessResultCard,
  isErrorSeverity,
  xmlBlocksPublish,
} from './resultCard';

describe('result card status', () => {
  it('names the page TAC to IWXXM', () => {
    expect(PAGE_TITLE).toBe('TAC to IWXXM');
    expect(PAGE_TITLE).not.toBe('METAR-2-IWXXM');
  });

  it('treats missing and error severity as errors, and info or warnings as notes', () => {
    expect(isErrorSeverity(undefined)).toBe(true);
    expect(isErrorSeverity(null)).toBe(true);
    expect(isErrorSeverity('')).toBe(true);
    expect(isErrorSeverity(' ERROR ')).toBe(true);
    expect(isErrorSeverity('critical')).toBe(true);
    expect(isErrorSeverity('info')).toBe(false);
    expect(isErrorSeverity(' Warning ')).toBe(false);
    expect(isErrorSeverity('warn')).toBe(false);
    expect(isErrorSeverity('note')).toBe(false);
  });

  it('blocks publish for blank or malformed XML and allows a well-formed document', () => {
    expect(xmlBlocksPublish(undefined)).toBe(false);
    expect(xmlBlocksPublish(null)).toBe(false);
    expect(xmlBlocksPublish('   ')).toBe(true);
    expect(xmlBlocksPublish('<iwxxm')).toBe(true);
    expect(xmlBlocksPublish('<iwxxm>ok</iwxxm>')).toBe(false);
  });

  it('is valid when the XML is well-formed and nothing was reported', () => {
    const card = assessResultCard({ xml: '<iwxxm>ok</iwxxm>', ok: true });
    expect(card.statusLabel).toBe(RESULT_STATUS_VALID);
    expect(card.publishBlocked).toBe(false);
    expect(card.errors).toEqual([]);
    expect(card.notes).toEqual([]);
  });

  it('is valid with notes when only informational issues are present', () => {
    const card = assessResultCard({
      xml: '<iwxxm>ok</iwxxm>',
      errors: ['  '],
      issues: [
        { severity: 'info', message: 'Remark stays in the decode', code: 'RMK_NOTE' },
        { severity: 'warning', message: '  ' },
        { severity: 'info', message: null },
        { severity: 'warning', message: 'Check the cloud group', code: '   ' },
      ],
    });
    expect(card.statusLabel).toBe(RESULT_STATUS_NOTES);
    expect(card.publishBlocked).toBe(false);
    expect(card.errors).toEqual([]);
    expect(card.notes).toEqual([
      { message: 'Remark stays in the decode', code: 'RMK_NOTE' },
      { message: 'Check the cloud group' },
    ]);
  });

  it('says needs attention and blocks publish when an error or invalid XML is present', () => {
    const fromError = assessResultCard({
      xml: '<iwxxm>ok</iwxxm>',
      ok: true,
      errors: ['XML is not valid'],
      issues: [
        { severity: 'error', message: 'Schema check failed', code: 'XML_SCHEMA' },
        { message: 'Missing severity still blocks publish' },
        { severity: 'info', message: 'A note stays with notes', code: 'NOTE' },
      ],
    });
    expect(fromError.statusLabel).toBe(RESULT_STATUS_ATTENTION);
    expect(fromError.publishBlocked).toBe(true);
    expect(fromError.errors.map((line) => line.message)).toEqual([
      'XML is not valid',
      'Schema check failed',
      'Missing severity still blocks publish',
    ]);
    expect(fromError.notes).toEqual([
      { message: 'A note stays with notes', code: 'NOTE' },
    ]);

    const fromFlag = assessResultCard({ xml: '<iwxxm>ok</iwxxm>', ok: false });
    expect(fromFlag.publishBlocked).toBe(true);
    expect(fromFlag.statusLabel).toBe(RESULT_STATUS_ATTENTION);

    const fromXml = assessResultCard({ xml: '<iwxxm', ok: true });
    expect(fromXml.publishBlocked).toBe(true);
    expect(DO_NOT_PUBLISH_LABEL).toBe('Do not publish');
  });

  it('assesses a stored file, including a card with no saved issues', () => {
    expect(
      assessConvertedFile({
        convertedContent: '<iwxxm>ok</iwxxm>',
      }).statusLabel,
    ).toBe(RESULT_STATUS_VALID);

    expect(
      assessConvertedFile({
        convertedContent: '<iwxxm>ok</iwxxm>',
        resultCard: {
          ok: true,
          issues: [{ severity: 'info', message: 'Kept as a note' }],
        },
      }).statusLabel,
    ).toBe(RESULT_STATUS_NOTES);
  });
});

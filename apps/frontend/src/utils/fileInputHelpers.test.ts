/**
 * EV-080 — helpers extracted for FileConverter / DisseminationDrawer branch fills.
 */
import { describe, expect, it, vi } from 'vitest';
import {
  applyFocusedQueueContent,
  applyWebkitDirectoryAttrs,
  ariaInvalidFromError,
  caExtensionBundleAvailableFromStatus,
  clearFileInputValue,
  coalescePreviewXml,
  firstDropFile,
  firstTacForArchive,
  focusedValidateErrorMessage,
  forEachFileInList,
  hydratedResultName,
  isDropZoneActivateKey,
  iwxxmValidationErrorMessage,
  lintIssueCount,
  queueResultOriginalName,
  resolveDisseminationProduct,
  shouldIgnoreWorkQueueKey,
} from './fileInputHelpers';

describe('fileInputHelpers', () => {
  it('applyWebkitDirectoryAttrs no-ops on null and sets attrs on input', () => {
    applyWebkitDirectoryAttrs(null);
    const el = document.createElement('input');
    applyWebkitDirectoryAttrs(el);
    expect(el.getAttribute('webkitdirectory')).toBe('');
    expect(el.getAttribute('directory')).toBe('');
  });

  it('clearFileInputValue no-ops on null and clears value', () => {
    clearFileInputValue(null);
    const el = document.createElement('input');
    el.value = 'x';
    clearFileInputValue(el);
    expect(el.value).toBe('');
  });

  it('forEachFileInList skips sparse slots', () => {
    const visited: string[] = [];
    const files = {
      length: 2,
      0: undefined,
      1: { name: 'ok.tac' } as File,
    } as unknown as FileList;
    forEachFileInList(files, (file) => {
      visited.push(file.name);
    });
    expect(visited).toEqual(['ok.tac']);
  });

  it('firstDropFile returns null for empty slot', () => {
    const empty = { length: 1, 0: undefined } as unknown as FileList;
    expect(firstDropFile(empty)).toBeNull();
    const filled = {
      length: 1,
      0: { name: 'a.xml' } as File,
    } as unknown as FileList;
    expect(firstDropFile(filled)?.name).toBe('a.xml');
  });

  it('resolveDisseminationProduct prefers candidate then fallback', () => {
    expect(resolveDisseminationProduct('taf', 'metar')).toBe('taf');
    expect(resolveDisseminationProduct(undefined, 'metar')).toBe('metar');
  });

  it('caExtensionBundleAvailableFromStatus covers missing pins', () => {
    expect(caExtensionBundleAvailableFromStatus({})).toBeNull();
    expect(caExtensionBundleAvailableFromStatus({ profile_pins: {} })).toBeNull();
    expect(
      caExtensionBundleAvailableFromStatus({
        profile_pins: { ca_eccc: {} },
      }),
    ).toBeNull();
    expect(
      caExtensionBundleAvailableFromStatus({
        profile_pins: { ca_eccc: { extension_bundle_available: false } },
      }),
    ).toBe(false);
    expect(
      caExtensionBundleAvailableFromStatus({
        profile_pins: { ca_eccc: { extension_bundle_available: true } },
      }),
    ).toBe(true);
  });

  it('ariaInvalidFromError is true only when error is set', () => {
    expect(ariaInvalidFromError(null)).toBeUndefined();
    expect(ariaInvalidFromError(undefined)).toBeUndefined();
    expect(ariaInvalidFromError('')).toBeUndefined();
    expect(ariaInvalidFromError('bad')).toBe(true);
  });

  it('forEachFileInList can return promises', async () => {
    const spy = vi.fn(async () => undefined);
    const files = {
      length: 1,
      0: { name: 'a.tac' } as File,
    } as unknown as FileList;
    await Promise.all(forEachFileInList(files, spy));
    expect(spy).toHaveBeenCalledOnce();
  });

  it('covers FileConverter name/preview/archive helpers', () => {
    expect(hydratedResultName('named', 0)).toBe('named');
    expect(hydratedResultName(undefined, 2)).toBe('result-3');
    expect(queueResultOriginalName('a.tac', 'r')).toBe('a.tac');
    expect(queueResultOriginalName(undefined, 'r')).toBe('r');
    expect(queueResultOriginalName(undefined, undefined)).toBe('unknown');
    expect(coalescePreviewXml('<x/>')).toBe('<x/>');
    expect(coalescePreviewXml(undefined)).toBe('');
    expect(iwxxmValidationErrorMessage(new Error('boom'))).toBe('boom');
    expect(iwxxmValidationErrorMessage('x')).toBe('IWXXM validation failed');
    expect(lintIssueCount([{ a: 1 }, { b: 2 }])).toBe(2);
    expect(lintIssueCount(undefined)).toBe(0);
    expect(lintIssueCount(null)).toBe(0);
    expect(firstTacForArchive('kept', 'other')).toBe('kept');
    expect(firstTacForArchive(null, 'fallback')).toBe('fallback');
    expect(isDropZoneActivateKey('Enter')).toBe(true);
    expect(isDropZoneActivateKey(' ')).toBe(true);
    expect(isDropZoneActivateKey('a')).toBe(false);
    expect(shouldIgnoreWorkQueueKey(0)).toBe(true);
    expect(shouldIgnoreWorkQueueKey(2)).toBe(false);
    expect(focusedValidateErrorMessage(new Error('x'), 'a.tac')).toBe('x');
    expect(focusedValidateErrorMessage('nope', 'a.tac')).toBe(
      'Validate failed for a.tac',
    );
    const setContent = vi.fn();
    applyFocusedQueueContent(undefined, setContent);
    expect(setContent).not.toHaveBeenCalled();
    applyFocusedQueueContent({ content: 'METAR' }, setContent);
    expect(setContent).toHaveBeenCalledWith('METAR');
  });
});

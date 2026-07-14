/**
 * T4.2 — Span normalize / decoration helpers for live workbench (UJ-017).
 */

import { afterEach, describe, expect, it } from 'vitest';
import { EditorState } from '@codemirror/state';
import { EditorView } from '@codemirror/view';
import {
  buildSpanDecorations,
  normalizeTacSpans,
  setTacSpansEffect,
  tacSpanExtensions,
} from './tacEditorSpans';

describe('normalizeTacSpans', () => {
  it('clamps to document length and drops empty ranges', () => {
    const out = normalizeTacSpans(
      [
        { start: -2, end: 4, message: 'a' },
        { start: 10, end: 10, message: 'empty' },
        { start: 8, end: 100, message: 'clamp' },
      ],
      12,
    );
    expect(out).toEqual([
      { start: 0, end: 4, message: 'a' },
      { start: 8, end: 12, message: 'clamp' },
    ]);
  });

  it('sorts by start then end', () => {
    const out = normalizeTacSpans(
      [
        { start: 5, end: 8 },
        { start: 1, end: 3 },
        { start: 1, end: 2 },
      ],
      20,
    );
    expect(out.map((s) => [s.start, s.end])).toEqual([
      [1, 2],
      [1, 3],
      [5, 8],
    ]);
  });
});

describe('buildSpanDecorations', () => {
  it('creates a decoration set sized to the span count', () => {
    const set = buildSpanDecorations([
      { start: 0, end: 5, message: 'x' },
      { start: 6, end: 9, message: 'y' },
    ]);
    expect(set.size).toBe(2);
  });
});

describe('tacSpanExtensions', () => {
  let view: EditorView | null = null;

  afterEach(() => {
    view?.destroy();
    view = null;
  });

  it('mounts CodeMirror extensions and applies span effects', () => {
    const parent = document.createElement('div');
    document.body.appendChild(parent);
    const state = EditorState.create({
      doc: 'METAR KJFK',
      extensions: tacSpanExtensions(),
    });
    view = new EditorView({ state, parent });
    view.dispatch({
      effects: setTacSpansEffect.of([{ start: 0, end: 5, code: 'T', message: 'type' }]),
    });
    expect(view.state.doc.toString()).toBe('METAR KJFK');
    // document edit triggers span field update path
    view.dispatch({
      changes: { from: 10, to: 10, insert: ' X' },
    });
    expect(view.state.doc.toString()).toContain('X');
  });
});

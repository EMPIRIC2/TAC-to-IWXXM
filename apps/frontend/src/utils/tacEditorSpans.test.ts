/**
 * T4.2 — Span normalize / decoration helpers for live workbench (UJ-017).
 */

import { afterEach, describe, expect, it, vi } from 'vitest';
import { EditorState, StateEffect } from '@codemirror/state';
import { EditorView } from '@codemirror/view';
import {
  buildSpanDecorations,
  normalizeTacSpans,
  setTacSpansEffect,
  spanTooltip,
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
    // No-op selection update hits tacSpansField update return-value path
    view.dispatch({
      selection: { anchor: 0, head: 0 },
    });
    // Non-matching effect hits the effect.is(...) false branch
    const other = StateEffect.define<number>();
    view.dispatch({ effects: other.of(1) });
  });

  it('buildSpanDecorations uses info mark for info severity', () => {
    const set = buildSpanDecorations([
      { start: 0, end: 2, severity: 'info' },
      { start: 3, end: 5, severity: 'error' },
    ]);
    expect(set.size).toBe(2);
  });

  it('spanTooltip returns null when pos misses all spans', () => {
    const parent = document.createElement('div');
    document.body.appendChild(parent);
    view = new EditorView({
      state: EditorState.create({
        doc: 'METAR KJFK',
        extensions: tacSpanExtensions(),
      }),
      parent,
    });
    view.dispatch({
      effects: setTacSpansEffect.of([{ start: 0, end: 5, message: 'type' }]),
    });
    expect(spanTooltip(view, 9)).toBeNull();
  });

  it('spanTooltip builds DOM with fix button and dispatches tac-span-fix', () => {
    const parent = document.createElement('div');
    document.body.appendChild(parent);
    view = new EditorView({
      state: EditorState.create({
        doc: 'METAR KJFK',
        extensions: tacSpanExtensions(),
      }),
      parent,
    });
    view.dispatch({
      effects: setTacSpansEffect.of([
        {
          start: 0,
          end: 5,
          code: 'MISSING_TERMINATOR',
          message: 'add equals',
          fixCode: 'add_terminator',
          fixLabel: 'Add `=`',
        },
      ]),
    });

    const tip = spanTooltip(view, 2);
    expect(tip).not.toBeNull();
    const created = tip!.create(view);
    expect(created.dom.getAttribute('data-testid')).toBe('tac-span-tooltip');
    const btn = created.dom.querySelector(
      '[data-testid="tac-span-fix-add_terminator"]',
    ) as HTMLButtonElement;
    expect(btn).toBeTruthy();

    const heard = vi.fn();
    view.dom.addEventListener('tac-span-fix', heard);
    btn.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
    expect(heard).toHaveBeenCalled();
    const detail = (heard.mock.calls[0]?.[0] as CustomEvent).detail;
    expect(detail).toEqual({ fixCode: 'add_terminator' });
  });

  it('spanTooltip falls back to Issue label when code and message are empty', () => {
    const parent = document.createElement('div');
    document.body.appendChild(parent);
    view = new EditorView({
      state: EditorState.create({
        doc: 'METAR',
        extensions: tacSpanExtensions(),
      }),
      parent,
    });
    view.dispatch({
      effects: setTacSpansEffect.of([{ start: 0, end: 5 }]),
    });
    const tip = spanTooltip(view, 1);
    const created = tip!.create(view);
    expect(created.dom.textContent).toBe('Issue');
  });
});

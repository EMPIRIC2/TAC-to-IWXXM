/**
 * T3.5 / TC-F10-002 §4 — editor affordance for terminator hint (S013 / EV-009).
 */

import { describe, expect, it } from 'vitest';
import { EditorState } from '@codemirror/state';
import { EditorView } from '@codemirror/view';
import {
  setTacSpansEffect,
  tacSpanExtensions,
  type TacSpanMark,
} from './tacEditorSpans';

describe('tacEditorSpans terminator affordance', () => {
  it('marks info-severity spans with cm-tac-issue-info class', () => {
    const parent = document.createElement('div');
    document.body.appendChild(parent);
    const view = new EditorView({
      state: EditorState.create({
        doc: 'METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034',
        extensions: tacSpanExtensions(),
      }),
      parent,
    });
    const spans: TacSpanMark[] = [
      {
        start: 48,
        end: 49,
        code: 'MISSING_TERMINATOR',
        message: "Reports in bulletins end with '=' — add it before publishing",
        severity: 'info',
        fixCode: 'add_terminator',
        fixLabel: 'Add `=`',
      },
    ];
    view.dispatch({ effects: setTacSpansEffect.of(spans) });
    const info = parent.querySelector('.cm-tac-issue-info');
    expect(info).toBeTruthy();
    view.destroy();
    parent.remove();
  });
});

/**
 * Map lint/decode issue offsets to CodeMirror decorations (UJ-017 / #694).
 */

import {
  Decoration,
  EditorView,
  hoverTooltip,
  type DecorationSet,
  type Tooltip,
} from '@codemirror/view';
import { StateEffect, StateField, type Extension, type Range } from '@codemirror/state';

export interface TacSpanMark {
  start: number;
  end: number;
  message?: string;
  severity?: string;
  code?: string;
}

export const setTacSpansEffect = StateEffect.define<TacSpanMark[]>();

const issueMark = Decoration.mark({
  class: 'cm-tac-issue',
});

/**
 * Clamp and sort spans for a document length.
 *
 * @param spans - Raw start/end marks
 * @param docLength - Editor document length
 * @returns Valid ranges only
 */
export function normalizeTacSpans(
  spans: TacSpanMark[],
  docLength: number,
): TacSpanMark[] {
  return spans
    .map((s) => ({
      ...s,
      start: Math.max(0, Math.min(s.start, docLength)),
      end: Math.max(0, Math.min(s.end, docLength)),
    }))
    .filter((s) => s.end > s.start)
    .sort((a, b) => a.start - b.start || a.end - b.end);
}

/**
 * Build decoration ranges for issue spans.
 *
 * @param spans - Normalized spans
 * @returns CodeMirror decoration set
 */
export function buildSpanDecorations(spans: TacSpanMark[]): DecorationSet {
  const ranges: Range<Decoration>[] = [];
  for (const span of spans) {
    ranges.push(issueMark.range(span.start, span.end));
  }
  return Decoration.set(ranges, true);
}

const tacSpansField = StateField.define<TacSpanMark[]>({
  create: () => [],
  update(value, tr) {
    for (const effect of tr.effects) {
      if (effect.is(setTacSpansEffect)) {
        return normalizeTacSpans(effect.value, tr.state.doc.length);
      }
    }
    if (tr.docChanged) {
      return normalizeTacSpans(value, tr.state.doc.length);
    }
    return value;
  },
});

const tacSpansDecorations = StateField.define<DecorationSet>({
  create: () => Decoration.none,
  update(_value, tr) {
    const spans = tr.state.field(tacSpansField);
    return buildSpanDecorations(spans);
  },
  provide: (field) => EditorView.decorations.from(field),
});

// StateField update always rebuilds from tacSpansField (doc/effects land there first).

function spanTooltip(view: EditorView, pos: number): Tooltip | null {
  const spans = view.state.field(tacSpansField);
  const hit = spans.find((s) => pos >= s.start && pos < s.end);
  if (!hit) {
    return null;
  }
  const text = [hit.code, hit.message].filter(Boolean).join(': ') || 'Issue';
  return {
    pos: hit.start,
    end: hit.end,
    above: true,
    create() {
      const dom = document.createElement('div');
      dom.className = 'cm-tac-issue-tooltip';
      dom.textContent = text;
      dom.setAttribute('data-testid', 'tac-span-tooltip');
      return { dom };
    },
  };
}

/**
 * CodeMirror extensions: span field, decorations, hover tooltips, theme.
 *
 * @returns Extension bundle for TacEditor
 */
export function tacSpanExtensions(): Extension[] {
  return [
    tacSpansField,
    tacSpansDecorations,
    hoverTooltip(spanTooltip, { hoverTime: 200 }),
    EditorView.baseTheme({
      '.cm-tac-issue': {
        backgroundColor: 'rgba(251, 191, 36, 0.35)',
        borderBottom: '2px wavy #d97706',
      },
      '.cm-tac-issue-tooltip': {
        padding: '4px 8px',
        borderRadius: '4px',
        backgroundColor: '#1f2937',
        color: '#f9fafb',
        fontSize: '12px',
        maxWidth: '280px',
      },
    }),
  ];
}

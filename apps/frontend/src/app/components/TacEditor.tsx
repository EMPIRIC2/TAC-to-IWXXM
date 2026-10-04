/* eslint-disable react-refresh/only-export-components */
/**
 * CodeMirror 6 TAC editor shell for the F7 operator workbench (S011 / #702/#694).
 */

import { useEffect, useRef } from 'react';
import { EditorView, basicSetup } from 'codemirror';
import { EditorState } from '@codemirror/state';
import {
  setTacSpansEffect,
  tacSpanExtensions,
  type TacSpanMark,
} from '/utils/tacEditorSpans';

/**
 * Type `FailedSpanMark`.
 * @example
 * const _ = true;
 */
export interface FailedSpanMark {
  start: number;
  end: number;
  code?: string;
  message?: string;
}

/**
 * Type `TacEditorProps`.
 * @example
 * const _ = true;
 */
export interface TacEditorProps {
  id?: string;
  value: string;
  onChange: (value: string) => void;
  readOnly?: boolean;
  placeholder?: string;
  'aria-label'?: string;
  className?: string;
  /** Soft-preview / Failed-TAC spans — marks editor chrome when non-empty (UJ-016). */
  failedSpans?: FailedSpanMark[];
  /** Live lint/decode issue spans for highlight + hover (UJ-017). */
  issueSpans?: TacSpanMark[];
  /** Quick-fix from span tooltip (F10 — e.g. add_terminator). */
  onSpanFix?: (fixCode: string) => void;
  /** Move the caret to this offset when a lint issue is chosen. */
  focusOffset?: number | null;
  /** Called with pasted report text. Typing does not call this. */
  onReportLoaded?: (text: string) => void;
}

/**
 * Sync controlled value into an existing CodeMirror view (no-op when unmounted).
 * @example
 * const _ = true;
 */
export function syncTacEditorValue(view: EditorView | null, value: string): void {
  if (!view) {
    return;
  }
  const current = view.state.doc.toString();
  if (current !== value) {
    view.dispatch({
      changes: { from: 0, to: current.length, insert: value },
    });
  }
}

/**
 * Toggle contentEditable for read-only mode (no-op when unmounted).
 * @example
 * const _ = true;
 */
export function syncTacEditorReadOnly(
  view: EditorView | null,
  readOnly: boolean,
): void {
  if (!view) {
    return;
  }
  view.contentDOM.contentEditable = readOnly ? 'false' : 'true';
}

/**
 * Keep a11y id/label in sync when props change (no-op when unmounted).
 * @example
 * const _ = true;
 */
export function syncTacEditorA11y(
  view: EditorView | null,
  ariaLabel: string,
  id: string,
): void {
  if (!view) {
    return;
  }
  view.contentDOM.setAttribute('aria-label', ariaLabel);
  view.contentDOM.id = id;
}

/**
 * Push issue span decorations (no-op when unmounted).
 * @example
 * const _ = true;
 */
export function syncTacEditorIssueSpans(
  view: EditorView | null,
  issueSpans: TacSpanMark[],
): void {
  if (!view) {
    return;
  }
  view.dispatch({ effects: setTacSpansEffect.of(issueSpans) });
}

/**
 * Scroll the editor to a lint-issue offset.
 *
 * @param view - Mounted CodeMirror view, or null before mount
 * @param offset - Character offset, or null when no issue is selected
 * @example
 * const _ = true;
 */
export function scrollTacEditorTo(
  view: EditorView | null,
  offset: number | null | undefined,
): void {
  if (!view || offset == null) return;
  const pos = Math.max(0, Math.min(offset, view.state.doc.length));
  view.dispatch({
    selection: { anchor: pos },
    effects: EditorView.scrollIntoView(pos, { y: 'center' }),
  });
}

/**
 * Handle bubbled ``tac-span-fix`` events from span tooltips.
 * @example
 * const _ = true;
 */
export function handleTacSpanFixEvent(
  event: Event,
  onSpanFix: ((fixCode: string) => void) | undefined,
): void {
  const detail = (event as CustomEvent<{ fixCode?: string }>).detail;
  if (detail?.fixCode) {
    onSpanFix?.(detail.fixCode);
  }
}

/**
 * Mount CodeMirror when a host element exists; no-op when missing.
 * @example
 * const _ = true;
 */
export function mountTacEditorView(
  parent: HTMLElement | null,
  factory: (parent: HTMLElement) => { destroy: () => void },
): (() => void) | undefined {
  if (!parent) {
    return undefined;
  }
  const view = factory(parent);
  return () => {
    view.destroy();
  };
}

/**
 * Attach ``tac-span-fix`` listener on the editor chrome root.
 * @example
 * const _ = true;
 */
export function attachTacSpanFixListener(
  inner: HTMLElement | null,
  handler: (event: Event) => void,
): (() => void) | undefined {
  const root = inner?.parentElement ?? null;
  if (!root) {
    return undefined;
  }
  root.addEventListener('tac-span-fix', handler);
  return () => {
    root.removeEventListener('tac-span-fix', handler);
  };
}

/**
 * Controlled CodeMirror 6 editor for TAC text.
 *
 * @param props.value - Current TAC text
 * @param props.onChange - Called when the document changes
 * @param props.readOnly - When true, editing is disabled
 * @param props.failedSpans - Optional soft-preview failure spans
 * @param props.issueSpans - Optional live lint spans
 * @param props.onReportLoaded - Called when a report is pasted
 * @example
 * const _ = true;
 */
export function TacEditor({
  id = 'manual-input',
  value,
  onChange,
  readOnly = false,
  placeholder = '',
  'aria-label': ariaLabel = 'Enter TAC data manually',
  className = '',
  failedSpans = [],
  issueSpans = [],
  onSpanFix,
  focusOffset = null,
  onReportLoaded,
}: TacEditorProps) {
  const parentRef = useRef<HTMLDivElement | null>(null);
  const viewRef = useRef<EditorView | null>(null);
  const onChangeRef = useRef(onChange);
  const onSpanFixRef = useRef(onSpanFix);
  const onReportLoadedRef = useRef(onReportLoaded);
  const hasFailedTac = failedSpans.length > 0;

  useEffect(() => {
    onChangeRef.current = onChange;
  }, [onChange]);

  useEffect(() => {
    onSpanFixRef.current = onSpanFix;
  }, [onSpanFix]);

  useEffect(() => {
    onReportLoadedRef.current = onReportLoaded;
  }, [onReportLoaded]);

  useEffect(() => {
    return mountTacEditorView(parentRef.current, (parent) => {
      const extensions = [
        basicSetup,
        EditorView.lineWrapping,
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            onChangeRef.current(update.state.doc.toString());
          }
        }),
        EditorState.readOnly.of(readOnly),
        EditorView.editable.of(!readOnly),
        EditorView.contentAttributes.of({
          'aria-label': ariaLabel,
          id,
        }),
        EditorView.theme({
          '&': { height: '100%', minHeight: '11rem', fontSize: '0.875rem' },
          '.cm-scroller': { overflow: 'auto' },
          '.cm-content': {
            fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
          },
        }),
        ...tacSpanExtensions(),
      ];

      const state = EditorState.create({
        doc: value,
        extensions,
      });
      const view = new EditorView({ state, parent });
      viewRef.current = view;
      const onPaste = (event: Event) => {
        const clipboard = (event as ClipboardEvent).clipboardData;
        const text = clipboard?.getData('text') ?? '';
        if (text.trim()) {
          onReportLoadedRef.current?.(text);
        }
      };
      view.dom.addEventListener('paste', onPaste);

      if (issueSpans.length > 0) {
        view.dispatch({ effects: setTacSpansEffect.of(issueSpans) });
      }

      return {
        destroy: () => {
          view.dom.removeEventListener('paste', onPaste);
          view.destroy();
          viewRef.current = null;
        },
      };
    });
    // Mount once; value/readOnly/spans synced below.
    // eslint-disable-next-line react-hooks/exhaustive-deps -- intentional mount-only
  }, []);

  useEffect(() => {
    syncTacEditorValue(viewRef.current, value);
  }, [value]);

  useEffect(() => {
    syncTacEditorReadOnly(viewRef.current, readOnly);
  }, [readOnly]);

  // Mount-once CodeMirror keeps initial contentAttributes; sync a11y label when
  // FileConverter switches modes (e.g. TAC → Validate IWXXM / UJ-058 live).
  useEffect(() => {
    syncTacEditorA11y(viewRef.current, ariaLabel, id);
  }, [ariaLabel, id]);

  useEffect(() => {
    syncTacEditorIssueSpans(viewRef.current, issueSpans);
  }, [issueSpans]);

  useEffect(() => {
    scrollTacEditorTo(viewRef.current, focusOffset);
  }, [focusOffset]);

  useEffect(() => {
    return attachTacSpanFixListener(parentRef.current, (event) => {
      handleTacSpanFixEvent(event, onSpanFixRef.current);
    });
  }, []);

  return (
    <div
      className={`flex min-h-0 flex-1 flex-col overflow-hidden rounded-md border bg-white dark:bg-gray-800 ${
        hasFailedTac
          ? 'border-rose-400 dark:border-rose-600'
          : 'border-gray-300 dark:border-gray-700'
      } ${className}`}
      data-testid="tac-editor"
      data-placeholder={placeholder}
      data-issue-span-count={issueSpans.length}
      {...(hasFailedTac ? { 'data-failed-tac': 'true' } : {})}
    >
      <div ref={parentRef} className="min-h-0 flex-1" />
    </div>
  );
}

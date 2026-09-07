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

export interface FailedSpanMark {
  start: number;
  end: number;
  code?: string;
  message?: string;
}

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
}

/** Sync controlled value into an existing CodeMirror view (no-op when unmounted). */
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

/** Toggle contentEditable for read-only mode (no-op when unmounted). */
export function syncTacEditorReadOnly(
  view: EditorView | null,
  readOnly: boolean,
): void {
  if (!view) {
    return;
  }
  view.contentDOM.contentEditable = readOnly ? 'false' : 'true';
}

/** Keep a11y id/label in sync when props change (no-op when unmounted). */
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

/** Push issue span decorations (no-op when unmounted). */
export function syncTacEditorIssueSpans(
  view: EditorView | null,
  issueSpans: TacSpanMark[],
): void {
  if (!view) {
    return;
  }
  view.dispatch({ effects: setTacSpansEffect.of(issueSpans) });
}

/** Handle bubbled ``tac-span-fix`` events from span tooltips. */
export function handleTacSpanFixEvent(
  event: Event,
  onSpanFix: ((fixCode: string) => void) | undefined,
): void {
  const detail = (event as CustomEvent<{ fixCode?: string }>).detail;
  if (detail?.fixCode) {
    onSpanFix?.(detail.fixCode);
  }
}

/** Mount CodeMirror when a host element exists; no-op when missing. */
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

/** Attach ``tac-span-fix`` listener on the editor chrome root. */
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
}: TacEditorProps) {
  const parentRef = useRef<HTMLDivElement | null>(null);
  const viewRef = useRef<EditorView | null>(null);
  const onChangeRef = useRef(onChange);
  const onSpanFixRef = useRef(onSpanFix);
  const hasFailedTac = failedSpans.length > 0;

  useEffect(() => {
    onChangeRef.current = onChange;
  }, [onChange]);

  useEffect(() => {
    onSpanFixRef.current = onSpanFix;
  }, [onSpanFix]);

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
          '&': { minHeight: '120px', fontSize: '0.875rem' },
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

      if (issueSpans.length > 0) {
        view.dispatch({ effects: setTacSpansEffect.of(issueSpans) });
      }

      return {
        destroy: () => {
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
    return attachTacSpanFixListener(parentRef.current, (event) => {
      handleTacSpanFixEvent(event, onSpanFixRef.current);
    });
  }, []);

  return (
    <div
      className={`overflow-hidden rounded-md border bg-white dark:bg-gray-800 ${
        hasFailedTac
          ? 'border-rose-400 dark:border-rose-600'
          : 'border-gray-300 dark:border-gray-700'
      } ${className}`}
      data-testid="tac-editor"
      data-placeholder={placeholder}
      data-issue-span-count={issueSpans.length}
      {...(hasFailedTac ? { 'data-failed-tac': 'true' } : {})}
    >
      <div ref={parentRef} />
    </div>
  );
}

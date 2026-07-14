/**
 * CodeMirror 6 TAC editor shell for the F7 operator workbench (S011 / #702).
 */

import { useEffect, useRef } from 'react';
import { EditorView, basicSetup } from 'codemirror';
import { EditorState } from '@codemirror/state';

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
}

/**
 * Controlled CodeMirror 6 editor for TAC text.
 *
 * @param props.value - Current TAC text
 * @param props.onChange - Called when the document changes
 * @param props.readOnly - When true, editing is disabled
 * @param props.failedSpans - Optional soft-preview failure spans
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
}: TacEditorProps) {
  const parentRef = useRef<HTMLDivElement | null>(null);
  const viewRef = useRef<EditorView | null>(null);
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;
  const hasFailedTac = failedSpans.length > 0;

  useEffect(() => {
    if (!parentRef.current) {
      return;
    }

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
        '.cm-content': { fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace' },
      }),
    ];

    const state = EditorState.create({
      doc: value,
      extensions,
    });
    const view = new EditorView({ state, parent: parentRef.current });
    viewRef.current = view;

    return () => {
      view.destroy();
      viewRef.current = null;
    };
    // Mount once; value/readOnly synced below.
    // eslint-disable-next-line react-hooks/exhaustive-deps -- intentional mount-only
  }, []);

  useEffect(() => {
    const view = viewRef.current;
    if (!view) {
      return;
    }
    const current = view.state.doc.toString();
    if (current !== value) {
      view.dispatch({
        changes: { from: 0, to: current.length, insert: value },
      });
    }
  }, [value]);

  useEffect(() => {
    const view = viewRef.current;
    if (!view) {
      return;
    }
    view.dispatch({
      effects: [
        // reconfigure readOnly via compartment would be cleaner; recreate attrs via facet update
      ],
    });
    // Toggle editable DOM attribute for accessibility
    view.contentDOM.contentEditable = readOnly ? 'false' : 'true';
  }, [readOnly]);

  return (
    <div
      className={`overflow-hidden rounded-md border bg-white dark:bg-gray-800 ${
        hasFailedTac
          ? 'border-rose-400 dark:border-rose-600'
          : 'border-gray-300 dark:border-gray-700'
      } ${className}`}
      data-testid="tac-editor"
      data-placeholder={placeholder}
      {...(hasFailedTac ? { 'data-failed-tac': 'true' } : {})}
    >
      <div ref={parentRef} />
    </div>
  );
}

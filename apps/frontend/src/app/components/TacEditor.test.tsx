/**
 * TacEditor — CodeMirror host + span sync / fix events (EV-080 coverage).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { useState } from 'react';

type UpdateListener = (update: {
  docChanged: boolean;
  state: { doc: { toString: () => string } };
}) => void;

const editorMocks = vi.hoisted(() => {
  let updateListener: UpdateListener | null = null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let lastView: any = null;

  class FakeEditorView {
    static lineWrapping = {};
    static updateListener = {
      of: (fn: UpdateListener) => {
        updateListener = fn;
        return { __updateListener: fn };
      },
    };
    static editable = { of: () => ({}) };
    static contentAttributes = { of: () => ({}) };
    static theme = () => ({});
    static decorations = { from: () => ({}) };

    state: {
      doc: { toString: () => string; length: number };
    };
    contentDOM: HTMLElement;
    dom: HTMLElement;
    private docText: string;

    constructor(config?: { parent?: HTMLElement | null; state?: { doc?: string } }) {
      this.docText = typeof config?.state?.doc === 'string' ? config.state.doc : '';
      this.state = {
        doc: {
          toString: () => this.docText,
          length: this.docText.length,
        },
      };
      this.contentDOM = document.createElement('div');
      this.contentDOM.contentEditable = 'true';
      this.contentDOM.setAttribute('aria-label', 'Enter TAC data manually');
      this.contentDOM.id = 'manual-input';
      this.dom = document.createElement('div');
      this.dom.appendChild(this.contentDOM);
      config?.parent?.appendChild(this.dom);
      // Capture instance for assertions; FakeEditorView is the mock under test.
      // eslint-disable-next-line @typescript-eslint/no-this-alias -- test harness stores view
      lastView = this;
    }

    dispatch(spec?: {
      changes?: { from: number; to: number; insert: string };
      effects?: unknown;
    }) {
      if (spec?.changes) {
        this.docText = spec.changes.insert;
        this.state = {
          doc: {
            toString: () => this.docText,
            length: this.docText.length,
          },
        };
        updateListener?.({
          docChanged: true,
          state: this.state,
        });
      }
    }

    destroy() {
      lastView = null;
    }
  }

  return {
    FakeEditorView,
    getLastView: () => lastView,
    getUpdateListener: () => updateListener,
    reset: () => {
      updateListener = null;
      lastView = null;
    },
  };
});

vi.mock('codemirror', () => ({
  EditorView: editorMocks.FakeEditorView,
  basicSetup: [],
}));

vi.mock('@codemirror/state', () => ({
  EditorState: {
    create: (cfg: { doc?: string }) => ({ doc: cfg.doc ?? '' }),
    readOnly: { of: () => ({}) },
  },
  StateEffect: { define: () => ({ of: (v: unknown) => v }) },
  StateField: {
    define: () => ({}),
  },
}));

vi.mock('/utils/tacEditorSpans', () => ({
  setTacSpansEffect: { of: (v: unknown) => v },
  tacSpanExtensions: () => [],
}));

import {
  TacEditor,
  syncTacEditorValue,
  syncTacEditorReadOnly,
  syncTacEditorA11y,
  syncTacEditorIssueSpans,
  handleTacSpanFixEvent,
  mountTacEditorView,
  attachTacSpanFixListener,
} from './TacEditor';

describe('TacEditor', () => {
  beforeEach(() => {
    editorMocks.reset();
  });

  it('renders the CodeMirror host container', () => {
    render(
      <TacEditor
        value="METAR KJFK="
        onChange={() => undefined}
        aria-label="TAC editor"
      />,
    );
    expect(screen.getByTestId('tac-editor')).toBeInTheDocument();
  });

  it('exposes issue span count for live workbench highlights', () => {
    render(
      <TacEditor
        value="METAR KJFK="
        onChange={() => undefined}
        issueSpans={[{ start: 0, end: 5, message: 'type' }]}
      />,
    );
    expect(screen.getByTestId('tac-editor')).toHaveAttribute(
      'data-issue-span-count',
      '1',
    );
  });

  it('marks failed-tac chrome when failedSpans are present', () => {
    render(
      <TacEditor
        value="METAR"
        onChange={() => undefined}
        failedSpans={[{ start: 0, end: 5, message: 'fail' }]}
      />,
    );
    expect(screen.getByTestId('tac-editor')).toHaveAttribute('data-failed-tac', 'true');
  });

  it('syncs contentDOM aria-label when the prop changes (UJ-058 / EV-057)', () => {
    function Harness() {
      const [label, setLabel] = useState('Enter METAR data manually');
      return (
        <div>
          <button type="button" onClick={() => setLabel('Enter IWXXM XML manually')}>
            switch-validate
          </button>
          <TacEditor value="<root/>" onChange={() => undefined} aria-label={label} />
        </div>
      );
    }

    render(<Harness />);
    expect(screen.getByLabelText('Enter METAR data manually')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'switch-validate' }));
    expect(screen.getByLabelText('Enter IWXXM XML manually')).toBeInTheDocument();
  });

  it('forwards doc changes via onChange and ignores non-doc updates', () => {
    const onChange = vi.fn();
    render(<TacEditor value="ABC" onChange={onChange} />);
    const view = editorMocks.getLastView();
    expect(view).toBeTruthy();
    act(() => {
      view!.dispatch({ changes: { from: 0, to: 3, insert: 'XYZ' } });
    });
    expect(onChange).toHaveBeenCalledWith('XYZ');
    const listener = editorMocks.getUpdateListener();
    listener?.({
      docChanged: false,
      state: { doc: { toString: () => 'XYZ' } },
    });
    expect(onChange).toHaveBeenCalledTimes(1);
  });

  it('syncs external value into the editor', () => {
    const { rerender } = render(<TacEditor value="one" onChange={() => undefined} />);
    rerender(<TacEditor value="two" onChange={() => undefined} />);
    const view = editorMocks.getLastView();
    expect(view?.state.doc.toString()).toBe('two');
  });

  it('toggles contentEditable when readOnly changes', () => {
    const { rerender } = render(
      <TacEditor value="x" onChange={() => undefined} readOnly={false} />,
    );
    expect(editorMocks.getLastView()?.contentDOM.contentEditable).toBe('true');
    rerender(<TacEditor value="x" onChange={() => undefined} readOnly />);
    expect(editorMocks.getLastView()?.contentDOM.contentEditable).toBe('false');
  });

  it('dispatches issue span effects when issueSpans change', () => {
    const { rerender } = render(
      <TacEditor value="METAR" onChange={() => undefined} issueSpans={[]} />,
    );
    const view = editorMocks.getLastView();
    const dispatchSpy = vi.spyOn(view!, 'dispatch');
    rerender(
      <TacEditor
        value="METAR"
        onChange={() => undefined}
        issueSpans={[{ start: 0, end: 3, message: 'm' }]}
      />,
    );
    expect(dispatchSpy).toHaveBeenCalled();
  });

  it('invokes onSpanFix when tac-span-fix bubbles from the editor root', () => {
    const onSpanFix = vi.fn();
    render(
      <TacEditor value="METAR" onChange={() => undefined} onSpanFix={onSpanFix} />,
    );
    fireEvent(
      screen.getByTestId('tac-editor'),
      new CustomEvent('tac-span-fix', {
        bubbles: true,
        detail: { fixCode: 'add_terminator' },
      }),
    );
    expect(onSpanFix).toHaveBeenCalledWith('add_terminator');
  });

  it('ignores tac-span-fix events without a fixCode', () => {
    const onSpanFix = vi.fn();
    render(
      <TacEditor value="METAR" onChange={() => undefined} onSpanFix={onSpanFix} />,
    );
    fireEvent(
      screen.getByTestId('tac-editor'),
      new CustomEvent('tac-span-fix', { bubbles: true, detail: {} }),
    );
    expect(onSpanFix).not.toHaveBeenCalled();
  });

  it('sync helpers no-op when view is null and apply when present', () => {
    syncTacEditorValue(null, 'x');
    syncTacEditorReadOnly(null, true);
    syncTacEditorA11y(null, 'a', 'id');
    syncTacEditorIssueSpans(null, []);
    handleTacSpanFixEvent(new CustomEvent('tac-span-fix', { detail: {} }), vi.fn());

    const onFix = vi.fn();
    handleTacSpanFixEvent(
      new CustomEvent('tac-span-fix', { detail: { fixCode: 'add_terminator' } }),
      onFix,
    );
    expect(onFix).toHaveBeenCalledWith('add_terminator');

    render(<TacEditor value="same" onChange={() => undefined} />);
    const view = editorMocks.getLastView();
    syncTacEditorValue(view, 'same');
    syncTacEditorReadOnly(view, true);
    syncTacEditorA11y(view, 'lbl', 'nid');
    syncTacEditorIssueSpans(view, [{ start: 0, end: 1 }]);
    expect(view.contentDOM.contentEditable).toBe('false');
    expect(view.contentDOM.getAttribute('aria-label')).toBe('lbl');
  });

  it('mountTacEditorView and attachTacSpanFixListener handle missing hosts', () => {
    expect(
      mountTacEditorView(null, () => ({ destroy: () => undefined })),
    ).toBeUndefined();
    expect(attachTacSpanFixListener(null, () => undefined)).toBeUndefined();

    const host = document.createElement('div');
    const destroy = vi.fn();
    const cleanup = mountTacEditorView(host, () => ({ destroy }));
    cleanup?.();
    expect(destroy).toHaveBeenCalled();

    const inner = document.createElement('div');
    const outer = document.createElement('div');
    outer.appendChild(inner);
    const handler = vi.fn();
    const detach = attachTacSpanFixListener(inner, handler);
    outer.dispatchEvent(new CustomEvent('tac-span-fix', { bubbles: true }));
    expect(handler).toHaveBeenCalled();
    detach?.();
  });
});

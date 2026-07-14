/**
 * T2.7 smoke — TacEditor mounts a CodeMirror host.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

vi.mock('codemirror', () => {
  class FakeEditorView {
    static lineWrapping = {};
    static updateListener = { of: () => ({}) };
    static editable = { of: () => ({}) };
    static contentAttributes = { of: () => ({}) };
    static theme = () => ({});
    state = { doc: { toString: () => '', length: 0 } };
    contentDOM = { contentEditable: 'true' };
    constructor() {
      /* no-op for unit smoke */
    }
    dispatch() {
      /* no-op */
    }
    destroy() {
      /* no-op */
    }
  }
  return { EditorView: FakeEditorView, basicSetup: [] };
});

vi.mock('@codemirror/state', () => ({
  EditorState: {
    create: () => ({}),
    readOnly: { of: () => ({}) },
  },
}));

import { TacEditor } from './TacEditor';

describe('TacEditor', () => {
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
});

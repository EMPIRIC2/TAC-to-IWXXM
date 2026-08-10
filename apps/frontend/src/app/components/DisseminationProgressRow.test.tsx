/**
 * T3.3 — DisseminationProgressRow Vitest (E18-10/13/14).
 */

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

import { DisseminationProgressRow } from './DisseminationProgressRow';

const mockUseReducedMotion = vi.hoisted(() => vi.fn(() => false));

vi.mock('motion/react', async (importOriginal) => {
  const actual = await importOriginal<typeof import('motion/react')>();
  return {
    ...actual,
    useReducedMotion: mockUseReducedMotion,
  };
});

describe('DisseminationProgressRow', () => {
  it('shows mail graphic while in-flight and hides under reduced motion', () => {
    const { rerender } = render(
      <DisseminationProgressRow
        candidateId="a"
        name="a.xml"
        status="send"
        forceReducedMotion={false}
      />,
    );
    expect(screen.getByTestId('dissemination-progress-graphic-a')).toBeInTheDocument();
    expect(
      screen.getByTestId('dissemination-progress-mail-anim-a'),
    ).toBeInTheDocument();

    rerender(
      <DisseminationProgressRow
        candidateId="a"
        name="a.xml"
        status="send"
        forceReducedMotion
      />,
    );
    expect(
      screen.queryByTestId('dissemination-progress-graphic-a'),
    ).not.toBeInTheDocument();
    expect(screen.getByTestId('dissemination-progress-text-a')).toBeInTheDocument();
  });

  it('shows green check on success and red X on fail', () => {
    const { rerender } = render(
      <DisseminationProgressRow
        candidateId="a"
        name="a.xml"
        status="success"
        forceReducedMotion={false}
      />,
    );
    expect(screen.getByTestId('dissemination-progress-ok-a')).toBeInTheDocument();
    expect(screen.getByTestId('dissemination-progress-row-a')).toHaveAttribute(
      'data-status',
      'success',
    );

    rerender(
      <DisseminationProgressRow
        candidateId="a"
        name="a.xml"
        status="failed"
        detail="boom"
        forceReducedMotion={false}
      />,
    );
    expect(screen.getByTestId('dissemination-progress-fail-a')).toBeInTheDocument();
    expect(screen.getByTestId('dissemination-progress-detail-a')).toHaveTextContent(
      'boom',
    );
  });

  it('uses system reduced-motion preference when forceReducedMotion is omitted', () => {
    mockUseReducedMotion.mockReturnValueOnce(true);

    render(
      <DisseminationProgressRow
        candidateId="sys"
        name="sys.xml"
        status="failed"
        detail="timeout"
      />,
    );

    expect(
      screen.queryByTestId('dissemination-progress-graphic-sys'),
    ).not.toBeInTheDocument();
    expect(screen.getByTestId('dissemination-progress-text-sys')).toHaveTextContent(
      'Failed — timeout',
    );
  });
});

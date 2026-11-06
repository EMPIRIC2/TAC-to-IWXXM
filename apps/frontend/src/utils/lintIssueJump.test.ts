import { describe, expect, it } from 'vitest';
import {
  jumpableLintIssues,
  lintIssueFromKey,
  lintSeverityLabel,
  stepLintIssue,
  type JumpableLintIssue,
} from './lintIssueJump';

const wind: JumpableLintIssue = {
  start: 0,
  end: 5,
  message: 'Wind group is incomplete',
  severity: 'error',
  code: 'WIND',
};

describe('lintIssueJump', () => {
  it('drops issues that have no span', () => {
    expect(
      jumpableLintIssues([
        { message: 'missing start', severity: 'error', end: 2 },
        { message: 'missing end', severity: 'error', start: 1 },
        { message: 'empty', severity: 'warning', start: 3, end: 3 },
        wind,
      ]),
    ).toEqual([wind]);
  });

  it('labels severity in words', () => {
    expect(lintSeverityLabel('error')).toBe('Error');
    expect(lintSeverityLabel('warning')).toBe('Warning');
    expect(lintSeverityLabel('warn')).toBe('Warning');
    expect(lintSeverityLabel('info')).toBe('Note');
  });

  it('steps around the list', () => {
    expect(stepLintIssue(0, null, 1)).toBe(0);
    expect(stepLintIssue(3, null, 1)).toBe(0);
    expect(stepLintIssue(3, null, -1)).toBe(2);
    expect(stepLintIssue(3, -1, 1)).toBe(0);
    expect(stepLintIssue(3, 4, -1)).toBe(2);
    expect(stepLintIssue(3, 1, 1)).toBe(2);
    expect(stepLintIssue(3, 0, -1)).toBe(2);
  });

  it('reads Alt+Arrow and ignores other keys', () => {
    const issues = [wind, { ...wind, start: 6, end: 8, message: 'second' }];
    expect(
      lintIssueFromKey({ altKey: false, key: 'ArrowDown' }, issues, null),
    ).toBeNull();
    expect(lintIssueFromKey({ altKey: true, key: 'Enter' }, issues, null)).toBeNull();
    expect(lintIssueFromKey({ altKey: true, key: 'ArrowDown' }, [], null)).toBeNull();
    expect(lintIssueFromKey({ altKey: true, key: 'ArrowDown' }, issues, null)).toEqual(
      issues[0],
    );
    expect(lintIssueFromKey({ altKey: true, key: 'ArrowUp' }, issues, 0)).toEqual(
      issues[1],
    );
    const hole = [wind];
    delete (hole as unknown[])[0];
    expect(lintIssueFromKey({ altKey: true, key: 'ArrowDown' }, hole, null)).toBeNull();
  });
});

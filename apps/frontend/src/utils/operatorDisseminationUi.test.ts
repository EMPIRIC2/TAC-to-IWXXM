/**
 * Drop-guard: dissemination destinations UI removed (FR-052..056 / DI-008).
 */
import { describe, expect, it } from 'vitest';
import {
  isOperatorDisseminationDestinationsEnabled,
  operatorDisseminationUiConfig,
} from './operatorDisseminationUi';

describe('operatorDisseminationUi DI-008', () => {
  it('keeps destinations disabled (success / read path)', () => {
    expect(operatorDisseminationUiConfig.destinationsEnabled).toBe(false);
    expect(isOperatorDisseminationDestinationsEnabled()).toBe(false);
  });
});

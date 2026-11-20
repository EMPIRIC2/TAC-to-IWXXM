import { describe, expect, it } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useWorkbenchBusyFlags } from './workbenchBusyFlags';

describe('useWorkbenchBusyFlags', () => {
  it('updates busy flags with boolean and functional setters', () => {
    const { result } = renderHook(() => useWorkbenchBusyFlags());

    expect(result.current.workbenchBusyRef.current).toBe(false);

    act(() => {
      result.current.setIsConverting(true);
    });
    expect(result.current.workbenchBusyRef.current).toBe(true);
    expect(result.current.isConverting).toBe(true);

    act(() => {
      result.current.setIsConverting((prev) => !prev);
      result.current.setIsConvertAndSending((prev) => !prev);
      result.current.setIsBatchValidating((prev) => !prev);
    });
    expect(result.current.isConverting).toBe(false);
    expect(result.current.isConvertAndSending).toBe(true);
    expect(result.current.isBatchValidating).toBe(true);
    expect(result.current.workbenchBusyRef.current).toBe(true);

    act(() => {
      result.current.setIsConvertAndSending(false);
      result.current.setIsBatchValidating(false);
    });
    expect(result.current.workbenchBusyRef.current).toBe(false);
  });
});

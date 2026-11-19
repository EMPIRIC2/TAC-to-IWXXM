/** Synchronous busy-flag refs for FileConverter queue guards. */
import { useCallback, useRef, useState } from 'react';

/**
 * Type `BusyFlagSetters`.
 * @example
 * const _ = true;
 */
export type BusyFlagSetters = {
  isConverting: boolean;
  isConvertAndSending: boolean;
  isBatchValidating: boolean;
  workbenchBusyRef: { current: boolean };
  setIsConverting: (value: boolean | ((prev: boolean) => boolean)) => void;
  setIsConvertAndSending: (value: boolean | ((prev: boolean) => boolean)) => void;
  setIsBatchValidating: (value: boolean | ((prev: boolean) => boolean)) => void;
};

/**
 * useWorkbenchBusyFlags.
 * @example
 * const _ = true;
 */
export function useWorkbenchBusyFlags(): BusyFlagSetters {
  const [isConverting, setIsConvertingState] = useState(false);
  const [isConvertAndSending, setIsConvertAndSendingState] = useState(false);
  const [isBatchValidating, setIsBatchValidatingState] = useState(false);
  const isConvertingRef = useRef(false);
  const isConvertAndSendingRef = useRef(false);
  const isBatchValidatingRef = useRef(false);
  const workbenchBusyRef = useRef(false);

  const sync = useCallback(() => {
    workbenchBusyRef.current =
      isConvertingRef.current ||
      isConvertAndSendingRef.current ||
      isBatchValidatingRef.current;
  }, []);

  const setIsConverting = useCallback(
    (value: boolean | ((prev: boolean) => boolean)) => {
      const next = typeof value === 'function' ? value(isConvertingRef.current) : value;
      isConvertingRef.current = next;
      sync();
      setIsConvertingState(next);
    },
    [sync],
  );

  const setIsConvertAndSending = useCallback(
    (value: boolean | ((prev: boolean) => boolean)) => {
      const next =
        typeof value === 'function' ? value(isConvertAndSendingRef.current) : value;
      isConvertAndSendingRef.current = next;
      sync();
      setIsConvertAndSendingState(next);
    },
    [sync],
  );

  const setIsBatchValidating = useCallback(
    (value: boolean | ((prev: boolean) => boolean)) => {
      const next =
        typeof value === 'function' ? value(isBatchValidatingRef.current) : value;
      isBatchValidatingRef.current = next;
      sync();
      setIsBatchValidatingState(next);
    },
    [sync],
  );

  return {
    isConverting,
    isConvertAndSending,
    isBatchValidating,
    workbenchBusyRef,
    setIsConverting,
    setIsConvertAndSending,
    setIsBatchValidating,
  };
}

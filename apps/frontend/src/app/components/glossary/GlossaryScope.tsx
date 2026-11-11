/* eslint-disable react-refresh/only-export-components */
/**
 * Context for Annex 3 glossary hover tips (F38).
 */

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useSyncExternalStore,
  type ReactNode,
} from 'react';
import {
  GLOSSARY_PREFS_STORAGE_KEY,
  isGlossaryHoverEnabled,
} from '@/utils/glossaryHoverPrefs';

/**
 * Type `GlossaryScopeValue`.
 * @example
 * const _ = true;
 */
export type GlossaryScopeValue = {
  /** Whether hover/focus tips are active. */
  hoverEnabled: boolean;
  /** Navigate shell to Glossary focused on an entry id. */
  openGlossaryEntry: (entryId: string) => void;
};

const GlossaryScopeContext = createContext<GlossaryScopeValue | null>(null);

/** Subscribe to glossary preference change events. */
function subscribePrefs(onStoreChange: () => void): () => void {
  const handler = (event: StorageEvent) => {
    if (event.key === GLOSSARY_PREFS_STORAGE_KEY || event.key === null) {
      onStoreChange();
    }
  };
  window.addEventListener('storage', handler);
  window.addEventListener('metar-glossary-prefs-changed', onStoreChange);
  return () => {
    window.removeEventListener('storage', handler);
    window.removeEventListener('metar-glossary-prefs-changed', onStoreChange);
  };
}

/**
 * Notify listeners that glossary hover prefs changed in this tab.
 *
 * @example
 * const _ = true;
 */
export function notifyGlossaryPrefsChanged(): void {
  window.dispatchEvent(new Event('metar-glossary-prefs-changed'));
}

/**
 * Provider for glossary tip enablement and Glossary navigation.
 *
 * @param props.openGlossaryEntry - Shell navigation callback
 * @param props.children - Scoped UI
 * @example
 * const _ = true;
 */
export function GlossaryScope({
  openGlossaryEntry,
  children,
}: {
  openGlossaryEntry: (entryId: string) => void;
  children: ReactNode;
}) {
  const hoverEnabled = useSyncExternalStore(
    subscribePrefs,
    isGlossaryHoverEnabled,
    () => true,
  );

  const stableOpen = useCallback(
    (entryId: string) => {
      openGlossaryEntry(entryId);
    },
    [openGlossaryEntry],
  );

  const value = useMemo(
    () => ({ hoverEnabled, openGlossaryEntry: stableOpen }),
    [hoverEnabled, stableOpen],
  );

  return (
    <GlossaryScopeContext.Provider value={value}>
      {children}
    </GlossaryScopeContext.Provider>
  );
}

/**
 * Read glossary scope; returns disabled no-op when outside provider.
 *
 * @example
 * const _ = true;
 */
export function useGlossaryScope(): GlossaryScopeValue {
  const ctx = useContext(GlossaryScopeContext);
  if (ctx) {
    return ctx;
  }
  return {
    hoverEnabled: false,
    openGlossaryEntry: () => undefined,
  };
}

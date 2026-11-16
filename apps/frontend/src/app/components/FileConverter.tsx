import { FileConverterView } from './FileConverterView';
import { useFileConverter } from '@/hooks/useFileConverter';
import type { FileConverterProps } from '@/models/fileConverter';

/**
 * Operator workbench: TAC queue, convert, validate, and dissemination entry points.
 */
/**
 * FileConverter.
 */
export function FileConverter({
  accessToken,
  userEmail = 'Guest',
  isGuest = true,
  onLogout,
  onRequestLogin,
  onOpenHistory,
  onOpenVisuals,
  onLoadWorkSession,
  onNewMetar,
  onSessionUpdated,
  onActiveSessionIdChange,
  activeWorkSessionId,
  loadedWorkSession,
  pendingMapTac = null,
  onPendingMapTacConsumed,
  onOpenCatalog,
}: FileConverterProps) {
  const vm = useFileConverter({
    accessToken,
    userEmail,
    isGuest,
    onLogout,
    onRequestLogin,
    onOpenHistory,
    onOpenVisuals,
    onLoadWorkSession,
    onNewMetar,
    onSessionUpdated,
    onActiveSessionIdChange,
    activeWorkSessionId,
    loadedWorkSession,
    pendingMapTac,
    onPendingMapTacConsumed,
    onOpenCatalog,
  });
  return <FileConverterView {...vm} />;
}

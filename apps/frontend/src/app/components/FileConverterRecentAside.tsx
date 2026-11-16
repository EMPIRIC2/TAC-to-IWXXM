/** FileConverterRecentAside */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterRecentAside.
 */
export function FileConverterRecentAside(props: FileConverterViewProps) {
  const {
    accessToken,
    activeWorkSessionId,
    onLoadWorkSession,
    onOpenHistory,
    recentWorkCollapsed,
    setRecentWorkCollapsed,
  } = props;
  return (
    <aside
      className={
        recentWorkCollapsed
          ? 'relative z-0 sticky top-20 w-12 min-w-0 max-w-12 shrink-0 self-start'
          : 'relative z-0 sticky top-20 mt-8 w-[280px] min-w-0 max-w-[280px] shrink-0 self-start'
      }
      data-testid="recent-work-aside"
    >
      <S.WorkHistorySidebar
        accessToken={accessToken}
        activeSessionId={activeWorkSessionId}
        onSelectSession={onLoadWorkSession}
        onOpenHistory={onOpenHistory}
        collapsed={recentWorkCollapsed}
        onCollapsedChange={setRecentWorkCollapsed}
      />
    </aside>
  );
}

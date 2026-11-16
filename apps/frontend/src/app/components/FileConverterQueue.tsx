/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-nocheck — mechanical line-count split
/** FileConverterQueue */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterQueue.
 */
export function FileConverterQueue(props: FileConverterViewProps) {
  const {
    activeSelectedCount,
    focusQueueItem,
    handleBatchConvertSelected,
    handleBatchValidateSelected,
    handleWorkQueueKeyDown,
    isBusy,
    isReadOnly,
    pendingFiles,
    removePendingFile,
    safeQueueFocusIndex,
    selectedPendingIds,
    setSelectedPendingIds,
  } = props;
  if (pendingFiles.length === 0) {
    return null;
  }
  return (
    <div
      className="mb-8 sticky top-2 z-10 rounded-lg border border-gray-200 bg-white/95 p-4 shadow-sm backdrop-blur dark:border-gray-700 dark:bg-gray-900/95"
      role="region"
      aria-label="Pending files queue"
      data-testid="operator-work-queue"
      tabIndex={0}
      onKeyDown={handleWorkQueueKeyDown}
    >
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Work queue
          </h2>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            ↑/↓ focus · Enter convert · Shift+Enter validate · multi-select for batch
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <S.Button
            type="button"
            size="sm"
            variant="outline"
            data-testid="batch-convert-button"
            disabled={isBusy || isReadOnly || activeSelectedCount === 0}
            onClick={() => {
              void handleBatchConvertSelected();
            }}
            aria-label="Batch convert selected queue items"
          >
            Batch Convert
            <span className="ml-1 tabular-nums">({activeSelectedCount})</span>
          </S.Button>
          <S.Button
            type="button"
            size="sm"
            variant="outline"
            data-testid="batch-validate-button"
            disabled={isBusy || activeSelectedCount === 0}
            onClick={() => {
              void handleBatchValidateSelected();
            }}
            aria-label="Batch validate selected queue items"
          >
            Batch Validate
            <span className="ml-1 tabular-nums">({activeSelectedCount})</span>
          </S.Button>
        </div>
      </div>
      <div className="space-y-2" role="listbox" aria-label="Queue items">
        {pendingFiles.map((file, index) => {
          const focused = index === safeQueueFocusIndex;
          const selected = selectedPendingIds.has(file.id);
          return (
            <S.Card
              key={file.id}
              role="option"
              aria-selected={focused}
              data-testid={`queue-item-${index}`}
              className={`p-4 cursor-pointer dark:border-gray-700 ${
                focused
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-950 ring-2 ring-blue-500'
                  : 'bg-white dark:bg-gray-800'
              }`}
              onClick={() => focusQueueItem(index)}
            >
              <div className="flex items-center justify-between gap-3">
                <div className="flex min-w-0 items-center gap-3">
                  <input
                    type="checkbox"
                    className="h-4 w-4 shrink-0"
                    data-testid={`queue-select-${index}`}
                    checked={selected}
                    onClick={(e) => e.stopPropagation()}
                    onChange={() => {
                      setSelectedPendingIds((prev) =>
                        S.toggleQueueSelection(prev, file.id),
                      );
                    }}
                    aria-label={`Select ${file.name} for batch actions`}
                  />
                  <S.FileText
                    className="w-5 h-5 shrink-0 text-blue-500 dark:text-blue-400"
                    aria-hidden="true"
                  />
                  <div className="min-w-0">
                    <p className="truncate text-base font-medium text-gray-900 dark:text-white">
                      {file.name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {file.content.split('\n').length} line(s)
                      {focused ? ' · focused' : ''}
                    </p>
                  </div>
                </div>
                <S.Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    removePendingFile(file.id);
                  }}
                  className="hover:bg-gray-100 dark:hover:bg-gray-700 focus:ring-2 focus:ring-red-500"
                  aria-label={`Remove ${file.name} from queue`}
                >
                  <S.X
                    className="w-4 h-4 text-gray-600 dark:text-gray-400"
                    aria-hidden="true"
                  />
                </S.Button>
              </div>
            </S.Card>
          );
        })}
      </div>
    </div>
  );
}

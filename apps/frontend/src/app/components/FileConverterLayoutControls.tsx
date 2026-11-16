/** FileConverterLayoutControls */
import type { FileConverterViewProps } from './FileConverterViewProps';

/**
 * FileConverterLayoutControls.
 */
export function FileConverterLayoutControls(props: FileConverterViewProps) {
  const { updateLiveLayout, liveLayout } = props;
  return (
    <div
      className="flex flex-wrap items-center gap-3"
      data-testid="convert-layout-controls"
    >
      <div
        className="flex rounded-md bg-gray-100 p-0.5 dark:bg-gray-800"
        role="group"
        aria-label="Decode density"
      >
        <button
          type="button"
          aria-pressed={liveLayout.density === 'detailed'}
          className={`rounded px-2 py-1 text-xs font-medium ${
            liveLayout.density === 'detailed'
              ? 'bg-gray-300 text-gray-950 dark:bg-gray-600 dark:text-white'
              : 'text-gray-900 dark:text-gray-100'
          }`}
          onClick={() => updateLiveLayout({ density: 'detailed' })}
        >
          Detailed
        </button>
        <button
          type="button"
          aria-pressed={liveLayout.density === 'compact'}
          className={`rounded px-2 py-1 text-xs font-medium ${
            liveLayout.density === 'compact'
              ? 'bg-gray-300 text-gray-950 dark:bg-gray-600 dark:text-white'
              : 'text-gray-900 dark:text-gray-100'
          }`}
          onClick={() => updateLiveLayout({ density: 'compact' })}
        >
          Compact
        </button>
      </div>
      <div
        className="flex rounded-md bg-gray-100 p-0.5 dark:bg-gray-800"
        role="group"
        aria-label="Convert layout"
      >
        <button
          type="button"
          aria-pressed={liveLayout.span === 'roomy'}
          className={`rounded px-2 py-1 text-xs font-medium ${
            liveLayout.span === 'roomy'
              ? 'bg-gray-300 text-gray-950 dark:bg-gray-600 dark:text-white'
              : 'text-gray-900 dark:text-gray-100'
          }`}
          onClick={() => updateLiveLayout({ span: 'roomy' })}
        >
          Roomier
        </button>
        <button
          type="button"
          aria-pressed={liveLayout.span === 'tight'}
          className={`rounded px-2 py-1 text-xs font-medium ${
            liveLayout.span === 'tight'
              ? 'bg-gray-300 text-gray-950 dark:bg-gray-600 dark:text-white'
              : 'text-gray-900 dark:text-gray-100'
          }`}
          onClick={() => updateLiveLayout({ span: 'tight' })}
        >
          Tighter
        </button>
      </div>
      <label className="flex items-center gap-2 text-xs text-gray-800 dark:text-gray-200">
        <input
          type="checkbox"
          data-testid="wrap-xml-lines"
          checked={liveLayout.wrapXml}
          onChange={(event) =>
            updateLiveLayout({
              wrapXml: event.target.checked,
            })
          }
        />
        Wrap XML lines
      </label>
    </div>
  );
}

/* eslint-disable @typescript-eslint/no-explicit-any */
/** Convert chrome toolbar (toggle, product, settings entry). */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';
import type { TacProductSelection } from '@/utils/tacProduct';
import { FileConverterSetup } from './FileConverterSetup';
import { FileConverterParamsBar } from './FileConverterParamsBar';
import { FileConverterMetadataPanel } from './FileConverterMetadataPanel';
import { FileConverterSecondaryActions } from './FileConverterSecondaryActions';
import { FileConverterLayoutControls } from './FileConverterLayoutControls';

/**
 * FileConverterChromeToolbar.
 * @example
 * const _ = true;
 */
export function FileConverterChromeToolbar(props: FileConverterViewProps) {
  const {
    bulletinSource,
    converterOpen,
    setConverterOpen,
    conversionParams,
    setConversionParams,
    convertedFiles,
    focusedBulletinReport,
    inputMode,
    isReadOnly,
    setFocusedBulletinReport,
    setInputMode,
    setManualInput,
    setPlaceholderNotice,
  } = props;

  return (
    <div
      className="flex flex-col gap-1.5 border-b border-gray-200 px-2 py-1.5 dark:border-gray-700 lg:flex-row lg:items-center lg:justify-between"
      data-testid="convert-chrome-toolbar"
    >
      <div
        className="flex min-w-0 flex-wrap items-center gap-1.5"
        data-testid="convert-chrome-toolbar-start"
      >
        <button
          type="button"
          data-testid="convert-panes-toggle"
          aria-expanded={converterOpen}
          className="inline-flex h-8 w-fit items-center rounded-md border border-gray-200 bg-white px-2.5 text-sm font-medium text-gray-800 shadow-sm hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
          onClick={() => setConverterOpen((open: boolean) => !open)}
        >
          {converterOpen ? 'Hide converter' : 'Show converter'}
        </button>
        <S.Label
          htmlFor="param-product"
          className="sr-only text-sm text-gray-700 dark:text-gray-300"
        >
          Product type
        </S.Label>
        <select
          id="param-product"
          aria-label="Product"
          data-testid="product-type-select"
          value={conversionParams.product}
          disabled={isReadOnly}
          onChange={(e) =>
            setConversionParams((prev: any) => ({
              ...prev,
              product: e.target.value as TacProductSelection,
              reportVariant: '',
            }))
          }
          className="min-w-[9.5rem] shrink-0 rounded-md border border-gray-300 bg-white px-2 py-1.5 text-sm text-gray-900 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
        >
          <option value="auto">Auto-detect</option>
          <option value="AIRMET">AIRMET</option>
          <option value="METAR">METAR</option>
          <option value="SIGMET">SIGMET</option>
          <option value="SPECI">SPECI</option>
          <option value="TAF">TAF</option>
          <option value="VAA">VAA</option>
          <option value="TCA">TCA</option>
          <option value="SWXA">SWXA</option>
          <option value="VONA">VONA</option>
          <option value="IWXXM">IWXXM</option>
        </select>
      </div>
      <div
        className="flex shrink-0 items-center gap-1.5 lg:ml-auto"
        data-testid="convert-chrome-toolbar-end"
      >
        <S.ConvertSettingsCog>
          <div
            className="flex max-w-full flex-wrap rounded-md border border-gray-300 dark:border-gray-600"
            role="group"
            aria-label="Input mode"
            data-testid="input-mode-group"
          >
            {(
              [
                ['tac', 'TAC report'],
                ['ahl_bulletin', 'AHL bulletin'],
                ['collect_iwxxm', 'IWXXM COLLECT'],
                ['validate_iwxxm', 'Validate IWXXM'],
              ] as const
            ).map(([value, label]) => (
              <button
                key={value}
                type="button"
                data-testid={`input-mode-${value}`}
                disabled={isReadOnly}
                onClick={() => {
                  if (value !== 'ahl_bulletin' && focusedBulletinReport !== null) {
                    setManualInput(bulletinSource);
                    setFocusedBulletinReport(null);
                  }
                  if (value === 'validate_iwxxm') {
                    const xml = convertedFiles[0]?.convertedContent?.trim() || '';
                    if (xml) {
                      setManualInput(xml);
                    }
                  }
                  setInputMode(value);
                  if (value !== 'collect_iwxxm') {
                    setPlaceholderNotice(null);
                  }
                }}
                className={`px-2 py-1 text-xs whitespace-nowrap ${
                  inputMode === value
                    ? 'bg-blue-700 text-white dark:bg-blue-600'
                    : 'bg-white text-gray-700 dark:bg-gray-800 dark:text-gray-200'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
          <FileConverterSetup {...props} />
          {inputMode !== 'validate_iwxxm' ? (
            <>
              <FileConverterLayoutControls {...props} />
              <FileConverterMetadataPanel {...props} />
              <FileConverterParamsBar {...props} />
            </>
          ) : null}
          <FileConverterSecondaryActions {...props} />
        </S.ConvertSettingsCog>
      </div>
    </div>
  );
}

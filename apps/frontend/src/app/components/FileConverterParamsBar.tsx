/* eslint-disable @typescript-eslint/ban-ts-comment, complexity */
// @ts-nocheck — mechanical line-count split
/** FileConverterParamsBar */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterParamsBar.
 */
export function FileConverterParamsBar(props: FileConverterViewProps) {
  const {
    bulletinFieldError,
    conversionParams,
    isParamsExpanded,
    issuingCenterFieldError,
    setBulletinFieldError,
    setConversionParams,
    setIsParamsExpanded,
    setIssuingCenterFieldError,
  } = props;
  return (
    <div
      className="space-y-3 border-t border-gray-200 pt-3 dark:border-gray-700"
      data-testid="conversion-params-bar"
    >
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-medium text-gray-900 dark:text-white">
          Conversion parameters
        </p>
        <S.Button
          variant="ghost"
          size="sm"
          onClick={() => setIsParamsExpanded(!isParamsExpanded)}
          className="hover:bg-gray-100 dark:hover:bg-gray-700 focus:ring-2 focus:ring-gray-500"
          aria-label={isParamsExpanded ? 'Collapse parameters' : 'Expand parameters'}
        >
          {isParamsExpanded ? (
            <S.ChevronUp
              className="h-4 w-4 text-gray-600 dark:text-gray-400"
              aria-hidden="true"
            />
          ) : (
            <S.ChevronDown
              className="h-4 w-4 text-gray-600 dark:text-gray-400"
              aria-hidden="true"
            />
          )}
        </S.Button>
      </div>
      <div className="flex flex-col gap-3">
        <div>
          <S.Label
            htmlFor="param-bulletin-id"
            className="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-200"
          >
            Bulletin ID
          </S.Label>
          <S.Input
            id="param-bulletin-id"
            data-testid="bulletin-id-input"
            value={conversionParams.bulletinId}
            onChange={(e) => {
              setBulletinFieldError(null);
              setConversionParams((prev) => ({
                ...prev,
                bulletinId: e.target.value.toUpperCase(),
              }));
            }}
            placeholder="SAAA00"
            maxLength={6}
            aria-invalid={S.ariaInvalidFromError(bulletinFieldError)}
            className="dark:border-gray-600 dark:bg-gray-700 dark:text-white"
          />
          {bulletinFieldError ? (
            <p
              className="mt-1 text-xs text-red-600 dark:text-red-400"
              data-testid="bulletin-id-field-error"
              role="alert"
            >
              {bulletinFieldError}
            </p>
          ) : (
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Format: 4 letters + 2 digits. Leave blank to discover from the AHL.
            </p>
          )}
        </div>
        <div>
          <S.IcaoAutocomplete
            label="Issuing Center (ICAO)"
            id="param-issuing-center"
            inputTestId="issuing-center-input"
            formatOnly
            value={conversionParams.issuingCenter}
            onChange={(value) => {
              setIssuingCenterFieldError(null);
              setConversionParams((prev) => ({
                ...prev,
                issuingCenter: value,
              }));
            }}
            placeholder="KWBC"
            maxLength={4}
            helperText={
              issuingCenterFieldError
                ? undefined
                : '4-letter ICAO code. Leave blank to discover from the AHL.'
            }
          />
          {issuingCenterFieldError ? (
            <p
              className="mt-1 text-xs text-red-600 dark:text-red-400"
              data-testid="issuing-center-field-error"
              role="alert"
            >
              {issuingCenterFieldError}
            </p>
          ) : null}
        </div>
        <div className={isParamsExpanded ? '' : 'hidden'}>
          <S.AirportDetailsCard icao={conversionParams.issuingCenter} />
        </div>
        <div className={isParamsExpanded ? '' : 'hidden'}>
          <S.Label htmlFor="param-iwxxm-version" className="mb-2 dark:text-white">
            IWXXM Version
          </S.Label>
          <select
            id="param-iwxxm-version"
            value={conversionParams.iwxxmVersion}
            onChange={(e) =>
              setConversionParams((prev) => ({
                ...prev,
                iwxxmVersion: S.coerceIwxxmVersion(e.target.value),
              }))
            }
            className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
          >
            {S.iwxxmVersionOptionsForProfile(conversionParams.profile).map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        <div className={isParamsExpanded ? '' : 'hidden'}>
          <S.Label htmlFor="param-on-error" className="mb-2 dark:text-white">
            On Error Behavior
          </S.Label>
          <select
            id="param-on-error"
            value={conversionParams.onError}
            onChange={(e) =>
              setConversionParams((prev) => ({
                ...prev,
                onError: e.target.value as OnErrorBehavior,
              }))
            }
            className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
          >
            <option value="skip">Skip - Continue, skip invalid</option>
            <option value="fail">Fail - Stop on first error</option>
            <option value="warn">Warn - Continue with warnings</option>
          </select>
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Fail sets API <code>stop_on_error=true</code>; Skip/Warn leave it false.
          </p>
        </div>
        <div className={isParamsExpanded ? '' : 'hidden'}>
          <S.Label htmlFor="param-log-level" className="mb-2 dark:text-white">
            Log Level
          </S.Label>
          <select
            id="param-log-level"
            value={conversionParams.logLevel}
            onChange={(e) =>
              setConversionParams((prev) => ({
                ...prev,
                logLevel: e.target.value as LogLevel,
              }))
            }
            className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
          >
            <option value="DEBUG">DEBUG</option>
            <option value="INFO">INFO (Default)</option>
            <option value="WARNING">WARNING</option>
            <option value="ERROR">ERROR</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Filters conversion / validation / lint process messages (Results → Console).
            Sent as <code>log_level</code> on Convert.
          </p>
        </div>
        <div className={`flex flex-col gap-3 ${isParamsExpanded ? '' : 'hidden'}`}>
          <S.Label className="dark:text-white">Validation Options</S.Label>
          <S.StrictControls
            strict={conversionParams.strictValidation}
            strictLint={conversionParams.strictLint}
            strictConvert={conversionParams.strictConvert}
            strictValidate={conversionParams.strictValidate}
            onStrictChange={(value) =>
              setConversionParams((prev) => ({
                ...prev,
                strictValidation: value,
              }))
            }
            onStrictLintChange={(value) =>
              setConversionParams((prev) => ({
                ...prev,
                strictLint: value,
              }))
            }
            onStrictConvertChange={(value) =>
              setConversionParams((prev) => ({
                ...prev,
                strictConvert: value,
              }))
            }
            onStrictValidateChange={(value) =>
              setConversionParams((prev) => ({
                ...prev,
                strictValidate: value,
              }))
            }
          />
          <label className="flex cursor-pointer items-center">
            <input
              type="checkbox"
              checked={conversionParams.includeNilReasons}
              onChange={(e) =>
                setConversionParams((prev) => ({
                  ...prev,
                  includeNilReasons: e.target.checked,
                }))
              }
              className="h-4 w-4 rounded text-blue-600 focus:ring-2 focus:ring-blue-500"
              data-testid="include-nil-reasons-checkbox"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              Include Nil Reasons
            </span>
          </label>
          <p className="-mt-1 ml-6 text-xs text-gray-500 dark:text-gray-400">
            Sent as <code>include_nil_reasons</code>.
          </p>
        </div>
      </div>
    </div>
  );
}

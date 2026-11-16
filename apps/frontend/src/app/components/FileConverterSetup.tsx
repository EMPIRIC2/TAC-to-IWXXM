/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-nocheck — mechanical line-count split
/** FileConverterSetup */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterSetup.
 */
export function FileConverterSetup(props: FileConverterViewProps) {
  const {
    activeReportVariant,
    applyWmoLibraryDefaultsSync,
    caProfileBlocked,
    calmProfileLabel,
    conversionParams,
    inputMode,
    isReadOnly,
    onOpenCatalog,
    reportVariantOptions,
    setConversionParams,
    setProfileDrawerOpen,
  } = props;
  return (
    <div
      className="space-y-3 border-t border-gray-200 pt-3 dark:border-gray-700"
      data-testid="convert-setup"
    >
      <div className="flex flex-col gap-1.5">
        <div
          className="flex min-w-0 flex-col gap-1.5 rounded-md border border-gray-300 bg-white px-2 py-1.5 dark:border-gray-600 dark:bg-gray-800 lg:flex-row lg:flex-wrap lg:items-center"
          data-testid="product-profile-bar"
        >
          <div className="flex min-w-0 flex-wrap items-center gap-2">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Profile:{' '}
              <span
                data-testid="convert-active-profile"
                className="font-medium text-gray-900 dark:text-gray-100"
              >
                {calmProfileLabel}
              </span>
            </span>
            <button
              type="button"
              className="text-sm font-medium text-blue-700 underline-offset-2 hover:underline dark:text-blue-300"
              data-testid="convert-profile-change-live"
              onClick={() => setProfileDrawerOpen(true)}
            >
              Change
            </button>
          </div>
          {inputMode !== 'validate_iwxxm' ? (
            <>
              <details
                className="order-2 w-full rounded-md border border-gray-200 bg-white px-2 py-1.5 dark:border-gray-700 dark:bg-gray-800"
                data-testid="convert-advanced-engines"
              >
                <summary className="cursor-pointer select-none text-sm font-medium text-gray-700 dark:text-gray-200">
                  Customize each step
                </summary>
                <div className="mt-2 space-y-2 border-t border-gray-100 pt-2 dark:border-gray-700">
                  <S.LibraryPickersBar
                    disabled={isReadOnly}
                    values={{
                      conversionLibraryId: conversionParams.conversionLibraryId,
                      tacValidationLibraryId: conversionParams.tacValidationLibraryId,
                      iwxxmValidationLibraryId:
                        conversionParams.iwxxmValidationLibraryId,
                      disseminationLibraryId: conversionParams.disseminationLibraryId,
                      decodingLibraryId: conversionParams.decodingLibraryId,
                    }}
                    onOpenCatalog={onOpenCatalog}
                    onChange={(next, conversionEngineProfileId) => {
                      setConversionParams((prev) => {
                        if (!conversionEngineProfileId) {
                          return { ...prev, ...next };
                        }
                        const lineChanging = S.isSemanticProfileLineChange(
                          prev.profile,
                          conversionEngineProfileId,
                        );
                        if (lineChanging) {
                          if (
                            !S.confirmLibraryResetForProfile(conversionEngineProfileId)
                          ) {
                            return prev;
                          }
                          const { profile, libraryIds } = S.libraryResetForProfile(
                            conversionEngineProfileId,
                          );
                          return {
                            ...prev,
                            ...libraryIds,
                            profile,
                            reportVariant: '',
                            iwxxmVersion: S.coerceIwxxmVersionForProfile(
                              profile,
                              prev.iwxxmVersion,
                            ),
                          };
                        }
                        const profile = S.coerceIwxxmProfile(conversionEngineProfileId);
                        return {
                          ...prev,
                          ...next,
                          profile,
                          reportVariant: '',
                          iwxxmVersion: S.coerceIwxxmVersionForProfile(
                            profile,
                            prev.iwxxmVersion,
                          ),
                        };
                      });
                    }}
                  />
                  <div className="flex shrink-0 items-center gap-1">
                    <S.Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      disabled={isReadOnly}
                      data-testid="reset-wmo-library-defaults"
                      className="text-xs text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                      onClick={() => {
                        const sync = S.resetWmoLibraryDefaultsSync();
                        applyWmoLibraryDefaultsSync(sync);
                      }}
                    >
                      {S.CONVERT_RESET_WMO_LIBRARY_DEFAULTS}
                    </S.Button>
                    <S.Tooltip>
                      <S.TooltipTrigger asChild>
                        <button
                          type="button"
                          className="inline-flex h-6 w-6 items-center justify-center rounded text-gray-500 hover:text-gray-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:text-gray-400 dark:hover:text-gray-100"
                          aria-label="About reset to WMO defaults"
                          data-testid="reset-wmo-library-defaults-help"
                        >
                          <S.CircleHelp className="h-3.5 w-3.5" aria-hidden />
                        </button>
                      </S.TooltipTrigger>
                      <S.TooltipContent side="bottom" className="max-w-xs text-balance">
                        {S.CONVERT_RESET_WMO_LIBRARY_DEFAULTS_HELP}
                      </S.TooltipContent>
                    </S.Tooltip>
                  </div>
                </div>
              </details>
              {reportVariantOptions.length > 0 && inputMode !== 'ahl_bulletin' && (
                <>
                  <div className="order-1 flex shrink-0 items-center gap-1">
                    <S.Label
                      htmlFor="param-report-variant"
                      className="shrink-0 text-sm text-gray-700 dark:text-gray-300"
                    >
                      Report variant
                    </S.Label>
                    <S.Tooltip>
                      <S.TooltipTrigger asChild>
                        <button
                          type="button"
                          className="inline-flex h-6 w-6 items-center justify-center rounded text-gray-500 hover:text-gray-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:text-gray-400 dark:hover:text-gray-100"
                          aria-label="About Report variant"
                          data-testid="report-variant-help-icon"
                        >
                          <S.CircleHelp className="h-3.5 w-3.5" aria-hidden />
                        </button>
                      </S.TooltipTrigger>
                      <S.TooltipContent side="bottom" className="max-w-xs text-balance">
                        Optional profile-scoped IWXXM root inside the selected product
                        family. Leave on Auto-detect to infer from the TAC lead.
                      </S.TooltipContent>
                    </S.Tooltip>
                  </div>
                  <select
                    id="param-report-variant"
                    aria-label="Report variant"
                    data-testid="report-variant-select"
                    value={activeReportVariant}
                    disabled={isReadOnly}
                    onChange={(e) => {
                      setConversionParams((prev) => ({
                        ...prev,
                        reportVariant: e.target.value,
                      }));
                    }}
                    className="order-1 min-w-[10rem] shrink-0 rounded-md border border-gray-300 bg-white px-2 py-1.5 text-sm text-gray-900 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="">Auto-detect from TAC</option>
                    {reportVariantOptions.map((variant) => (
                      <option key={variant.tac_lead} value={variant.tac_lead}>
                        {variant.tac_lead}
                        {variant.minimal_observation ? ' (minimal)' : ''}
                      </option>
                    ))}
                  </select>
                </>
              )}
            </>
          ) : null}
        </div>
        {inputMode !== 'validate_iwxxm' ? (
          <>
            <div className="flex flex-wrap items-center justify-end gap-2">
              <p
                id="product-profile-bar-summary"
                className="sr-only"
                data-testid="product-profile-bar-summary"
              >
                Encoding and packaging rules only. This does not set destinations,
                credentials, or editable overlays.
              </p>
              <details
                className="rounded-md border border-gray-200 bg-white px-2 py-1 text-xs text-gray-600 open:pb-2 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400"
                data-testid="product-profile-trust-details"
              >
                <summary className="cursor-pointer select-none font-medium text-gray-700 dark:text-gray-300">
                  What&apos;s this?
                </summary>
                <div className="mt-1.5 space-y-1.5 border-t border-gray-100 pt-1.5 dark:border-gray-700">
                  <p data-testid="semantic-profile-help">
                    Profile selects encoding rules for conversion. Does not set
                    destinations or credentials, and does not make national overlays
                    editable.
                  </p>
                  <p data-testid="exchange-profile-help">
                    Exchange profile is used when packaging bulletins. Does not choose
                    destinations or credentials.
                  </p>
                </div>
              </details>
            </div>
            <div
              className="hidden flex-wrap items-center gap-2"
              aria-hidden="true"
              data-testid="country-preset"
            >
              <label
                className="flex items-center gap-2"
                htmlFor="country-preset-select"
              >
                <span className="text-xs font-medium text-gray-500">
                  {S.COUNTRY_PRESET_LABEL}
                </span>
                <select
                  id="country-preset-select"
                  data-testid="country-preset-select"
                  aria-label={S.COUNTRY_PRESET_LABEL}
                  title={S.COUNTRY_PRESET_HELP}
                  className="min-w-[10rem] rounded-md border border-gray-300 bg-white px-2 py-1.5 text-sm text-gray-900 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  value={S.countryPresetLineForLibraries(conversionParams)}
                  disabled={isReadOnly}
                  onChange={(event) => {
                    const line = event.target.value;
                    if (line === '') {
                      return;
                    }
                    const { profile, libraryIds } = S.libraryResetForProfile(line);
                    setConversionParams((prev) => ({
                      ...prev,
                      ...libraryIds,
                      profile,
                      reportVariant: '',
                      iwxxmVersion: S.coerceIwxxmVersionForProfile(
                        profile,
                        prev.iwxxmVersion,
                      ),
                    }));
                  }}
                >
                  <option value="">{S.COUNTRY_PRESET_CUSTOM}</option>
                  {S.SEMANTIC_PROFILE_OPTIONS.filter((option) =>
                    (S.COUNTRY_PRESET_LINES as readonly string[]).includes(
                      option.value,
                    ),
                  ).map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
              <p className="sr-only" data-testid="country-preset-help">
                {S.COUNTRY_PRESET_HELP}
              </p>
            </div>
            {S.isCaEcccProfile(conversionParams.profile) && (
              <div
                className="rounded border border-sky-200 bg-sky-50 px-2 py-1.5 text-xs text-sky-950 dark:border-sky-900 dark:bg-sky-950/40 dark:text-sky-100"
                data-testid="ca-eccc-profile-metadata"
                role="status"
              >
                <p>IWXXM {S.CA_ECCC_IWXXM_VERSION} (MSC operational line)</p>
                <p>{S.CA_ECCC_EXTENSION_LABEL}</p>
                <p>Supported products: {S.CA_ECCC_SUPPORTED_PRODUCTS.join(', ')}</p>
                {caProfileBlocked && (
                  <p className="mt-1 font-medium text-amber-900 dark:text-amber-200">
                    Canadian extension schemas are not available on this deployment.
                    Conversion is blocked until the vendor bundle is installed.
                  </p>
                )}
              </div>
            )}
          </>
        ) : null}
      </div>
    </div>
  );
}

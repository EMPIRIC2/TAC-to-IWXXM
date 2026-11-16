/** FileConverterMetadataPanel */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterMetadataPanel.
 */
export function FileConverterMetadataPanel(props: FileConverterViewProps) {
  const {
    isGuest,
    isMetadataChecklistOpen,
    isReadOnly,
    metadataPrefs,
    persistMetadataPrefs,
    setIsMetadataChecklistOpen,
    updateMetadataChecklist,
  } = props;
  return (
    <div
      className="flex min-w-0 flex-col gap-1 border-t border-gray-200 pt-3 dark:border-gray-700"
      data-testid="conversion-metadata-export-panel"
    >
      <div className="flex items-center gap-2">
        <S.Checkbox
          id="conversion-metadata-toggle"
          data-testid="conversion-metadata-toggle"
          checked={metadataPrefs.enabled}
          disabled={isReadOnly}
          onCheckedChange={(checked) => {
            persistMetadataPrefs({
              ...metadataPrefs,
              enabled: checked === true,
              checklist:
                checked === true && !metadataPrefs.enabled
                  ? S.defaultConversionMetadataChecklist()
                  : metadataPrefs.checklist,
            });
          }}
        />
        <S.Label
          htmlFor="conversion-metadata-toggle"
          className="flex cursor-pointer items-center gap-1 text-sm text-gray-800 dark:text-gray-200"
        >
          {S.CONVERSION_METADATA_TOGGLE_LABEL}
          <S.Tooltip>
            <S.TooltipTrigger asChild>
              <button
                type="button"
                className="inline-flex h-5 w-5 items-center justify-center rounded text-gray-500 hover:text-gray-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:text-gray-400 dark:hover:text-gray-100"
                aria-label="About conversion metadata"
                data-testid="conversion-metadata-toggle-help"
                onClick={(event) => event.preventDefault()}
              >
                <S.CircleHelp className="h-3.5 w-3.5" aria-hidden />
              </button>
            </S.TooltipTrigger>
            <S.TooltipContent side="bottom" className="max-w-xs text-balance">
              {S.CONVERSION_METADATA_TOGGLE_HELP}
            </S.TooltipContent>
          </S.Tooltip>
          <S.BetaBadge className="inline-flex" />
        </S.Label>
      </div>
      {metadataPrefs.enabled ? (
        <S.Collapsible
          open={isMetadataChecklistOpen}
          onOpenChange={setIsMetadataChecklistOpen}
        >
          <S.CollapsibleTrigger asChild>
            <button
              type="button"
              className="flex items-center gap-1 text-left text-xs font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
              data-testid="conversion-metadata-checklist-trigger"
            >
              {isMetadataChecklistOpen ? (
                <S.ChevronUp className="h-3.5 w-3.5" aria-hidden="true" />
              ) : (
                <S.ChevronDown className="h-3.5 w-3.5" aria-hidden="true" />
              )}
              {S.CONVERSION_METADATA_CHECKLIST_HEADING}
            </button>
          </S.CollapsibleTrigger>
          <S.CollapsibleContent
            className="mt-1 space-y-1.5"
            data-testid="conversion-metadata-checklist"
          >
            {(
              [
                ['libraries', S.CONVERSION_METADATA_CHECKLIST_LIBRARIES],
                ['libraryYamlHashes', S.CONVERSION_METADATA_CHECKLIST_YAML_HASHES],
                ['convertContext', S.CONVERSION_METADATA_CHECKLIST_CONVERT_CONTEXT],
                ['operator', S.CONVERSION_METADATA_CHECKLIST_OPERATOR],
                ['lintSummary', S.CONVERSION_METADATA_CHECKLIST_LINT],
                ['tacFingerprint', S.CONVERSION_METADATA_CHECKLIST_TAC_FINGERPRINT],
                [
                  'mappingBridgeSummary',
                  S.CONVERSION_METADATA_CHECKLIST_MAPPING_BRIDGE,
                ],
              ] as const
            ).map(([key, label]) => (
              <div key={key} className="flex items-center gap-2">
                <S.Checkbox
                  id={`conversion-metadata-check-${key}`}
                  checked={metadataPrefs.checklist[key]}
                  disabled={isReadOnly || (key === 'operator' && isGuest)}
                  onCheckedChange={(checked) =>
                    updateMetadataChecklist(key, checked === true)
                  }
                />
                <S.Label
                  htmlFor={`conversion-metadata-check-${key}`}
                  className="cursor-pointer text-xs text-gray-700 dark:text-gray-300"
                >
                  {label}
                  {key === 'operator' && isGuest ? ' (sign in required)' : ''}
                </S.Label>
              </div>
            ))}
          </S.CollapsibleContent>
        </S.Collapsible>
      ) : null}
    </div>
  );
}

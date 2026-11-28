/** Re-exports for FileConverter hook parts. */

export {
  useState,
  useRef,
  useEffect,
  useLayoutEffect,
  useCallback,
  useMemo,
} from 'react';
export { stationFromReport } from '@/utils/decodeVisuals';
export { DECODE_VISUALS_OPEN } from '@/utils/decodeVisualsCopy';
export { publishDecodeVisuals } from '@/utils/decodeVisualsStore';
export { type LivePlace } from '@/utils/liveMap';
export { LiveWorldMap } from '@/app/components/LiveWorldMap';
export { Button } from '@/app/components/ui/button';
export { Card } from '@/app/components/ui/card';
export { Input } from '@/app/components/ui/input';
export { Label } from '@/app/components/ui/label';
export { TacEditor } from '@/app/components/TacEditor';
export { DecodePanel } from '@/app/components/DecodePanel';
export { FailedTacCue } from '@/app/components/FailedTacCue';
export {
  IwxxmPreviewPane,
  type IwxxmPreviewMode,
  type IwxxmPreviewStatus,
} from '@/app/components/IwxxmPreviewPane';
export { SoftPreviewControl } from '@/app/components/SoftPreviewControl';
export { PropagateResidualsControl } from '@/app/components/PropagateResidualsControl';
export { IncludeNationalRemarksControl } from '@/app/components/IncludeNationalRemarksControl';
export { LiveIwxxmToggle } from '@/app/components/LiveIwxxmToggle';
export { BulletinReportList } from '@/app/components/BulletinReportList';
export { LiveConvertStatusStrip } from '@/app/components/LiveConvertStatusStrip';
export { TacLintJumps } from '@/app/components/TacLintJumps';
export { StatusBanner } from '@/app/components/StatusBanner';
export { ConvertResultsDrawer } from '@/app/components/ConvertResultsDrawer';
export { ConvertSettingsCog } from '@/app/components/ConvertSettingsCog';
export { VerticalResizeHandle } from '@/app/components/VerticalResizeHandle';
export {
  defaultTabAfterConvert,
  shouldAutoOpenResultsDrawer,
  type ConvertResultsTab,
} from '@/utils/convertResultsDrawer';
export {
  lintHighlightTokens,
  readLintHighlightPreset,
  writeLintHighlightPreset,
  type LintHighlightPreset,
} from '@/utils/lintHighlightPreset';
export { useLintIssueCatalog } from '@/hooks/useLintIssueCatalog';
export {
  Upload,
  X,
  Download,
  Copy,
  FileText,
  Loader2,
  Settings,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  XCircle,
  LogOut,
  CircleHelp,
} from 'lucide-react';
export { default as JSZip } from 'jszip';
export { toast } from 'sonner';
export { ThemeToggle } from '@/app/components/ThemeToggle';
export { GoldenExamplesSelect } from '@/app/components/GoldenExamplesSelect';
export { BetaBadge } from '@/app/components/BetaBadge';
export { Checkbox } from '@/app/components/ui/checkbox';
export {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/app/components/ui/collapsible';
export { Tooltip, TooltipContent, TooltipTrigger } from '@/app/components/ui/tooltip';
export {
  fetchProfileCatalog,
  type MetarFamilyVariant,
  type ProfileCatalogEntry,
} from '@/utils/conversionProfilesApi';
export { convertOverlayFields } from '@/utils/convertOverlayFields';
export { LibraryPickersBar } from '@/app/components/LibraryPickersBar';
export { libraryDisplayName } from '@/utils/libraryChoiceReason';
export { libraryIdsForNationalLine } from '@/utils/libraryIds';
export {
  confirmLibraryResetForProfile,
  COUNTRY_PRESET_LINES,
  countryPresetLineForLibraries,
  libraryIdsFromSessionParams,
  isSemanticProfileLineChange,
  libraryResetForProfile,
} from '@/utils/profileLibraryReset';
export {
  buildConversionExportMetadata,
  CONVERSION_METADATA_CHECKLIST_CONVERT_CONTEXT,
  CONVERSION_METADATA_CHECKLIST_HEADING,
  CONVERSION_METADATA_CHECKLIST_LIBRARIES,
  CONVERSION_METADATA_CHECKLIST_LINT,
  CONVERSION_METADATA_CHECKLIST_MAPPING_BRIDGE,
  CONVERSION_METADATA_CHECKLIST_OPERATOR,
  CONVERSION_METADATA_CHECKLIST_TAC_FINGERPRINT,
  CONVERSION_METADATA_TOGGLE_HELP,
  CONVERSION_METADATA_CHECKLIST_YAML_HASHES,
  CONVERSION_METADATA_TOGGLE_LABEL,
  defaultConversionMetadataChecklist,
  isConversionMetadataExportEnabled,
  metaSidecarFileName,
  readConversionMetadataPrefs,
  serializeConversionMetadata,
  writeConversionMetadataPrefs,
  type ConversionExportContext,
  type ConversionMetadataChecklistKey,
  type ConversionMetadataPrefs,
} from '@/utils/conversionExportMetadata';
export {
  CONVERT_RESET_WMO_LIBRARY_DEFAULTS,
  CONVERT_RESET_WMO_LIBRARY_DEFAULTS_HELP,
  COUNTRY_PRESET_CUSTOM,
  COUNTRY_PRESET_HELP,
  COUNTRY_PRESET_LABEL,
  VALIDATE_IWXXM_DROP_HELP,
  VALIDATE_IWXXM_DROP_TITLE,
  VALIDATE_IWXXM_EMPTY_RESULTS,
  VALIDATE_IWXXM_HEADING,
  VALIDATE_IWXXM_INTRO,
} from '@/utils/conversionProfilesCopy';
export {
  readWmoLibraryDefaultsSync,
  resetWmoLibraryDefaultsSync,
  WMO_LIBRARY_DEFAULTS_SYNC_EVENT,
  WMO_LIBRARY_DEFAULTS_SYNC_KEY,
  type WmoLibraryDefaultsSync,
} from '@/utils/wmoLibraryDefaultsSync';
export { optionalFormField } from '@/utils/optionalFormField';
export { UserPreferencesDialog } from '@/app/components/UserPreferencesDialog';
export { PrivacyNotice } from '@/app/components/PrivacyNotice';
export { PrivacySettingsDialog } from '@/app/components/PrivacySettingsDialog';
export { OperatorFooter } from '@/app/components/OperatorFooter';
export { SiteTermsDialog } from '@/app/components/SiteTermsDialog';
export {
  acknowledgePrivacyNotice,
  shouldShowPrivacyNotice,
} from '@/utils/privacyPreferences';
export {
  GUEST_LOSS_OF_PROGRESS_MESSAGE,
  shouldShowGuestLossOfProgressNotice,
} from '@/utils/guestLossNotice';
export {
  preferCollapsedWorkbenchChrome,
  subscribeNarrowWorkbenchChrome,
} from '@/utils/workbenchChrome';
export {
  DEFAULT_IWXXM_VERSION,
  CA_ECCC_IWXXM_VERSION,
  type IwxxmVersionId,
  coerceIwxxmVersion,
  coerceIwxxmVersionForProfile,
  isMscOperationalLine,
  iwxxmVersionOptionsForProfile,
} from '@/utils/iwxxmVersions';
export { signOutWithScope } from '@/utils/supabase/logout';
export { getExampleById } from '@/fixtures/examples/examplesCatalog';
export { IcaoAutocomplete } from '@/app/components/IcaoAutocomplete';
export { AirportDetailsCard } from '@/app/components/AirportDetailsCard';
export {
  convertMetarToIwxxm as callBackendConversion,
  convertBulletin,
  ingestCollect,
  lintTac,
  validateIwxxm,
  fetchSchemaStatus,
  downloadBlob,
  EndpointNotImplementedError,
  type FailedSpan,
} from '/utils/api';
export type { ValidateResponse } from '@/utils/openapiTypes';
export { ValidateIwxxmReport } from '@/app/components/ValidateIwxxmReport';
export {
  clampQueueIndex,
  nextQueueIndex,
  prevQueueIndex,
  toggleQueueSelection,
} from '@/utils/operatorWorkQueue';
export { useLiveWorkbenchAssist } from '@/hooks/useLiveWorkbenchAssist';
export {
  formFieldSpanInEditor,
  lintSummaryLabel,
  previewIsIncomplete,
  readGroupTrace,
  spansWithSelection,
  type GroupTrace,
  type LiveTraceTarget,
} from '@/utils/liveConvertTrace';
export {
  jumpableLintIssues,
  lintIssueFromKey,
  type JumpableLintIssue,
} from '@/utils/lintIssueJump';
export {
  errorLayerNames,
  lintIssueCounts,
  outputLayerStatus,
  strictConvertRan,
  tacLintLayerStatus,
} from '@/utils/checkLayers';
export {
  appendOutputVersion,
  readOutputVersions,
  type OutputVersion,
} from '@/utils/outputVersions';
export { shellFrameClass, useLiveConvertLayout } from '@/utils/liveConvertLayout';
export { listBulletinReports, replaceBulletinReport } from '@/utils/bulletinReportList';
export { isAbortError } from '@/utils/liveAssist';
export {
  detectTacProduct,
  coerceIwxxmProfile,
  hydrateSemanticProfile,
  isCaEcccProfile,
  isConvertProductSelection,
  resolveConvertProduct,
  splitManualEntries,
  DEFAULT_SEMANTIC_PROFILE,
  SEMANTIC_PROFILE_OPTIONS,
  TAC_PRODUCTS,
  type TacProduct,
  type IwxxmProfile,
  type TacProductSelection,
} from '@/utils/tacProduct';
export {
  coerceExchangeProfile,
  DEFAULT_EXCHANGE_PROFILE,
  type ExchangeProfileId,
} from '@/utils/exchangeProfile';
export {
  CA_ECCC_EXTENSION_LABEL,
  CA_ECCC_SUPPORTED_PRODUCTS,
  exchangeOutputForProfile,
  nationalExtensionsForProfile,
} from '@/utils/profileWire';
export {
  IWXXM_PRODUCT_CONVERT_ARIA,
  IWXXM_PRODUCT_CONVERT_LABEL,
  IWXXM_PRODUCT_HELP,
} from '@/utils/iwxxmProductCopy';
export {
  CONVERT_AND_SEND_UPLOAD_OPTIONS,
  uploadConvertedFiles,
} from '@/utils/databaseUpload';
export { ConvertHelpChecklist } from '@/app/components/ConvertHelpChecklist';
export { ConvertProfileDrawer } from '@/app/components/ConvertProfileDrawer';
export { ErrorLogPanel, type ConversionLog } from '@/app/components/ErrorLogPanel';
export { WorkHistorySidebar } from '@/app/components/WorkHistorySidebar';
export type { WorkSession } from '@metar/shared';
export { useWorkSessionSync } from '@/hooks/useWorkSessionSync';
export {
  type ConverterSnapshot,
  resolveManualLineMetaFromResult,
} from '@/utils/workSessionPayload';
export { readGuestConverterState } from '@/utils/guestConverterState';
export {
  CALM_CONVERT_PRIMARY_LABEL,
  CALM_DOWNLOAD_PRIMARY_LABEL,
  deriveCalmConvertUi,
  resolveCalmProfileLabel,
} from '@/utils/convertCalmState';
export {
  assessConvertedFile,
  PAGE_TITLE,
  type ResultIssueInput,
} from '@/utils/resultCard';
export {
  ACCUMULATE_RESULT_CAP,
  appendConvertedWithinCap,
  manualDownloadXmlName,
  manualOutputName,
  nextFirstAccumulatedTac,
  outputArchiveName,
  outputFilenameAfterReportLoad,
  sanitizeOutputFilename,
  toIwxxmDownloadName,
  toTacSourceName,
  alignConversionZipPairs,
} from '@/utils/outputFilename';
export { resolveConvertedDownloadXmlName } from './fileConverterDownloadName';

export { ConvertResultStatus } from '@/app/components/ConvertResultStatus';
export { deriveTacDisplayTitle, resolveOriginalTac } from '@/utils/resultTraceability';
export {
  convertFieldsFromParamsBar,
  isValidBulletinId,
  isValidIssuingCenter,
  type ConvertLogLevel,
  type ConvertOnError,
  type ConvertParamsBar,
} from '@/utils/convertParams';
export { StrictControls } from '@/app/components/StrictControls';
export {
  BULLETIN_ID_FIELD_ERROR,
  ISSUING_CENTER_FIELD_ERROR,
} from '@/utils/bulletinFieldsCopy';
export {
  detectInputKind,
  kindToMode,
  looksLikeAhlBulletin,
  looksLikeCollectIwxxm,
  looksLikeTacNotXml,
  type OperatorInputMode,
} from '@/utils/inputKind';
export { inflateGzipToText, isGzipFileName } from '@/utils/gunzip';
export {
  applyFocusedQueueContent,
  ariaInvalidFromError,
  caExtensionBundleAvailableFromStatus,
  coalescePreviewXml,
  firstTacForArchive,
  focusedValidateErrorMessage,
  forEachFileInList,
  hydratedResultName,
  isDropZoneActivateKey,
  iwxxmValidationErrorMessage,
  lintIssueCount,
  queueResultOriginalName,
} from '@/utils/fileInputHelpers';
export type {
  ConversionParams,
  ConvertedFile,
  FileConverterProps,
  PendingFile,
} from '@/models/fileConverter';
export {
  isStructuredConvertError,
  mergeVisibleConvertErrors,
  fallbackProfileSummary,
  paramsBarFromState,
  snapshotExportContext,
  initialConversionParams,
  conversionParamsFromStoredPreferences,
  activeMetarFamilyVariants,
} from '@/utils/fileConverterHelpers';

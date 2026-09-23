/**
 * Operator-visible copy for ConversionProfile editor (EV-933 / F7.w).
 * Plain language only — no planning vocabulary.
 */

export const PROFILES_EDITOR_TITLE = 'Conversion profiles';
export const PROFILES_EDITOR_SUBTITLE =
  'Inspect deployed profiles and compare settings. Rule catalogs are read-only; selection uses workbench dropdowns.';
export const PROFILES_TRUST_CATALOGS_HINT =
  'Browse TAC, IWXXM, conversion, dissemination, and decoding rules on the Validation Issues Catalog tab.';
export const PROFILES_AUTHORING_RETIRED_NOTE =
  'In-app profile and library authoring has been removed. Deployed packages own the rules.';
export const PROFILES_ASSEMBLY_HEADING = 'Guided assembly';
export const PROFILES_ASSEMBLY_HELP =
  'Work top to bottom: choose a base profile, map TAC tokens to IWXXM, then attach validation and dissemination when ready.';
export const PROFILES_ASSEMBLY_STEP_BASE = '1 · Base profile';
export const PROFILES_ASSEMBLY_STEP_CONVERT = '2 · Conversion library';
export const PROFILES_ASSEMBLY_STEP_VALIDATE = '3 · Validation libraries';
export const PROFILES_ASSEMBLY_STEP_DISSEM = '4 · Dissemination & decoding';
export const PROFILES_LIBRARIES_HEADING = 'Libraries';
export const PROFILES_LIBRARIES_HELP =
  'Create or fork assets in each library. Built-in defaults stay read-only until you fork.';
export const PROFILES_LIBRARY_TAB_CONVERSION = 'Conversion';
export const PROFILES_LIBRARY_TAB_TAC_VALIDATION = 'TAC validation';
export const PROFILES_LIBRARY_TAB_IWXXM_VALIDATION = 'IWXXM validation';
export const PROFILES_LIBRARY_TAB_DISSEMINATION = 'Dissemination';
export const PROFILES_LIBRARY_TAB_DECODING = 'Decoding';
export const PROFILES_LIBRARY_TAB_OVERVIEW = 'Overview';
export const PROFILES_LIBRARY_LIST_LOADING = 'Loading library assets…';
export const PROFILES_LIBRARY_LIST_EMPTY = 'No assets in this library yet.';
export const PROFILES_LIBRARY_LIST_ERROR = 'Library assets unavailable.';
export const PROFILES_LIBRARY_ACCESS_BUILTIN = 'built-in';
export const PROFILES_LIBRARY_ACCESS_CUSTOM = 'custom';
export const PROFILES_LIBRARY_STUB_HELP =
  'Select a built-in asset to review. Editing creates your own fork in a later step.';
export const PROFILES_LIBRARY_DISSEM_HELP =
  'Ordered post-IWXXM transforms (envelope, topic/filename, checksum, bulletin re-wrap) apply on Disseminate and Convert & Send only — not Convert-only.';
export const PROFILES_LIBRARY_DISSEM_TRANSFORMS_HEADING = 'Ordered transforms';
export const PROFILES_LIBRARY_DISSEM_EMPTY_TRANSFORMS =
  'No transforms defined for this asset.';
export const PROFILES_LIBRARY_DECODE_HELP =
  'Plain-language decode glossary seeded from the TAC decode catalog. Select this library on Convert to drive decode explanations.';
export const PROFILES_LIBRARY_DECODE_ENTRIES_HEADING = 'Decode entries';
export const PROFILES_LIBRARY_DECODE_EMPTY = 'No matching decode entries.';
export const PROFILES_CONV_TEMPLATES_HEADING = 'Conversion tokens';
export const PROFILES_CONV_TEMPLATES_HELP =
  'Map TAC groups to IWXXM blocks with typed slots. Built-in rules can be viewed or forked; your customs are editable.';
export const PROFILES_CONV_TEMPLATES_LOADING = 'Loading conversion tokens…';
export const PROFILES_CONV_TEMPLATES_EMPTY = 'No conversion tokens available.';
export const PROFILES_CONV_TEMPLATES_FORK = 'Fork to custom';
export const PROFILES_CONV_TEMPLATES_PREVIEW = 'Preview mapping';
export const PROFILES_CONV_TEMPLATES_MOVE_UP = 'Move slot up';
export const PROFILES_CONV_TEMPLATES_MOVE_DOWN = 'Move slot down';
export const PROFILES_CONV_TEMPLATES_FOCUS = 'Focused TAC group';
export const PROFILES_CONV_TEMPLATES_COMMENTS = 'Comments';
export const PROFILES_CONV_TEMPLATES_BETA = 'Conversion tokens';
export const PROFILES_CONV_TEMPLATES_MODE = 'Token mode';
export const PROFILES_CONV_TEMPLATES_MODE_CONVERT = 'Convert';
export const PROFILES_CONV_TEMPLATES_MODE_DECODE = 'Decode only';
export const PROFILES_CONV_TEMPLATES_MODE_SKIP = 'Skip';
export const PROFILES_CONV_TEMPLATES_GLOSS = 'Plain-language gloss';
export const PROFILES_CONV_TEMPLATES_ADVANCED = 'Advanced pattern options';
export const PROFILES_CONV_TEMPLATES_ADVANCED_HINT =
  'Optional compiled pattern for experts. Slot builder remains the default path.';
export const PROFILES_CONV_TEMPLATES_SKIP_CHIP = 'Skipped';
export const PROFILES_CONV_TEMPLATES_SELECT = 'Conversion rule';
export const PROFILES_CONV_TEMPLATES_SEARCH = 'Search conversion rules';
export const PROFILES_CONV_TEMPLATES_SEARCH_PLACEHOLDER =
  'Filter by name, group, or IWXXM block…';
export const PROFILES_CONV_TEMPLATES_CATALOG_HEADING = 'Rule catalog';
export const PROFILES_CONV_TEMPLATES_CATALOG_HELP =
  'Browse mined IWXXM schema groups. Select a rule to open a matching conversion token or focus the editor.';
export const PROFILES_CONV_TEMPLATES_CATALOG_EMPTY =
  'No catalog rules match this search.';
export const PROFILES_CONV_TEMPLATES_CATALOG_LOADING = 'Loading rule catalog…';
export const PROFILES_CONV_TEMPLATES_SLOT_LABEL = 'Slot name';
export const PROFILES_CONV_TEMPLATES_SAVE = 'Save changes';
export const PROFILES_CONV_TEMPLATES_READONLY =
  'Built-in rules are read-only. Fork to custom to rename slots or edit modes.';
export const PROFILES_CONV_TEMPLATES_SAVED = 'Saved.';
export const MAPPING_BRIDGE_HEADING = 'Mapping bridge';
export const MAPPING_BRIDGE_HELP =
  'See how a TAC group matches a conversion rule and the IWXXM block it produces.';
export const MAPPING_BRIDGE_COL_TAC = 'TAC report';
export const MAPPING_BRIDGE_COL_TEMPLATE = 'Template match';
export const MAPPING_BRIDGE_COL_IWXXM = 'IWXXM block';
export const MAPPING_BRIDGE_MATCHED = 'Matched';
export const MAPPING_BRIDGE_UNMATCHED = 'No matching conversion rule';
export const MAPPING_BRIDGE_UNMATCHED_HINT =
  'Every TAC group that maps to IWXXM needs an associated conversion rule. Unmatched groups fail closed.';
export const MAPPING_BRIDGE_EMPTY_IWXXM = 'Run preview to see the IWXXM block.';
export const PROFILES_GLOSSARY_HEADING = 'What these options mean';
export const PROFILES_GLOSSARY_PROFILE =
  'Base profile chooses the operational rule set and national extensions used for TAC lint, conversion, and IWXXM validation.';
export const PROFILES_GLOSSARY_EXCHANGE =
  'Exchange packaging describes how output is bundled for bulletin exchange. It does not select destinations or credentials.';
export const PROFILES_GLOSSARY_OVERLAY =
  'Libraries hold conversion, validation, dissemination, and decoding assets. Built-in defaults stay read-only until you fork a custom copy.';
export const PROFILES_OVERLAYS_HEADING = 'Signed overlays';
export const PROFILES_OVERLAYS_LOADING = 'Loading overlays…';
export const PROFILES_OVERLAYS_EMPTY = 'No overlays yet.';
export const PROFILES_OVERLAY_SLUG = 'Overlay short name';
export const PROFILES_OVERLAY_BASE = 'Base profile';
export const PROFILES_OVERLAY_BODY = 'Overlay JSON';
export const PROFILES_OVERLAY_SAVE = 'Save overlay';
export const PROFILES_OVERLAY_UPDATE = 'Update overlay';
export const PROFILES_OVERLAY_NEW = 'New overlay';
export const PROFILES_OVERLAY_DELETE = 'Delete overlay';
export const PROFILES_OVERLAY_HINT =
  'Overlays are signed on the server. Choose an overlay when converting to apply it.';
export const PROFILES_OVERLAYS_UNAVAILABLE =
  'Overlays unavailable right now. Try again after the profile service recovers.';
export const CONVERT_OVERLAY_LABEL = 'Signed overlay';
export const CONVERT_OVERLAY_NONE = 'None';
export const CONVERT_OVERLAY_HELP =
  'Optional saved overlay for this convert. Requires sign-in. Adds saved adjustments on top of the chosen Profile instead of replacing it.';
export const CONVERT_PRESET_LABEL = 'Semantic preset';
export const CONVERT_PRESET_NONE = 'None';
export const CONVERT_PRESET_HELP =
  'Optional saved preset for this convert. Applies saved profile defaults, but does not choose destinations or credentials.';
export const CONVERT_RESET_WMO_LIBRARY_DEFAULTS = 'Reset to WMO defaults';
export const CONVERT_RESET_WMO_LIBRARY_DEFAULTS_HELP =
  'Restore the ICAO / WMO baseline profile and matching built-in library selections on Convert.';
export const CONVERT_LIBRARY_HELP_DECODING =
  'Controls how TAC tokens are explained in the decode panel.';
export const CONVERT_LIBRARY_HELP_TAC_VALIDATION =
  'Controls TAC lint checks run before and with conversion.';
export const CONVERT_LIBRARY_HELP_IWXXM_VALIDATION =
  'Controls IWXXM output checks after conversion.';
export const CONVERT_LIBRARY_HELP_CONVERSION =
  'Controls how TAC is mapped into IWXXM for convert and export.';
export const CONVERT_LIBRARY_CATALOG_LINK = 'View rule catalog';
/**
 * Confirm copy when changing Convert national line / semantic profile.
 *
 * @param nationalLine - Target line id (plain language in message)
 */
export function CONVERT_PROFILE_LIBRARY_RESET_CONFIRM(nationalLine: string): string {
  return (
    `Change profile to ${nationalLine} and reset Decoding, TAC validation, ` +
    `IWXXM validation, and Conversion libraries to that line's defaults?`
  );
}
export const PROFILES_INSPECTOR_ACCESS_BUILTIN = 'Built-in (read-only default)';
export const PROFILES_INSPECTOR_STATUS_READY = 'Ready';
export const PROFILES_INSPECTOR_STATUS_DRAFT = 'Draft saved locally';
export const PROFILES_EDITOR_LOGIN_REQUIRED =
  'Sign in to open the conversion profiles inspector.';
export const PROFILES_EDITOR_SIGN_IN = 'Sign in';
export const PROFILES_INSPECTOR_HEADING = 'Catalog inspector';
export const PROFILES_INSPECTOR_LOADING = 'Loading catalog…';
export const PROFILES_INSPECTOR_EMPTY = 'No catalog profiles available.';
export const PROFILES_INSPECTOR_UNAVAILABLE =
  'Catalog unavailable right now. Try again after the profile service recovers.';
export const PROFILES_INSPECTOR_SELECT = 'Profile';
export const PROFILES_PROFILE_FAMILY = 'Profile family';
export const PROFILES_PROFILE_AUTHORITY = 'Authority';
export const PROFILES_PROFILE_COVERAGE = 'Coverage';
export const PROFILES_INSPECTOR_FAMILY_ICAO = 'ICAO / WMO baseline';
export const PROFILES_INSPECTOR_FAMILY_NATIONAL = 'National or regional extension';
export const PROFILES_INSPECTOR_AUTHORITY_ICAO = 'ICAO / WMO';
export const PROFILES_INSPECTOR_COVERAGE_UNAVAILABLE = 'Coverage details unavailable';
export const PROFILES_PACKS_HEADING = 'Rule packs';
export const PROFILES_PACKS_LOADING = 'Loading rule packs…';
export const PROFILES_PACKS_EMPTY = 'No rule packs yet.';
export const PROFILES_PACKS_UNAVAILABLE =
  'Rule packs unavailable right now. Try again after the profile service recovers.';
export const PROFILES_PACK_SLUG = 'Pack short name';
export const PROFILES_PACK_PROFILE = 'Applies to profile';
export const PROFILES_PACK_PRODUCT = 'Product';
export const PROFILES_PACK_STAGE = 'Stage';
export const PROFILES_PACK_SEVERITY = 'Severity';
export const PROFILES_PACK_WHEN = 'When';
export const PROFILES_PACK_MESSAGE = 'Message';
export const PROFILES_PACK_REF = 'Standard reference';
export const PROFILES_PACK_SAVE = 'Save pack';
export const PROFILES_PACK_UPDATE = 'Update pack';
export const PROFILES_PACK_NEW = 'New pack';
export const PROFILES_PACK_DELETE = 'Delete pack';
export const PROFILES_PACK_EXPORT = 'Export share bundle';
export const PROFILES_PACK_IMPORT = 'Import share bundle';
export const PROFILES_ERROR_PREFIX = 'Profiles error:';
export const PROFILES_COUNT_UNAVAILABLE = 'Unavailable';
export const PROFILES_PRESETS_HEADING = 'Semantic presets';
export const PROFILES_PRESETS_LOADING = 'Loading semantic presets…';
export const PROFILES_PRESETS_EMPTY = 'No semantic presets yet.';
export const PROFILES_PRESETS_UNAVAILABLE =
  'Semantic presets unavailable right now. Try again after the profile service recovers.';
export const PROFILES_PRESET_SLUG = 'Preset short name';
export const PROFILES_PRESET_NAME = 'Preset name';
export const PROFILES_PRESET_PROFILE = 'Semantic profile';
export const PROFILES_PRESET_IWXXM_VERSION = 'IWXXM version';
export const PROFILES_PRESET_REPORT_VARIANT = 'Report variant';
export const PROFILES_PRESET_OVERLAY = 'Signed overlay short name';
export const PROFILES_PRESET_SHARED = 'Shared with other signed-in operators';
export const PROFILES_PRESET_SAVE = 'Save preset';
export const PROFILES_PRESET_UPDATE = 'Update preset';
export const PROFILES_PRESET_NEW = 'New preset';
export const PROFILES_PRESET_DELETE = 'Delete preset';
export const PROFILES_TEMPLATES_HEADING = 'Dissemination templates';
export const PROFILES_TEMPLATES_LOADING = 'Loading dissemination templates…';
export const PROFILES_TEMPLATES_EMPTY = 'No dissemination templates yet.';
export const PROFILES_TEMPLATES_UNAVAILABLE =
  'Dissemination templates unavailable right now. Try again after the profile service recovers.';
export const PROFILES_TEMPLATE_SLUG = 'Template short name';
export const PROFILES_TEMPLATE_NAME = 'Template name';
export const PROFILES_TEMPLATE_SINK = 'Destination sink';
export const PROFILES_TEMPLATE_PRODUCT = 'Default product';
export const PROFILES_TEMPLATE_DDL = 'Create-if-missing by default';
export const PROFILES_TEMPLATE_PARAMS = 'Saved non-secret fields (JSON)';
export const PROFILES_TEMPLATE_SHARED = 'Shared with other signed-in operators';
export const PROFILES_TEMPLATE_SAVE = 'Save template';
export const PROFILES_TEMPLATE_UPDATE = 'Update template';
export const PROFILES_TEMPLATE_NEW = 'New template';
export const PROFILES_TEMPLATE_DELETE = 'Delete template';
export const PROFILES_TEMPLATE_HINT =
  'Templates save non-secret sink defaults only. Enter live credentials or destination URIs each time you send.';
export const DISSEMINATION_TEMPLATE_LABEL = 'Saved dissemination template';
export const DISSEMINATION_TEMPLATE_NONE = 'None';
export const DISSEMINATION_TEMPLATE_HELP =
  'Optional saved template for this send. It can prefill non-secret sink defaults, but it never stores credentials or destination URIs.';
export const PROFILES_WORKFLOWS_HEADING = 'Workflow references';
export const PROFILES_WORKFLOWS_BODY =
  'Workflow definitions are read-only in this screen. Open the current definitions or runtime details in a separate tab.';
export const PROFILES_WORKFLOWS_DEFINITIONS_LINK = 'Open workflow definitions';
export const PROFILES_WORKFLOWS_RUNTIME_LINK = 'Open workflow runtime';
export const PROFILES_WORKFLOWS_EXAMPLES_LINK = 'Open examples on Convert';
export const PROFILES_WORKFLOWS_DEFINITIONS_URL =
  'https://github.com/EMPIRIC2/TAC-to-IWXXM/tree/main/workflows';
export const PROFILES_WORKFLOWS_RUNTIME_URL =
  'https://github.com/EMPIRIC2/TAC-to-IWXXM/tree/main/packages/workflows';
export const PROFILES_EXAMPLES_HEADING = 'Examples';
export const PROFILES_EXAMPLES_PREFIX = 'Examples available on Convert:';
export const PROFILES_EXAMPLES_EMPTY =
  'No example products are listed for this profile yet.';
export const PROFILES_EXAMPLES_REUSE_NOTE =
  'Current examples are reused from the ICAO / WMO demo set and keep profile-specific notes in the picker.';

/** Profile builder control tooltips (plain language). */
export const PROFILES_TOOLTIP_LIBRARIES =
  'Five libraries hold conversion, validation, dissemination, and decoding assets. Built-in defaults stay read-only until you fork a custom copy.';
export const PROFILES_TOOLTIP_LIBRARY_TAB_CONVERSION =
  'Map TAC groups to IWXXM blocks with typed slots and optional decode-only or skip modes.';
export const PROFILES_TOOLTIP_LIBRARY_TAB_TAC_VALIDATION =
  'TAC lint rules that run before or alongside conversion for the selected profile line.';
export const PROFILES_TOOLTIP_LIBRARY_TAB_IWXXM_VALIDATION =
  'IWXXM schema and Schematron checks applied to converted output.';
export const PROFILES_TOOLTIP_LIBRARY_TAB_DISSEMINATION =
  'Ordered post-IWXXM transforms for bulletin exchange on Disseminate and Convert & Send.';
export const PROFILES_TOOLTIP_LIBRARY_TAB_DECODING =
  'Plain-language decode glossary entries shown when you enable live decode on Convert.';
export const PROFILES_TOOLTIP_LIBRARY_TAB_OVERVIEW =
  'Compare profiles and choose which products, file types, and IWXXM versions this profile enables.';
export const PROFILES_TOOLTIP_WORKBENCH =
  'Catalog lists assets; editor opens one item; optional IWXXM and validation previews stay off until you enable them.';
export const PROFILES_WORKBENCH_CATALOG_LABEL = 'Catalog';
export const PROFILES_WORKBENCH_EDITOR_LABEL = 'Editor';
export const PROFILES_WORKBENCH_PREVIEW_IWXXM = 'IWXXM preview';
export const PROFILES_WORKBENCH_PREVIEW_IWXXM_HELP =
  'Show a sample IWXXM fragment for the selected item. Off by default.';
export const PROFILES_WORKBENCH_PREVIEW_ISSUES = 'Validation issues preview';
export const PROFILES_WORKBENCH_PREVIEW_ISSUES_HELP =
  'Show lint or validation warnings and failures for the selected item. Off by default.';
export const PROFILES_WORKBENCH_PREVIEW_IWXXM_PLACEHOLDER =
  'IWXXM preview will appear here when sample data is available.';
export const PROFILES_WORKBENCH_PREVIEW_ISSUES_PLACEHOLDER =
  'Validation issues will appear here when sample data is available.';
export const PROFILES_OVERVIEW_HEADING = 'Overview';
export const PROFILES_OVERVIEW_HELP =
  'Compare two profiles and set which products, file types, and IWXXM versions the primary profile enables.';
export const PROFILES_OVERVIEW_COMPARE_HEADING = 'Profile compare';
export const PROFILES_OVERVIEW_ENABLEMENT_HEADING = 'Product enablement';
export const PROFILES_OVERVIEW_YAML_HEADING = 'Enablement YAML';
export const PROFILES_OVERVIEW_COMPARE_STUB =
  'Profile compare is available in the Overview compare panel.';
export const PROFILES_OVERVIEW_ENABLEMENT_STUB =
  'Product, file-type, and IWXXM version enablement is editable in the Overview enablement panel.';
export const PROFILES_TOOLTIP_INSPECTOR_PROFILE =
  'Choose a built-in semantic profile to inspect its catalog metadata and block wiring.';
export const PROFILES_TOOLTIP_INSPECTOR_COMPARE =
  'Optionally compare a second profile side by side to highlight product and IWXXM line differences.';
export const PROFILES_TOOLTIP_PROFILE_BLOCKS =
  'Step through how the selected profile wires input, lint, convert, validate, and exchange.';

/** Draft authoring shell copy. */
export const PROFILES_DRAFT_HEADING = 'Draft authoring';
export const PROFILES_DRAFT_HELP =
  'Start from a template, duplicate a built-in asset, or paste YAML. Save as a draft any time. Activate when Fail diagnostics are gone so Convert can use the library.';
export const PROFILES_DRAFT_NEW_TEMPLATE = 'New from template';
export const PROFILES_DRAFT_DUPLICATE = 'Duplicate built-in';
export const PROFILES_DRAFT_IMPORT_LABEL = 'Import YAML';
export const PROFILES_DRAFT_IMPORT_PLACEHOLDER =
  'Paste or edit YAML for this library kind. Invalid YAML stays in the editor until you fix it.';
export const PROFILES_DRAFT_SAVE = 'Save draft';
export const PROFILES_DRAFT_ACTIVATE = 'Activate';
export const PROFILES_DRAFT_STATUS_IDLE = 'Not saved';
export const PROFILES_DRAFT_STATUS_DRAFT = 'Draft';
export const PROFILES_DRAFT_STATUS_SAVED = 'Draft saved';
export const PROFILES_DRAFT_STATUS_ACTIVATED = 'Activated';
export const PROFILES_DRAFT_BLOCKS_HEADING = 'IWXXM blocks';
export const PROFILES_DRAFT_BLOCKS_HELP =
  'Named slots map TAC groups to IWXXM. Full slot rename and catalog search arrive in a later release.';
export const PROFILES_DRAFT_BLOCK_OBSERVATION = 'Observation';
export const PROFILES_DRAFT_BLOCK_CLOUD = 'Cloud';
export const PROFILES_DRAFT_BLOCK_RVR = 'Runway visual range';
export const PROFILES_DRAFT_CARD_WIND = 'Surface wind';
export const PROFILES_DRAFT_CARD_VISIBILITY = 'Visibility';
export const PROFILES_DRAFT_CARD_CLOUD_AMOUNT = 'Cloud amount';
export const PROFILES_DRAFT_CARD_RVR = 'RVR value';
export const PROFILES_DRAFT_TOOLTIP_NEW =
  'Load a starter YAML outline for this library kind.';
export const PROFILES_DRAFT_TOOLTIP_DUPLICATE =
  'Copy the selected built-in asset into a new draft you can edit.';
export const PROFILES_DRAFT_TOOLTIP_IMPORT =
  'Paste YAML from another environment or an exported share bundle.';
export const PROFILES_DRAFT_TOOLTIP_SAVE =
  'Save this YAML as a draft. Convert cannot use it until you activate.';
export const PROFILES_DRAFT_TOOLTIP_ACTIVATE =
  'Activate when YAML is valid and every regex compiles. Warn is allowed; Fail is not.';
export const PROFILES_DRAFT_DIAGNOSTICS_HEADING = 'Regex diagnostics';
export const PROFILES_DRAFT_DIAGNOSTICS_HELP =
  'Fail means the pattern does not compile or the required sample has no match. Warn means it compiles but may backtrack.';
export const PROFILES_DRAFT_CAPTURES_HEADING = 'Capture groups';
export const PROFILES_DRAFT_YAML_LOCK = 'Fix YAML before editing blocks or activating.';
export const PROFILES_DRAFT_ACTIVATE_BLOCKED =
  'Activate requires zero Fail diagnostics. Warn is allowed.';
export const PROFILES_DRAFT_SAMPLE_HEADING = 'Sample preview';
export const PROFILES_DRAFT_SAMPLE_HELP =
  'Paste a TAC, IWXXM, filename, or glossary sample for this library. Capture groups update as you type.';
export const PROFILES_DRAFT_SAMPLE_PLACEHOLDER =
  'Sample text for live match and capture summary';

export const PROFILES_TAC_RULES_HEADING = 'TAC validation rules';
export const PROFILES_TAC_RULES_HELP =
  'Search mined lint rules, set issue levels, and add custom regex with optional numeric bounds. Built-in catalogs stay read-only until you fork.';
export const PROFILES_TAC_RULES_SEARCH = 'Search rules';
export const PROFILES_TAC_RULES_SEARCH_PLACEHOLDER = 'Filter by id, code, or label…';
export const PROFILES_TAC_RULES_SELECT = 'Rule catalog';
export const PROFILES_TAC_RULES_IDENTITY = 'Rule id';
export const PROFILES_TAC_RULES_LABEL = 'Label';
export const PROFILES_TAC_RULES_SEVERITY = 'Issue level';
export const PROFILES_TAC_RULES_PATTERN = 'Regex pattern';
export const PROFILES_TAC_RULES_SAMPLE = 'Sample match';
export const PROFILES_TAC_RULES_ENABLED = 'Enabled';
export const PROFILES_TAC_RULES_CHECK_OP = 'Numeric check';
export const PROFILES_TAC_RULES_CHECK_VALUE = 'Check value';
export const PROFILES_TAC_RULES_CHECK_VALUES = 'Allowed values (comma-separated)';
export const PROFILES_TAC_RULES_CHECK_UNIT = 'Unit label';
export const PROFILES_TAC_RULES_CHECK_NONE = 'None';
export const PROFILES_TAC_RULES_ADD = 'Add custom rule';
export const PROFILES_TAC_RULES_FORK = 'Fork to edit';
export const PROFILES_TAC_RULES_SAVE = 'Save changes';
export const PROFILES_TAC_RULES_SAVED = 'Saved.';
export const PROFILES_TAC_RULES_READONLY =
  'Built-in TAC validation is read-only. Fork to create an editable copy.';
export const PROFILES_TAC_RULES_EMPTY = 'No rules match this search.';
export const PROFILES_TAC_RULES_LOADING = 'Loading TAC validation rules…';

export const PROFILES_IWXXM_RULES_HEADING = 'IWXXM validation asserts';
export const PROFILES_IWXXM_RULES_HELP =
  'Enable or disable Schematron asserts and add custom overlay rules. Built-in catalogs stay read-only until you fork.';
export const PROFILES_IWXXM_RULES_SEARCH = 'Search asserts';
export const PROFILES_IWXXM_RULES_SEARCH_PLACEHOLDER = 'Filter by id or label…';
export const PROFILES_IWXXM_RULES_SELECT = 'Assert catalog';
export const PROFILES_IWXXM_RULES_ENABLED = 'Enabled';
export const PROFILES_IWXXM_RULES_CONTEXT = 'Context';
export const PROFILES_IWXXM_RULES_TEST = 'Test';
export const PROFILES_IWXXM_RULES_ADD = 'Add custom overlay rule';
export const PROFILES_IWXXM_RULES_PATTERN = 'Regex or path';
export const PROFILES_IWXXM_RULES_FORK = 'Fork to edit';
export const PROFILES_IWXXM_RULES_SAVE = 'Save changes';
export const PROFILES_IWXXM_RULES_SAVED = 'Saved.';
export const PROFILES_IWXXM_RULES_READONLY =
  'Built-in IWXXM validation is read-only. Fork to create an editable copy.';
export const PROFILES_IWXXM_RULES_EMPTY = 'No asserts match this search.';
export const PROFILES_IWXXM_RULES_LOADING = 'Loading IWXXM validation asserts…';
export const PROFILES_IWXXM_RULES_CHECK_OP = 'Numeric check';
export const PROFILES_IWXXM_RULES_CHECK_VALUE = 'Check value';

/**
 * Operator-visible copy for ConversionProfile editor (EV-933 / F7.w).
 * Plain language only — no planning vocabulary.
 */

export const PROFILES_EDITOR_TITLE = 'Conversion profiles';
export const PROFILES_EDITOR_SUBTITLE =
  'Inspect catalog profiles, manage lint rule packs, save semantic presets, and keep reusable dissemination templates.';
export const PROFILES_GLOSSARY_HEADING = 'What these options mean';
export const PROFILES_GLOSSARY_PROFILE =
  'Semantic profile chooses the operational rule set and national extensions used for TAC lint, conversion, and IWXXM validation.';
export const PROFILES_GLOSSARY_EXCHANGE =
  'Exchange profile describes how output is packaged for bulletin exchange. It does not select destinations or credentials.';
export const PROFILES_GLOSSARY_OVERLAY =
  'Signed overlays are saved, server-signed JSON tweaks layered on top of a base profile. They let signed-in operators reuse approved profile adjustments without editing engine code.';
export const PROFILES_OVERLAYS_HEADING = 'Signed overlays';
export const PROFILES_OVERLAYS_LOADING = 'Loading overlays…';
export const PROFILES_OVERLAYS_EMPTY = 'No overlays yet.';
export const PROFILES_OVERLAY_SLUG = 'Overlay id';
export const PROFILES_OVERLAY_BASE = 'Base profile';
export const PROFILES_OVERLAY_BODY = 'Overlay JSON';
export const PROFILES_OVERLAY_SAVE = 'Save overlay';
export const PROFILES_OVERLAY_UPDATE = 'Update overlay';
export const PROFILES_OVERLAY_NEW = 'New overlay';
export const PROFILES_OVERLAY_DELETE = 'Delete overlay';
export const PROFILES_OVERLAY_HINT =
  'Overlays are signed on the server. Select an overlay id when converting to apply it.';
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
export const PROFILES_EDITOR_LOGIN_REQUIRED =
  'Sign in to open the conversion profiles editor.';
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
export const PROFILES_PACKS_HEADING = 'Rule packs';
export const PROFILES_PACKS_LOADING = 'Loading rule packs…';
export const PROFILES_PACKS_EMPTY = 'No rule packs yet.';
export const PROFILES_PACKS_UNAVAILABLE =
  'Rule packs unavailable right now. Try again after the profile service recovers.';
export const PROFILES_PACK_SLUG = 'Pack id';
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
export const PROFILES_PRESET_SLUG = 'Preset id';
export const PROFILES_PRESET_NAME = 'Preset name';
export const PROFILES_PRESET_PROFILE = 'Semantic profile';
export const PROFILES_PRESET_IWXXM_VERSION = 'IWXXM version';
export const PROFILES_PRESET_REPORT_VARIANT = 'Report variant';
export const PROFILES_PRESET_OVERLAY = 'Signed overlay id';
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
export const PROFILES_TEMPLATE_SLUG = 'Template id';
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

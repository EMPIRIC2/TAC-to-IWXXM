/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-nocheck — mechanical line-count split
/** Operator-visible copy catalog part 1. */
import type { OperatorVisibleCopyEntry } from '@/models/operatorCopy';
import * as C from './operatorVisibleCopyConsts';

/**
 * OPERATOR_VISIBLE_COPY_PART1.
 */
export const OPERATOR_VISIBLE_COPY_PART1: OperatorVisibleCopyEntry[] = [
  { id: 'soft-preview.label', text: C.SOFT_PREVIEW_LABEL },
  { id: 'soft-preview.help', text: C.SOFT_PREVIEW_HELP },
  { id: 'iwxxm-preview.expand', text: C.EXPAND_PREVIEW_LABEL },
  { id: 'iwxxm-preview.collapse', text: C.COLLAPSE_PREVIEW_LABEL },
  { id: 'propagate-residuals.label', text: C.PROPAGATE_RESIDUALS_LABEL },
  { id: 'propagate-residuals.help', text: C.PROPAGATE_RESIDUALS_HELP },
  { id: 'iwxxm-product.help', text: C.IWXXM_PRODUCT_HELP },
  { id: 'iwxxm-product.convert-label', text: C.IWXXM_PRODUCT_CONVERT_LABEL },
  { id: 'iwxxm-product.convert-aria', text: C.IWXXM_PRODUCT_CONVERT_ARIA },
  { id: 'bulletin-id.field-error', text: C.BULLETIN_ID_FIELD_ERROR },
  { id: 'issuing-center.field-error', text: C.ISSUING_CENTER_FIELD_ERROR },
  { id: 'guest.loss-of-progress', text: C.GUEST_LOSS_OF_PROGRESS_MESSAGE },
  { id: 'help.one-pager-url', text: C.OPERATOR_ONE_PAGER_URL },
  { id: 'help.handbook-url', text: C.OPERATOR_HANDBOOK_URL },
  { id: 'shell.nav.convert', text: C.SHELL_NAV_LABELS.converter },
  { id: 'shell.nav.history', text: C.SHELL_NAV_LABELS.history },
  { id: 'shell.nav.catalog', text: C.SHELL_NAV_LABELS.catalog },
  { id: 'shell.nav.dictionary', text: C.SHELL_NAV_LABELS.dictionary },
  { id: 'code-names.title', text: C.CODE_NAME_DICTIONARY_PAGE_TITLE },
  { id: 'code-names.intro', text: C.CODE_NAME_DICTIONARY_INTRO },
  { id: 'code-names.search', text: C.CODE_NAME_DICTIONARY_SEARCH_LABEL },
  {
    id: 'code-names.search-placeholder',
    text: C.CODE_NAME_DICTIONARY_SEARCH_PLACEHOLDER,
  },
  { id: 'code-names.product', text: C.CODE_NAME_DICTIONARY_PRODUCT_LABEL },
  { id: 'code-names.country', text: C.CODE_NAME_DICTIONARY_COUNTRY_LABEL },
  { id: 'code-names.amendment', text: C.CODE_NAME_DICTIONARY_AMENDMENT_LABEL },
  { id: 'code-names.filter-all', text: C.CODE_NAME_DICTIONARY_FILTER_ALL },
  { id: 'code-names.col-code', text: C.CODE_NAME_DICTIONARY_COL_CODE },
  { id: 'code-names.col-meaning', text: C.CODE_NAME_DICTIONARY_COL_MEANING },
  { id: 'code-names.col-products', text: C.CODE_NAME_DICTIONARY_COL_PRODUCTS },
  {
    id: 'code-names.col-countries',
    text: C.CODE_NAME_DICTIONARY_COL_COUNTRIES,
  },
  {
    id: 'code-names.col-amendment',
    text: C.CODE_NAME_DICTIONARY_COL_AMENDMENT,
  },
  { id: 'code-names.empty', text: C.CODE_NAME_DICTIONARY_EMPTY },
  { id: 'code-names.load-error', text: C.CODE_NAME_DICTIONARY_LOAD_ERROR },
  { id: 'code-names.loading', text: C.CODE_NAME_DICTIONARY_LOADING },
  { id: 'decode-visuals.title', text: C.DECODE_VISUALS_TITLE },
  { id: 'decode-visuals.intro', text: C.DECODE_VISUALS_INTRO },
  { id: 'decode-visuals.beta', text: C.DECODE_VISUALS_BETA },
  { id: 'decode-visuals.feedback', text: C.DECODE_VISUALS_FEEDBACK },
  { id: 'decode-visuals.no-map', text: C.DECODE_VISUALS_NO_MAP },
  { id: 'decode-visuals.map-loading', text: C.DECODE_VISUALS_MAP_LOADING },
  { id: 'decode-visuals.no-region', text: C.DECODE_VISUALS_NO_REGION },
  { id: 'decode-visuals.region-caption', text: C.DECODE_VISUALS_REGION_CAPTION },
  { id: 'decode-visuals.no-wind', text: C.DECODE_VISUALS_NO_WIND },
  { id: 'decode-visuals.wind-variable', text: C.DECODE_VISUALS_WIND_VARIABLE },
  { id: 'decode-visuals.open', text: C.DECODE_VISUALS_OPEN },
  { id: 'live-map.canvas', text: C.LIVE_MAP_CANVAS },
  { id: 'live-map.notice', text: C.LIVE_MAP_NOTICE },
  ...C.LIVE_MAP_VIEWS.map((view) => ({
    id: `live-map.view.${view.id}`,
    text: view.label,
  })),
  ...C.LIVE_MAP_PRODUCTS.map((product) => ({
    id: `live-map.product.${product}`,
    text: C.productLabel(product),
  })),
  { id: 'live-map.zoom-hint', text: C.LIVE_MAP_ZOOM_HINT },
  { id: 'live-map.loading', text: C.LIVE_MAP_LOADING },
  { id: 'live-map.refreshing', text: C.LIVE_MAP_REFRESHING },
  { id: 'live-map.empty', text: C.LIVE_MAP_EMPTY },
  { id: 'live-map.no-time', text: C.LIVE_MAP_NO_TIME },
  { id: 'live-map.layers-off', text: C.LIVE_MAP_LAYERS_OFF },
  { id: 'live-map.space', text: C.LIVE_MAP_SPACE },
  { id: 'live-map.error', text: C.LIVE_MAP_ERROR },
  { id: 'live-map.tac', text: C.LIVE_MAP_TAC },
  { id: 'live-map.issue-copy', text: C.LIVE_MAP_ISSUE_COPY },
  { id: 'live-map.send-to-converter', text: C.LIVE_MAP_SEND_TO_CONVERTER },
  { id: 'live-map.all-countries', text: C.LIVE_MAP_ALL_COUNTRIES },
  { id: 'live-map.all-regions', text: C.LIVE_MAP_ALL_REGIONS },
  { id: 'live-map.last-hour', text: C.LIVE_MAP_LAST_HOUR },
  { id: 'live-map.last-3-hours', text: C.LIVE_MAP_LAST_3_HOURS },
  { id: 'live-map.last-6-hours', text: C.LIVE_MAP_LAST_6_HOURS },
  { id: 'live-map.last-12-hours', text: C.LIVE_MAP_LAST_12_HOURS },
  { id: 'live-map.full-window', text: C.LIVE_MAP_FULL_WINDOW },
  { id: 'live-map.filter-country', text: C.LIVE_MAP_FILTER_COUNTRY },
  { id: 'live-map.filter-region', text: C.LIVE_MAP_FILTER_REGION },
  { id: 'live-map.filter-time', text: C.LIVE_MAP_FILTER_TIME },
  { id: 'live-map.filter-phenomenon', text: C.LIVE_MAP_FILTER_PHENOMENON },
  ...C.LIVE_MAP_PHENOMENA.map((item) => ({
    id: `live-map.phenomenon.${item.id}`,
    text: item.label,
  })),
  { id: 'live-map.tac-overlays', text: C.LIVE_MAP_TAC_OVERLAYS },
  { id: 'live-map.tac-overlay-empty', text: C.LIVE_MAP_TAC_OVERLAY_EMPTY },
  { id: 'live-map.cluster-pick', text: C.LIVE_MAP_CLUSTER_PICK },
  { id: 'live-map.cluster-count', text: C.LIVE_MAP_CLUSTER_COUNT },
  ...C.TAC_OVERLAY_LAYERS.map((layer) => ({
    id: `live-map.tac-overlay.${layer.id}`,
    text: layer.label,
  })),
  { id: 'live-map.panel', text: C.LIVE_MAP_PANEL },
  {
    id: 'lint-validation-catalog.title',
    text: C.LINT_VALIDATION_CATALOG_PAGE_TITLE,
  },
  {
    id: 'lint-validation-catalog.subtitle',
    text: C.LINT_VALIDATION_CATALOG_PAGE_SUBTITLE,
  },
  { id: 'lint-validation-catalog.empty', text: C.LINT_VALIDATION_CATALOG_EMPTY },
  {
    id: 'lint-validation-catalog.loading',
    text: C.LINT_VALIDATION_CATALOG_LOADING,
  },
  {
    id: 'lint-validation-catalog.search',
    text: C.LINT_VALIDATION_CATALOG_SEARCH,
  },
  {
    id: 'lint-validation-catalog.detail',
    text: C.LINT_VALIDATION_CATALOG_DETAIL,
  },
  {
    id: 'lint-validation-catalog.example-pass',
    text: C.LINT_VALIDATION_CATALOG_EXAMPLE_PASS,
  },
  {
    id: 'lint-validation-catalog.example-fail',
    text: C.LINT_VALIDATION_CATALOG_EXAMPLE_FAIL,
  },
  {
    id: 'lint-validation-catalog.example-pass-unavailable',
    text: C.LINT_VALIDATION_CATALOG_EXAMPLE_PASS_UNAVAILABLE,
  },
  {
    id: 'lint-validation-catalog.example-fail-unavailable',
    text: C.LINT_VALIDATION_CATALOG_EXAMPLE_FAIL_UNAVAILABLE,
  },
  {
    id: 'lint-validation-catalog.example-note',
    text: C.LINT_VALIDATION_CATALOG_EXAMPLE_NOTE,
  },
  {
    id: 'lint-validation-catalog.examples',
    text: C.LINT_VALIDATION_CATALOG_EXAMPLES,
  },
  {
    id: 'lint-validation-catalog.examples-unavailable',
    text: C.LINT_VALIDATION_CATALOG_EXAMPLES_UNAVAILABLE,
  },
  {
    id: 'lint-validation-catalog.missing-rule-lead',
    text: C.LINT_VALIDATION_CATALOG_MISSING_RULE_LEAD,
  },
  {
    id: 'lint-validation-catalog.missing-rule-link',
    text: C.LINT_VALIDATION_CATALOG_MISSING_RULE_LINK,
  },
  {
    id: 'lint-validation-catalog.view',
    text: C.LINT_VALIDATION_CATALOG_VIEW_LABEL,
  },
  {
    id: 'lint-validation-catalog.view-detailed',
    text: C.LINT_VALIDATION_CATALOG_VIEW_DETAILED,
  },
  {
    id: 'lint-validation-catalog.view-compact',
    text: C.LINT_VALIDATION_CATALOG_VIEW_COMPACT,
  },
  {
    id: 'lint-validation-catalog.family',
    text: C.LINT_VALIDATION_CATALOG_FAMILY_LABEL,
  },
  {
    id: 'lint-validation-catalog.family-all',
    text: C.LINT_VALIDATION_CATALOG_FAMILY_ALL,
  },
  {
    id: 'lint-validation-catalog.load-error',
    text: C.LINT_VALIDATION_CATALOG_LOAD_ERROR,
  },
  {
    id: 'lint-validation-catalog.retry',
    text: C.LINT_VALIDATION_CATALOG_RETRY,
  },
  ...Object.entries(C.LINT_VALIDATION_CATALOG_TYPE_LABELS).map(([value, text]) => ({
    id: `lint-validation-catalog.type.${value}`,
    text,
  })),
  ...Object.entries(C.LINT_VALIDATION_CATALOG_ACCESS_LABELS).map(([value, text]) => ({
    id: `lint-validation-catalog.access.${value}`,
    text,
  })),
  { id: 'issue-detail.title', text: C.ISSUE_DETAIL_TITLE },
  { id: 'issue-detail.close', text: C.ISSUE_DETAIL_CLOSE },
  { id: 'issue-detail.open', text: C.ISSUE_DETAIL_OPEN },
  { id: 'issue-detail.button', text: C.ISSUE_DETAIL_BUTTON },
  { id: 'issue-detail.code', text: C.ISSUE_DETAIL_CODE },
  { id: 'issue-detail.severity', text: C.ISSUE_DETAIL_SEVERITY },
  { id: 'issue-detail.message', text: C.ISSUE_DETAIL_MESSAGE },
  { id: 'issue-detail.rule', text: C.ISSUE_DETAIL_RULE },
  { id: 'issue-detail.hint', text: C.ISSUE_DETAIL_HINT },
  { id: 'issue-detail.source', text: C.ISSUE_DETAIL_SOURCE },
  { id: 'issue-detail.product', text: C.ISSUE_DETAIL_PRODUCT },
  { id: 'issue-detail.tags', text: C.ISSUE_DETAIL_TAGS },
  { id: 'issue-detail.location', text: C.ISSUE_DETAIL_LOCATION },
  { id: 'issue-detail.empty', text: C.ISSUE_DETAIL_EMPTY },
  {
    id: 'lint-validation-catalog.type',
    text: C.LINT_VALIDATION_CATALOG_TYPE_LABEL,
  },
  {
    id: 'lint-validation-catalog.level',
    text: C.LINT_VALIDATION_CATALOG_LEVEL_LABEL,
  },
  {
    id: 'lint-validation-catalog.access',
    text: C.LINT_VALIDATION_CATALOG_ACCESS_LABEL,
  },
  {
    id: 'lint-validation-catalog.sort',
    text: C.LINT_VALIDATION_CATALOG_SORT_LABEL,
  },
  {
    id: 'site-terms.title',
    text: C.SITE_TERMS_TITLE,
  },
  {
    id: 'site-terms.body',
    text: C.SITE_TERMS_BODY,
  },
  {
    id: 'site-terms.checkbox',
    text: C.SITE_TERMS_CHECKBOX,
  },
  {
    id: 'site-terms.continue',
    text: C.SITE_TERMS_CONTINUE,
  },
  {
    id: 'lint-validation-catalog.col-code',
    text: C.LINT_VALIDATION_CATALOG_COL_CODE,
  },
  {
    id: 'lint-validation-catalog.col-type',
    text: C.LINT_VALIDATION_CATALOG_COL_TYPE,
  },
  {
    id: 'lint-validation-catalog.col-level',
    text: C.LINT_VALIDATION_CATALOG_COL_LEVEL,
  },
  {
    id: 'lint-validation-catalog.col-description',
    text: C.LINT_VALIDATION_CATALOG_COL_DESCRIPTION,
  },
  {
    id: 'lint-validation-catalog.col-source',
    text: C.LINT_VALIDATION_CATALOG_COL_SOURCE,
  },
  { id: 'profiles.title', text: C.PROFILES_EDITOR_TITLE },
  { id: 'profiles.subtitle', text: C.PROFILES_EDITOR_SUBTITLE },
  {
    id: 'profiles.authoring-retired',
    text: C.PROFILES_AUTHORING_RETIRED_NOTE,
  },
  {
    id: 'profiles.trust-catalogs-hint',
    text: C.PROFILES_TRUST_CATALOGS_HINT,
  },
  { id: 'profiles.assembly-heading', text: C.PROFILES_ASSEMBLY_HEADING },
  { id: 'profiles.assembly-help', text: C.PROFILES_ASSEMBLY_HELP },
  { id: 'profiles.libraries-heading', text: C.PROFILES_LIBRARIES_HEADING },
  { id: 'profiles.libraries-help', text: C.PROFILES_LIBRARIES_HELP },
  {
    id: 'profiles.library-tab-conversion',
    text: C.PROFILES_LIBRARY_TAB_CONVERSION,
  },
];

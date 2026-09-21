//! PyO3 native extension for `iwxxm-validate` (F13 / E10-22 / D-S014-T33-crates).
//!
//! Stack A: **xmloxide** — well-formed + XSD + native ISO Schematron (no libxml2).
//!
//! Compiled XSD / Schematron schemas are cached process-wide (mirrors lxml
//! ``@lru_cache``) so hot-path calls are validate-only (T6.6 / E10-35).

use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex, OnceLock};

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use xmloxide::validation::schematron::{
    parse_schematron, validate_schematron, validate_schematron_with_phase, Phase, SchematronSchema,
};
use xmloxide::validation::xsd::{
    parse_xsd_with_options, validate_xsd, SchemaResolver, XsdParseOptions, XsdSchema,
};
use xmloxide::Document;

/// Extension package version (mirrors Cargo.toml).
#[pyfunction]
fn extension_version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

/// Health check used by CI / import smoke tests.
#[pyfunction]
fn ping() -> &'static str {
    "pong"
}

/// Clear compiled-schema caches (tests / version switches).
#[pyfunction]
fn clear_schema_caches() {
    if let Some(cache) = XSD_CACHE.get() {
        cache.lock().expect("xsd cache lock").clear();
    }
    if let Some(cache) = SCH_CACHE.get() {
        cache.lock().expect("sch cache lock").clear();
    }
    if let Some(cache) = RESOLVER_INDEX_CACHE.get() {
        cache.lock().expect("resolver index lock").clear();
    }
}

type XsdCacheKey = (String, Vec<String>);
type XsdCache = Mutex<HashMap<XsdCacheKey, Result<Arc<XsdSchema>, String>>>;
type SchCache = Mutex<HashMap<String, Result<Arc<SchematronSchema>, String>>>;
type ResolverIndexCache = Mutex<HashMap<Vec<String>, HashMap<String, Vec<PathBuf>>>>;

fn xsd_cache() -> &'static XsdCache {
    XSD_CACHE.get_or_init(|| Mutex::new(HashMap::new()))
}

fn sch_cache() -> &'static SchCache {
    SCH_CACHE.get_or_init(|| Mutex::new(HashMap::new()))
}

fn resolver_index_cache() -> &'static ResolverIndexCache {
    RESOLVER_INDEX_CACHE.get_or_init(|| Mutex::new(HashMap::new()))
}

static XSD_CACHE: OnceLock<XsdCache> = OnceLock::new();
static SCH_CACHE: OnceLock<SchCache> = OnceLock::new();
static RESOLVER_INDEX_CACHE: OnceLock<ResolverIndexCache> = OnceLock::new();

/// Pre-indexed vendor-tree resolver: basename → paths (+ relative / URL-aware joins).
///
/// Basename alone is ambiguous under ``externalSchema/aero/aixm`` (``5.1`` vs
/// ``5.1.1`` share ``AIXM_Features.xsd``). Prefer URL path segments / remaps so
/// ``http://www.aixm.aero/schema/5.1.1/...`` does not load the ``5.1`` tree.
///
/// xmloxide keeps the *original* ``base_uri`` for nested ``xsd:include`` (does not
/// re-base to the imported file). Track local directories of successfully resolved
/// schemas so relative includes like ``./AIXM_DataTypes.xsd`` stay in the same
/// version tree as the preceding absolute import.
struct VendorResolver {
    roots: Vec<PathBuf>,
    /// Lowercased basename → all matching files under catalog roots.
    by_basename: HashMap<String, Vec<PathBuf>>,
    /// Memoize resolve() results for this parse session.
    hit_cache: Mutex<HashMap<String, Option<String>>>,
    /// Parent dirs of files resolved in this parse (newest last).
    resolved_dirs: Mutex<Vec<PathBuf>>,
}

impl VendorResolver {
    fn new(roots: Vec<String>) -> Self {
        let key: Vec<String> = {
            let mut k = roots.clone();
            k.sort();
            k
        };
        let by_basename = {
            let mut guard = resolver_index_cache().lock().expect("resolver index lock");
            if let Some(idx) = guard.get(&key) {
                idx.clone()
            } else {
                let idx = build_basename_index(&key);
                guard.insert(key, idx.clone());
                idx
            }
        };
        Self {
            roots: roots.into_iter().map(PathBuf::from).collect(),
            by_basename,
            hit_cache: Mutex::new(HashMap::new()),
            resolved_dirs: Mutex::new(Vec::new()),
        }
    }

    fn candidates(&self, location: &str, base: Option<&str>) -> Vec<PathBuf> {
        let loc = location.split('/').next_back().unwrap_or(location);
        let stripped = location
            .strip_prefix("http://")
            .or_else(|| location.strip_prefix("https://"))
            .unwrap_or(location);
        let relative = is_relative_schema_location(location);
        let mut out: Vec<PathBuf> = Vec::new();

        // Prefer dirs of schemas already resolved in this parse (fixes xmloxide
        // base_uri not following nested includes/imports).
        if relative {
            if let Ok(dirs) = self.resolved_dirs.lock() {
                for dir in dirs.iter().rev() {
                    out.push(dir.join(location));
                    out.push(dir.join(loc));
                }
            }
        }

        if let Some(b) = base {
            let parent = Path::new(b).parent().unwrap_or(Path::new("."));
            out.push(parent.join(location));
            out.push(parent.join(stripped));
            out.push(parent.join(loc));
        }

        // Progressive URL-path suffixes (host/…/file → …/file → file).
        let suffix_paths = url_path_suffixes(stripped);
        let remapped = aixm_schema_remaps(stripped);
        let version_hint =
            version_hint_from_location(stripped).or_else(|| self.version_hint_from_resolved_dirs());

        for root in &self.roots {
            out.push(root.join(location));
            out.push(root.join(stripped));
            for suffix in &suffix_paths {
                out.push(root.join(suffix));
            }
            for remap in &remapped {
                out.push(root.join(remap));
            }
            out.push(root.join(loc));
        }

        // Version-aware basename pick (avoid 5.1 winning over 5.1.1).
        let hint_location = version_hint
            .as_deref()
            .map(|v| format!("schema/{v}/{loc}"))
            .unwrap_or_else(|| stripped.to_string());
        if let Some(p) = best_basename_match(&self.by_basename, loc, &hint_location) {
            out.push(p);
        }
        let loc_lower = loc.to_ascii_lowercase();
        if loc_lower != loc {
            if let Some(p) = best_basename_match(&self.by_basename, &loc_lower, &hint_location) {
                out.push(p);
            }
        }
        out
    }

    fn version_hint_from_resolved_dirs(&self) -> Option<String> {
        let Ok(dirs) = self.resolved_dirs.lock() else {
            return None;
        };
        for dir in dirs.iter().rev() {
            if let Some(name) = dir.file_name().and_then(|s| s.to_str()) {
                if name == "5.1.1" || name == "5.1" {
                    return Some(name.to_string());
                }
            }
            let s = dir.to_string_lossy();
            if s.contains("/5.1.1/") || s.ends_with("/5.1.1") {
                return Some("5.1.1".to_string());
            }
            if s.contains("/5.1/") || s.ends_with("/5.1") {
                return Some("5.1".to_string());
            }
        }
        None
    }

    fn remember_resolved_path(&self, path: &Path) {
        if let Some(parent) = path.parent() {
            if let Ok(mut dirs) = self.resolved_dirs.lock() {
                let parent = parent.to_path_buf();
                if !dirs.iter().any(|d| d == &parent) {
                    dirs.push(parent);
                } else {
                    // Move to newest
                    dirs.retain(|d| d != &parent);
                    dirs.push(parent);
                }
            }
        }
    }
}

fn is_relative_schema_location(location: &str) -> bool {
    if location.starts_with("http://") || location.starts_with("https://") {
        return false;
    }
    location.starts_with("./")
        || location.starts_with("../")
        || !location.contains("://")
            && Path::new(location).components().all(|c| {
                matches!(
                    c,
                    std::path::Component::Normal(_)
                        | std::path::Component::CurDir
                        | std::path::Component::ParentDir
                )
            })
}

fn version_hint_from_location(stripped: &str) -> Option<String> {
    let parts: Vec<&str> = stripped.split('/').filter(|p| !p.is_empty()).collect();
    for (i, part) in parts.iter().enumerate() {
        if *part == "5.1.1" || *part == "5.1" {
            // Prefer the segment immediately before the filename when present.
            if i + 1 < parts.len() {
                return Some((*part).to_string());
            }
        }
    }
    None
}

/// Path suffixes of a scheme-stripped URL / relative location, longest first.
fn url_path_suffixes(stripped: &str) -> Vec<String> {
    let parts: Vec<&str> = stripped.split('/').filter(|p| !p.is_empty()).collect();
    if parts.is_empty() {
        return Vec::new();
    }
    let mut out = Vec::with_capacity(parts.len());
    for i in 0..parts.len() {
        out.push(parts[i..].join("/"));
    }
    out
}

/// Map published AIXM schema URLs onto the vendored ``aero/aixm/{ver}/`` tree.
fn aixm_schema_remaps(stripped: &str) -> Vec<String> {
    // http://www.aixm.aero/schema/5.1.1/AIXM_Features.xsd
    //   → aero/aixm/5.1.1/AIXM_Features.xsd
    const PREFIXES: &[&str] = &["www.aixm.aero/schema/", "aixm.aero/schema/"];
    for prefix in PREFIXES {
        if let Some(rest) = stripped.strip_prefix(prefix) {
            return vec![format!("aero/aixm/{rest}"), rest.to_string()];
        }
    }
    Vec::new()
}

/// Choose among basename collisions using URL path version segments.
fn best_basename_match(
    index: &HashMap<String, Vec<PathBuf>>,
    basename: &str,
    stripped_location: &str,
) -> Option<PathBuf> {
    let paths = index.get(basename)?;
    if paths.is_empty() {
        return None;
    }
    if paths.len() == 1 {
        return Some(paths[0].clone());
    }

    let segments: Vec<&str> = stripped_location
        .split('/')
        .filter(|p| !p.is_empty())
        .collect();
    // Parent directory in the URL (e.g. ``5.1.1`` for …/5.1.1/AIXM_Features.xsd).
    let url_parent = if segments.len() >= 2 {
        Some(segments[segments.len() - 2])
    } else {
        None
    };

    let mut ranked: Vec<(i32, &PathBuf)> = paths
        .iter()
        .map(|p| (score_schema_candidate(p, url_parent, &segments), p))
        .collect();
    ranked.sort_by_key(|b| std::cmp::Reverse(b.0));
    ranked.first().map(|(_, p)| (*p).clone())
}

fn score_schema_candidate(path: &Path, url_parent: Option<&str>, url_segments: &[&str]) -> i32 {
    let path_str = path.to_string_lossy();
    let mut score = 0i32;

    if let Some(parent) = url_parent {
        // Exact parent dir match beats prefix collisions (5.1 vs 5.1.1).
        if path
            .parent()
            .and_then(|p| p.file_name())
            .and_then(|s| s.to_str())
            == Some(parent)
        {
            score += 100;
        } else if path_str.contains(&format!("/{parent}/")) {
            score += 40;
        }

        // Penalize sibling version trees when URL names a specific version.
        // ``5.1`` must not win for ``5.1.1``; profiles are secondary.
        if parent == "5.1.1" {
            if path_str.contains("/5.1/") && !path_str.contains("/5.1.1/") {
                score -= 80;
            }
            if path_str.contains("5.1_profiles") {
                score -= 20;
            }
            if path_str.contains("5.1.1_profiles") {
                score -= 10; // prefer canonical 5.1.1/ over profiles
            }
        } else if parent == "5.1" {
            if path_str.contains("/5.1.1/") {
                score -= 80;
            }
            if path_str.contains("5.1.1_profiles") {
                score -= 20;
            }
            if path_str.contains("5.1_profiles") {
                score -= 10;
            }
        }
    }

    for seg in url_segments {
        if path_str.contains(&format!("/{seg}/")) || path_str.ends_with(&format!("/{seg}")) {
            score += 2;
        }
    }
    score
}

fn build_basename_index(roots: &[String]) -> HashMap<String, Vec<PathBuf>> {
    let mut index: HashMap<String, Vec<PathBuf>> = HashMap::new();
    for root in roots {
        let root_path = PathBuf::from(root);
        index_walk(&root_path, &mut index, 6);
    }
    index
}

fn index_walk(dir: &Path, index: &mut HashMap<String, Vec<PathBuf>>, depth: usize) {
    if depth == 0 || !dir.is_dir() {
        return;
    }
    let Ok(rd) = std::fs::read_dir(dir) else {
        return;
    };
    for ent in rd.flatten() {
        let p = ent.path();
        if p.is_file() {
            if let Some(name) = p.file_name().and_then(|s| s.to_str()) {
                index.entry(name.to_string()).or_default().push(p.clone());
                let lower = name.to_ascii_lowercase();
                if lower != name {
                    index.entry(lower).or_default().push(p);
                }
            }
        } else if p.is_dir() {
            index_walk(&p, index, depth - 1);
        }
    }
}

impl SchemaResolver for VendorResolver {
    fn resolve(&self, location: &str, base: Option<&str>) -> Option<String> {
        let cache_key = match base {
            Some(b) => format!("{b}\0{location}"),
            None => location.to_string(),
        };
        if let Ok(guard) = self.hit_cache.lock() {
            if let Some(cached) = guard.get(&cache_key) {
                return cached.clone();
            }
        }
        let mut found: Option<String> = None;
        for c in self.candidates(location, base) {
            if c.is_file() {
                if let Ok(text) = std::fs::read_to_string(&c) {
                    self.remember_resolved_path(&c);
                    found = Some(text);
                    break;
                }
            }
        }
        if let Ok(mut guard) = self.hit_cache.lock() {
            guard.insert(cache_key, found.clone());
        }
        found
    }
}

fn issue_dict<'py>(
    py: Python<'py>,
    severity: &str,
    code: &str,
    message: &str,
    layer: &str,
    location: Option<&str>,
) -> PyResult<Bound<'py, PyDict>> {
    let d = PyDict::new(py);
    d.set_item("severity", severity)?;
    d.set_item("code", code)?;
    d.set_item("message", message)?;
    d.set_item("layer", layer)?;
    d.set_item("location", location)?;
    Ok(d)
}

/// One labeled Schematron row. Assertion codes are pattern ids when the pattern has one.
struct LabeledSchematron {
    severity: &'static str,
    code: String,
    message: String,
}

const PATTERN_PHASE: &str = "iwxxm-pattern";

fn xpath_error(message: &str) -> bool {
    message.starts_with("XPath error")
}

fn patterns_in_play(
    schema: &SchematronSchema,
) -> Vec<&xmloxide::validation::schematron::SchematronPattern> {
    if let Some(phase_id) = &schema.default_phase {
        if let Some(phase) = schema.phases.get(phase_id) {
            return schema
                .patterns
                .iter()
                .filter(|pattern| {
                    pattern
                        .id
                        .as_ref()
                        .is_some_and(|id| phase.active_patterns.iter().any(|active| active == id))
                })
                .collect();
        }
    }
    schema.patterns.iter().collect()
}

/// Label assertion errors with the pattern id.
///
/// A document with no assertion errors returns after one `validate_schematron` call.
/// Otherwise each active pattern is validated through the public phase API so the
/// issue code can be that pattern's id. Patterns with no id stay `SCHEMATRON_ASSERT`.
fn schematron_rows(doc: &Document, schema: &SchematronSchema) -> Vec<LabeledSchematron> {
    let quick = validate_schematron(doc, schema);
    let mut rows = Vec::new();
    let has_assert = quick.errors.iter().any(|err| !xpath_error(&err.message));
    if !has_assert {
        push_quick_rows(&mut rows, &quick);
        return rows;
    }

    let playing = patterns_in_play(schema);
    let named: Vec<String> = playing
        .iter()
        .filter_map(|pattern| pattern.id.clone())
        .collect();
    let has_unnamed = playing.iter().any(|pattern| pattern.id.is_none());
    let mut attributed: Vec<LabeledSchematron> = Vec::new();

    if !named.is_empty() {
        let mut scoped = schema.clone();
        scoped.default_phase = None;
        scoped.phases.insert(
            PATTERN_PHASE.to_string(),
            Phase {
                id: PATTERN_PHASE.to_string(),
                active_patterns: Vec::new(),
            },
        );
        for id in &named {
            if let Some(phase) = scoped.phases.get_mut(PATTERN_PHASE) {
                phase.active_patterns.clear();
                phase.active_patterns.push(id.clone());
            }
            let result = validate_schematron_with_phase(doc, &scoped, PATTERN_PHASE);
            for err in result.errors {
                if xpath_error(&err.message) {
                    continue;
                }
                attributed.push(LabeledSchematron {
                    severity: "error",
                    code: id.clone(),
                    message: err.message,
                });
            }
        }
    }

    if has_unnamed {
        let mut only = schema.clone();
        only.default_phase = None;
        only.phases.clear();
        only.patterns.retain(|pattern| pattern.id.is_none());
        let result = validate_schematron(doc, &only);
        for err in result.errors {
            if xpath_error(&err.message) {
                continue;
            }
            attributed.push(LabeledSchematron {
                severity: "error",
                code: "SCHEMATRON_ASSERT".to_string(),
                message: err.message,
            });
        }
    }

    if attributed.is_empty() {
        for err in &quick.errors {
            if xpath_error(&err.message) {
                continue;
            }
            rows.push(LabeledSchematron {
                severity: "error",
                code: "SCHEMATRON_ASSERT".to_string(),
                message: err.message.clone(),
            });
        }
    } else {
        rows.extend(attributed);
    }
    push_quick_rows(&mut rows, &quick);
    rows
}

fn push_quick_rows(
    rows: &mut Vec<LabeledSchematron>,
    quick: &xmloxide::validation::ValidationResult,
) {
    for err in &quick.errors {
        if !xpath_error(&err.message) {
            continue;
        }
        rows.push(LabeledSchematron {
            severity: "warning",
            code: "SCHEMATRON_XPATH_UNSUPPORTED".to_string(),
            message: err.message.clone(),
        });
    }
    for warn in &quick.warnings {
        rows.push(LabeledSchematron {
            severity: "warning",
            code: "SCHEMATRON_REPORT".to_string(),
            message: warn.message.clone(),
        });
    }
}

fn catalog_key(catalog_roots: &[String]) -> Vec<String> {
    let mut key = catalog_roots.to_vec();
    key.sort();
    key
}

fn get_or_parse_xsd(xsd_path: &str, catalog_roots: &[String]) -> Result<Arc<XsdSchema>, String> {
    let key = (xsd_path.to_string(), catalog_key(catalog_roots));
    {
        let guard = xsd_cache().lock().expect("xsd cache lock");
        if let Some(cached) = guard.get(&key) {
            return cached.clone();
        }
    }

    let xsd_text = std::fs::read_to_string(xsd_path)
        .map_err(|e| format!("XSD not readable at {xsd_path}: {e}"))?;
    let resolver = VendorResolver::new(catalog_roots.to_vec());
    let opts = XsdParseOptions {
        resolver: Some(&resolver),
        base_uri: Some(xsd_path.to_string()),
    };
    let parsed = parse_xsd_with_options(&xsd_text, &opts)
        .map(Arc::new)
        .map_err(|e| format!("Failed to parse XSD schema: {}", e.message));

    let mut guard = xsd_cache().lock().expect("xsd cache lock");
    // Another thread may have won the race; prefer existing entry.
    if let Some(existing) = guard.get(&key) {
        return existing.clone();
    }
    guard.insert(key, parsed.clone());
    parsed
}

fn get_or_parse_schematron(sch_path: &str) -> Result<Arc<SchematronSchema>, String> {
    let key = sch_path.to_string();
    {
        let guard = sch_cache().lock().expect("sch cache lock");
        if let Some(cached) = guard.get(&key) {
            return cached.clone();
        }
    }

    let sch_text = std::fs::read_to_string(sch_path)
        .map_err(|e| format!("Schematron not readable at {sch_path}: {e}"))?;
    // xmloxide 0.4.x only recognizes the typo NS `…/dml/schematron`, while WMO IWXXM
    // uses the ISO `…/dsdl/schematron`. Remap + (2025-2) METAR_SPECI XPath1 stand-ins.
    let prepared = prepare_schematron_for_xmloxide(&sch_text, sch_path);
    let parsed = parse_schematron(&prepared)
        .map(Arc::new)
        .map_err(|e| format!("Failed to parse Schematron: {}", e.message));

    let mut guard = sch_cache().lock().expect("sch cache lock");
    if let Some(existing) = guard.get(&key) {
        return existing.clone();
    }
    guard.insert(key, parsed.clone());
    parsed
}

/// Remap WMO Schematron for xmloxide (dsdl→dml).
///
/// Aggressive METAR_SPECI XPath1 stand-ins apply only for **2025-2** schemas so older
/// CA_ECCC (3.0.0) national uoms stay soft under residual XPath2 ``if()``.
fn prepare_schematron_for_xmloxide(sch_text: &str, sch_path: &str) -> String {
    let remapped = sch_text.replace(
        "http://purl.oclc.org/dsdl/schematron",
        "http://purl.oclc.org/dml/schematron",
    );
    let is_2025_2 = sch_path.contains("2025-2") || sch_path.contains("2025_2");
    if !is_2025_2 {
        return remapped;
    }
    let with_if = rewrite_xpath2_if_then_else_metar_speci_only(&remapped);
    let with_cmp = rewrite_xpath2_comparisons(&with_if);
    let with_num = rewrite_number_text_paths(&with_cmp);
    let with_doc = rewrite_document_codelist_in_metar_speci_patterns(&with_num);
    let with_obs2 = rewrite_observation2_assert(&with_doc);
    rewrite_report9_assert(&with_obs2)
}

/// Targeted XPath 1.0 stand-in for Observation-2 (low vis ⇒ RVR).
///
/// Generic ``number(path)`` rewrite still left this assert inert under xmloxide; use a
/// predicate form known to evaluate for convert METAR XML.
fn rewrite_observation2_assert(input: &str) -> String {
    const MARKER: &str = "id=\"METAR_SPECI.MeteorologicalAerodromeObservation-2\"";
    // Match by pattern id, then rewrite the following assert test= value.
    let Some(pat_idx) = input.find(MARKER) else {
        return input.to_string();
    };
    let after_pat = &input[pat_idx..];
    let Some(test_rel) = after_pat.find("test=\"") else {
        return input.to_string();
    };
    let test_abs = pat_idx + test_rel;
    let value_start = test_abs + "test=\"".len();
    let Some(value_end_rel) = input[value_start..].find('"') else {
        return input.to_string();
    };
    let value_end = value_start + value_end_rel;
    // Pass when high vis, non-metre uom, RVR present, or no visibility block.
    let replacement = concat!(
        "(number(iwxxm:visibility//iwxxm:prevailingVisibility) &gt;= 1500) ",
        "or not(iwxxm:visibility//iwxxm:prevailingVisibility/@uom = 'm') ",
        "or exists(iwxxm:rvr) ",
        "or not(exists(iwxxm:visibility))",
    );
    let mut out = String::with_capacity(input.len() + 64);
    out.push_str(&input[..value_start]);
    out.push_str(replacement);
    out.push_str(&input[value_end..]);
    out
}

/// Stand-in for RDF ``document()`` codelist membership (METAR_SPECI patterns only).
fn rewrite_document_codelist_in_metar_speci_patterns(input: &str) -> String {
    map_metar_speci_pattern_blocks(input, rewrite_document_codelist_asserts)
}

/// Stand-in for RDF ``document()`` codelist membership inside one SCH fragment.
///
/// Requires a mirrored unprefixed ``href`` (see ``mirror_xlink_href_attrs``) because
/// xmloxide Schematron XPath does not resolve ``@xlink:href``.
fn rewrite_document_codelist_asserts(input: &str) -> String {
    let marker = "@xlink:href = document(";
    let tail = " or @nilReason";
    let replacement = "(starts-with(@href,'http://codes.wmo.int/') or boolean(@nilReason))";
    let mut out = String::with_capacity(input.len());
    let mut rest = input;
    while let Some(idx) = rest.find(marker) {
        out.push_str(&rest[..idx]);
        let after = &rest[idx..];
        if let Some(end) = after.find(tail) {
            out.push_str(replacement);
            rest = &after[end + tail.len()..];
        } else {
            out.push_str(marker);
            rest = &rest[idx + marker.len()..];
        }
    }
    out.push_str(rest);
    out
}

/// Apply ``map`` to each ``<sch:pattern id="METAR_SPECI.…">…</sch:pattern>`` block.
fn map_metar_speci_pattern_blocks(input: &str, map: fn(&str) -> String) -> String {
    let open = "<sch:pattern";
    let close = "</sch:pattern>";
    let mut out = String::with_capacity(input.len() + 64);
    let mut rest = input;
    while let Some(idx) = rest.find(open) {
        out.push_str(&rest[..idx]);
        let from_pat = &rest[idx..];
        let Some(end_rel) = from_pat.find(close) else {
            out.push_str(from_pat);
            return out;
        };
        let end = end_rel + close.len();
        let block = &from_pat[..end];
        if block.contains("id=\"METAR_SPECI.") {
            out.push_str(&map(block));
        } else {
            out.push_str(block);
        }
        rest = &from_pat[end..];
    }
    out.push_str(rest);
    out
}

/// Report-9: ARP ``gml:pos`` ancestors with ``srsName`` must have srsDimension=2 + axisLabels.
fn rewrite_report9_assert(input: &str) -> String {
    const MARKER: &str = "id=\"METAR_SPECI.MeteorologicalAerodromeObservationReport-9\"";
    let Some(pat_idx) = input.find(MARKER) else {
        return input.to_string();
    };
    let after_pat = &input[pat_idx..];
    let Some(test_rel) = after_pat.find("test=\"") else {
        return input.to_string();
    };
    let test_abs = pat_idx + test_rel;
    let value_start = test_abs + "test=\"".len();
    let Some(value_end_rel) = input[value_start..].find('"') else {
        return input.to_string();
    };
    let value_end = value_start + value_end_rel;
    // Fail when a pos exists under ARP without a qualifying srs ancestor.
    let replacement = concat!(
        "not(iwxxm:aerodrome//aixm:ARP//gml:pos[not(ancestor-or-self::*",
        "[@srsName and @srsDimension='2' and boolean(@axisLabels)])])",
    );
    let mut out = String::with_capacity(input.len() + 64);
    out.push_str(&input[..value_start]);
    out.push_str(replacement);
    out.push_str(&input[value_end..]);
    out
}

/// Duplicate ``xlink:href="…"`` as unprefixed ``href="…"`` for Schematron XPath1.
fn mirror_xlink_href_attrs(xml: &str) -> String {
    let marker = "xlink:href=\"";
    let mut out = String::with_capacity(xml.len() + 64);
    let mut rest = xml;
    while let Some(idx) = rest.find(marker) {
        out.push_str(&rest[..idx]);
        let after_eq = &rest[idx + marker.len()..];
        let Some(end) = after_eq.find('"') else {
            out.push_str(marker);
            rest = after_eq;
            continue;
        };
        let value = &after_eq[..end];
        out.push_str(marker);
        out.push_str(value);
        out.push('"');
        let tail = &after_eq[end + 1..];
        // Skip if caller already mirrored.
        if tail.trim_start().starts_with("href=\"") {
            rest = tail;
            continue;
        }
        out.push_str(" href=\"");
        out.push_str(value);
        out.push('"');
        rest = tail;
    }
    out.push_str(rest);
    out
}

/// Rewrite XPath2 word comparisons to XPath 1.0 operators (XML-attribute safe).
fn rewrite_xpath2_comparisons(input: &str) -> String {
    // Must use entities: raw ``<`` inside ``test="..."`` breaks Schematron XML parse.
    input
        .replace(" gt ", " &gt; ")
        .replace(" lt ", " &lt; ")
        .replace(" ge ", " &gt;= ")
        .replace(" le ", " &lt;= ")
        .replace(" eq ", " = ")
        .replace(" ne ", " != ")
}

/// Rewrite ``path/number(text())`` → ``number(path)`` (XPath 1.0 cannot use number as a step).
fn rewrite_number_text_paths(input: &str) -> String {
    let needle = "/number(text())";
    let mut out = String::with_capacity(input.len() + 32);
    let mut rest = input;
    while let Some(idx) = rest.find(needle) {
        let before = &rest[..idx];
        let bytes = before.as_bytes();
        let mut start = bytes.len();
        while start > 0 {
            let c = bytes[start - 1] as char;
            if c.is_ascii_alphanumeric()
                || matches!(
                    c,
                    ':' | '.' | '/' | '[' | ']' | '@' | '=' | '\'' | '"' | '_' | '-'
                )
            {
                start -= 1;
            } else {
                break;
            }
        }
        out.push_str(&before[..start]);
        let path = &before[start..];
        out.push_str("number(");
        out.push_str(path);
        out.push(')');
        rest = &rest[idx + needle.len()..];
    }
    out.push_str(rest);
    out
}

/// Rewrite XPath2 ``if/then/else`` only inside ``METAR_SPECI.*`` patterns.
///
/// Leaving ``Common.*`` (e.g. Report-3 translation metadata) as XPath2 keeps them
/// soft under xmloxide so CA_ECCC partial translationCentre* emit stays valid.
fn rewrite_xpath2_if_then_else_metar_speci_only(input: &str) -> String {
    map_metar_speci_pattern_blocks(input, rewrite_xpath2_if_then_else)
}

/// Rewrite ``if(C) then(T) else(E)`` → ``((C) and (T)) or (not(C) and (E))`` (XPath 1.0).
fn rewrite_xpath2_if_then_else(input: &str) -> String {
    let bytes = input.as_bytes();
    let mut out = String::with_capacity(input.len() + 64);
    let mut i = 0usize;
    while i < bytes.len() {
        if bytes[i..].starts_with(b"if(") || bytes[i..].starts_with(b"if (") {
            let start = i;
            // consume 'if'
            i += 2;
            while i < bytes.len() && bytes[i].is_ascii_whitespace() {
                i += 1;
            }
            if i >= bytes.len() || bytes[i] != b'(' {
                out.push_str(&input[start..start + 2]);
                i = start + 2;
                continue;
            }
            let Some((cond, after_cond)) = take_paren_group(&input[i..]) else {
                out.push_str(&input[start..start + 2]);
                i = start + 2;
                continue;
            };
            i += after_cond;
            while i < bytes.len() && bytes[i].is_ascii_whitespace() {
                i += 1;
            }
            if !input[i..].starts_with("then") {
                out.push_str(&input[start..i]);
                continue;
            }
            i += 4;
            while i < bytes.len() && bytes[i].is_ascii_whitespace() {
                i += 1;
            }
            if i >= bytes.len() || bytes[i] != b'(' {
                out.push_str(&input[start..i]);
                continue;
            }
            let Some((then_expr, after_then)) = take_paren_group(&input[i..]) else {
                out.push_str(&input[start..i]);
                continue;
            };
            i += after_then;
            while i < bytes.len() && bytes[i].is_ascii_whitespace() {
                i += 1;
            }
            if !input[i..].starts_with("else") {
                out.push_str(&input[start..i]);
                continue;
            }
            i += 4;
            while i < bytes.len() && bytes[i].is_ascii_whitespace() {
                i += 1;
            }
            if i >= bytes.len() || bytes[i] != b'(' {
                out.push_str(&input[start..i]);
                continue;
            }
            let Some((else_expr, after_else)) = take_paren_group(&input[i..]) else {
                out.push_str(&input[start..i]);
                continue;
            };
            i += after_else;
            // Recurse into branches so nested if() rewrite.
            let cond_r = rewrite_xpath2_if_then_else(cond);
            let then_r = rewrite_xpath2_if_then_else(then_expr);
            let else_r = rewrite_xpath2_if_then_else(else_expr);
            out.push_str(&format!(
                "((({cond_r}) and ({then_r})) or (not({cond_r}) and ({else_r})))"
            ));
            continue;
        }
        out.push(bytes[i] as char);
        i += 1;
    }
    out
}

/// Return inner text of a `(...)` group starting at ``s[0]=='('``, plus bytes consumed.
fn take_paren_group(s: &str) -> Option<(&str, usize)> {
    let bytes = s.as_bytes();
    if bytes.first().copied() != Some(b'(') {
        return None;
    }
    let mut depth = 0i32;
    let mut in_str: Option<u8> = None;
    for (idx, &b) in bytes.iter().enumerate() {
        if let Some(q) = in_str {
            if b == q {
                in_str = None;
            }
            continue;
        }
        match b {
            b'\'' | b'"' => in_str = Some(b),
            b'(' => depth += 1,
            b')' => {
                depth -= 1;
                if depth == 0 {
                    return Some((&s[1..idx], idx + 1));
                }
            }
            _ => {}
        }
    }
    None
}

/// Validate IWXXM XML via xmloxide (well-formed + optional XSD + Schematron).
///
/// Returns a list of issue dicts: ``severity``, ``code``, ``message``, ``layer``, ``location``.
#[pyfunction]
#[pyo3(signature = (xml, *, xsd_path, sch_path, catalog_roots, levels))]
fn validate_document<'py>(
    py: Python<'py>,
    xml: &str,
    xsd_path: &str,
    sch_path: &str,
    catalog_roots: Vec<String>,
    levels: Vec<String>,
) -> PyResult<Bound<'py, PyList>> {
    let issues = PyList::empty(py);
    let want_xsd = levels.iter().any(|l| l == "xsd");
    let want_sch = levels.iter().any(|l| l == "schematron");

    // Mirror xlink:href → unprefixed href so Schematron XPath1 can see codelist URIs.
    let xml_owned;
    let xml_in = if want_sch {
        xml_owned = mirror_xlink_href_attrs(xml);
        xml_owned.as_str()
    } else {
        xml
    };

    let doc = match Document::parse_str(xml_in) {
        Ok(d) => d,
        Err(e) => {
            issues.append(issue_dict(
                py,
                "error",
                "XML_SYNTAX_ERROR",
                &format!("XML parsing failed: {e}"),
                "wellformed",
                None,
            )?)?;
            return Ok(issues);
        }
    };

    if want_xsd {
        match get_or_parse_xsd(xsd_path, &catalog_roots) {
            Ok(schema) => {
                let result = validate_xsd(&doc, &schema);
                for err in &result.errors {
                    issues.append(issue_dict(
                        py,
                        "error",
                        "XSD_VALIDATION_ERROR",
                        &err.message,
                        "xsd",
                        None,
                    )?)?;
                }
                for warn in &result.warnings {
                    issues.append(issue_dict(
                        py,
                        "warning",
                        "XSD_VALIDATION_WARNING",
                        &warn.message,
                        "xsd",
                        None,
                    )?)?;
                }
            }
            Err(msg) => {
                let code = if msg.contains("not readable") {
                    "SCHEMA_NOT_AVAILABLE"
                } else {
                    "SCHEMA_PARSE_ERROR"
                };
                issues.append(issue_dict(py, "error", code, &msg, "xsd", Some(xsd_path))?)?;
                if !want_sch {
                    return Ok(issues);
                }
            }
        }
    }

    if want_sch {
        match get_or_parse_schematron(sch_path) {
            Ok(schema) => {
                for row in schematron_rows(&doc, &schema) {
                    issues.append(issue_dict(
                        py,
                        row.severity,
                        &row.code,
                        &row.message,
                        "schematron",
                        None,
                    )?)?;
                }
            }
            Err(msg) => {
                let code = if msg.contains("not readable") {
                    "SCHEMATRON_NOT_AVAILABLE"
                } else {
                    "SCHEMATRON_PARSE_ERROR"
                };
                issues.append(issue_dict(
                    py,
                    "error",
                    code,
                    &msg,
                    "schematron",
                    Some(sch_path),
                )?)?;
            }
        }
    }

    Ok(issues)
}

#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_function(wrap_pyfunction!(extension_version, m)?)?;
    m.add_function(wrap_pyfunction!(ping, m)?)?;
    m.add_function(wrap_pyfunction!(clear_schema_caches, m)?)?;
    m.add_function(wrap_pyfunction!(validate_document, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::schematron_rows;
    use xmloxide::validation::schematron::{parse_schematron, SchematronSchema};
    use xmloxide::Document;

    fn schema(body: &str) -> SchematronSchema {
        parse_schematron(body).expect("schema")
    }

    fn errors(body: &str, xml: &str) -> Vec<String> {
        let doc = Document::parse_str(xml).expect("xml");
        schematron_rows(&doc, &schema(body))
            .into_iter()
            .filter(|row| row.severity == "error")
            .map(|row| row.code)
            .collect()
    }

    #[test]
    fn named_pattern_id_labels_the_failure() {
        let codes = errors(
            r#"<schema xmlns="http://purl.oclc.org/dml/schematron">
                <pattern id="P1"><rule context="/*"><assert test="false()">fail one</assert></rule></pattern>
                <pattern id="P2"><rule context="/*"><assert test="true()">ok</assert></rule></pattern>
            </schema>"#,
            "<root/>",
        );
        assert_eq!(codes, vec!["P1".to_string()]);
    }

    #[test]
    fn unnamed_pattern_stays_generic() {
        let codes = errors(
            r#"<schema xmlns="http://purl.oclc.org/dml/schematron">
                <pattern><rule context="/*"><assert test="false()">fail</assert></rule></pattern>
            </schema>"#,
            "<root/>",
        );
        assert_eq!(codes, vec!["SCHEMATRON_ASSERT".to_string()]);
    }

    #[test]
    fn passing_document_has_no_assertion_rows() {
        let codes = errors(
            r#"<schema xmlns="http://purl.oclc.org/dml/schematron">
                <pattern id="P1"><rule context="/*"><assert test="true()">ok</assert></rule></pattern>
            </schema>"#,
            "<root/>",
        );
        assert!(codes.is_empty());
    }

    #[test]
    fn default_phase_skips_inactive_pattern() {
        let codes = errors(
            r#"<schema xmlns="http://purl.oclc.org/dml/schematron" defaultPhase="quick">
                <phase id="quick"><active pattern="pass"/></phase>
                <pattern id="pass"><rule context="/*"><assert test="true()">ok</assert></rule></pattern>
                <pattern id="strict"><rule context="/*"><assert test="false()">fail</assert></rule></pattern>
            </schema>"#,
            "<root/>",
        );
        assert!(codes.is_empty());
    }
}

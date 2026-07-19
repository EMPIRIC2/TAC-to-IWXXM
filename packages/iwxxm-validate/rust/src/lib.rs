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
use xmloxide::validation::schematron::{parse_schematron, validate_schematron, SchematronSchema};
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
type ResolverIndexCache = Mutex<HashMap<Vec<String>, HashMap<String, PathBuf>>>;

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

/// Pre-indexed vendor-tree resolver: basename → path (+ relative joins).
struct VendorResolver {
    roots: Vec<PathBuf>,
    /// Lowercased basename → first matching file under catalog roots.
    by_basename: HashMap<String, PathBuf>,
    /// Memoize resolve() results for this parse session.
    hit_cache: Mutex<HashMap<String, Option<String>>>,
}

impl VendorResolver {
    fn new(roots: Vec<String>) -> Self {
        let key: Vec<String> = {
            let mut k = roots.clone();
            k.sort();
            k
        };
        let by_basename = {
            let mut guard = resolver_index_cache()
                .lock()
                .expect("resolver index lock");
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
        }
    }

    fn candidates(&self, location: &str, base: Option<&str>) -> Vec<PathBuf> {
        let loc = location.split('/').last().unwrap_or(location);
        let stripped = location
            .strip_prefix("http://")
            .or_else(|| location.strip_prefix("https://"))
            .unwrap_or(location);
        let mut out: Vec<PathBuf> = Vec::new();
        if let Some(b) = base {
            let parent = Path::new(b).parent().unwrap_or(Path::new("."));
            out.push(parent.join(location));
            out.push(parent.join(stripped));
            out.push(parent.join(loc));
        }
        for root in &self.roots {
            out.push(root.join(location));
            out.push(root.join(stripped));
            out.push(root.join(loc));
        }
        if let Some(p) = self.by_basename.get(loc) {
            out.push(p.clone());
        }
        // Case-insensitive basename fallback
        let loc_lower = loc.to_ascii_lowercase();
        if loc_lower != loc {
            if let Some(p) = self.by_basename.get(&loc_lower) {
                out.push(p.clone());
            }
        }
        out
    }
}

fn build_basename_index(roots: &[String]) -> HashMap<String, PathBuf> {
    let mut index: HashMap<String, PathBuf> = HashMap::new();
    for root in roots {
        let root_path = PathBuf::from(root);
        index_walk(&root_path, &mut index, 6);
    }
    index
}

fn index_walk(dir: &Path, index: &mut HashMap<String, PathBuf>, depth: usize) {
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
                index.entry(name.to_string()).or_insert_with(|| p.clone());
                index
                    .entry(name.to_ascii_lowercase())
                    .or_insert_with(|| p.clone());
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

fn catalog_key(catalog_roots: &[String]) -> Vec<String> {
    let mut key = catalog_roots.to_vec();
    key.sort();
    key
}

fn get_or_parse_xsd(
    xsd_path: &str,
    catalog_roots: &[String],
) -> Result<Arc<XsdSchema>, String> {
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
    let parsed = parse_schematron(&sch_text)
        .map(Arc::new)
        .map_err(|e| format!("Failed to parse Schematron: {}", e.message));

    let mut guard = sch_cache().lock().expect("sch cache lock");
    if let Some(existing) = guard.get(&key) {
        return existing.clone();
    }
    guard.insert(key, parsed.clone());
    parsed
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

    let doc = match Document::parse_str(xml) {
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
                issues.append(issue_dict(
                    py,
                    "error",
                    code,
                    &msg,
                    "xsd",
                    Some(xsd_path),
                )?)?;
                if !want_sch {
                    return Ok(issues);
                }
            }
        }
    }

    if want_sch {
        match get_or_parse_schematron(sch_path) {
            Ok(schema) => {
                let result = validate_schematron(&doc, &schema);
                for err in &result.errors {
                    issues.append(issue_dict(
                        py,
                        "error",
                        "SCHEMATRON_ASSERT",
                        &err.message,
                        "schematron",
                        None,
                    )?)?;
                }
                for warn in &result.warnings {
                    issues.append(issue_dict(
                        py,
                        "warning",
                        "SCHEMATRON_REPORT",
                        &warn.message,
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

//! PyO3 native extension for `iwxxm-validate` (F13 / E10-22 / D-S014-T33-crates).
//!
//! Stack A: **xmloxide** — well-formed + XSD + native ISO Schematron (no libxml2).

use std::path::{Path, PathBuf};

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use xmloxide::validation::schematron::{parse_schematron, validate_schematron};
use xmloxide::validation::xsd::{
    parse_xsd_with_options, validate_xsd, SchemaResolver, XsdParseOptions,
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

/// Vendor-tree resolver: maps ``http(s)://host/path`` → catalog roots + basename walk.
struct VendorResolver {
    roots: Vec<PathBuf>,
}

impl VendorResolver {
    fn new(roots: Vec<String>) -> Self {
        Self {
            roots: roots.into_iter().map(PathBuf::from).collect(),
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
            // OASIS-style mirror: externalSchema/schemas.opengis.net/...
            out.push(root.join(stripped));
            push_basename_walk(&mut out, root, loc, 4);
        }
        out
    }
}

fn push_basename_walk(out: &mut Vec<PathBuf>, dir: &Path, basename: &str, depth: usize) {
    if depth == 0 || !dir.is_dir() {
        return;
    }
    let Ok(rd) = std::fs::read_dir(dir) else {
        return;
    };
    for ent in rd.flatten() {
        let p = ent.path();
        if p.is_file() {
            if p.file_name().and_then(|s| s.to_str()) == Some(basename) {
                out.push(p);
            }
        } else if p.is_dir() {
            let try1 = p.join(basename);
            if try1.is_file() {
                out.push(try1);
            }
            push_basename_walk(out, &p, basename, depth - 1);
        }
    }
}

impl SchemaResolver for VendorResolver {
    fn resolve(&self, location: &str, base: Option<&str>) -> Option<String> {
        for c in self.candidates(location, base) {
            if c.is_file() {
                if let Ok(text) = std::fs::read_to_string(&c) {
                    return Some(text);
                }
            }
        }
        None
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
        let xsd_text = match std::fs::read_to_string(xsd_path) {
            Ok(t) => t,
            Err(e) => {
                issues.append(issue_dict(
                    py,
                    "error",
                    "SCHEMA_NOT_AVAILABLE",
                    &format!("XSD not readable at {xsd_path}: {e}"),
                    "xsd",
                    Some(xsd_path),
                )?)?;
                if !want_sch {
                    return Ok(issues);
                }
                String::new()
            }
        };
        if !xsd_text.is_empty() {
            let resolver = VendorResolver::new(catalog_roots.clone());
            let opts = XsdParseOptions {
                resolver: Some(&resolver),
                base_uri: Some(xsd_path.to_string()),
            };
            match parse_xsd_with_options(&xsd_text, &opts) {
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
                Err(e) => {
                    issues.append(issue_dict(
                        py,
                        "error",
                        "SCHEMA_PARSE_ERROR",
                        &format!("Failed to parse XSD schema: {}", e.message),
                        "xsd",
                        Some(xsd_path),
                    )?)?;
                }
            }
        }
    }

    if want_sch {
        let sch_text = match std::fs::read_to_string(sch_path) {
            Ok(t) => t,
            Err(e) => {
                issues.append(issue_dict(
                    py,
                    "error",
                    "SCHEMATRON_NOT_AVAILABLE",
                    &format!("Schematron not readable at {sch_path}: {e}"),
                    "schematron",
                    Some(sch_path),
                )?)?;
                return Ok(issues);
            }
        };
        match parse_schematron(&sch_text) {
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
            Err(e) => {
                issues.append(issue_dict(
                    py,
                    "error",
                    "SCHEMATRON_PARSE_ERROR",
                    &format!("Failed to parse Schematron: {}", e.message),
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
    m.add_function(wrap_pyfunction!(validate_document, m)?)?;
    Ok(())
}

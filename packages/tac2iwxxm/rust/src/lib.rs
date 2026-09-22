//! PyO3 native extension for `tac2iwxxm` (ADR-017).
//!
//! T4.3 scaffold + T4.5 [`scan_metar_tokens`] hotspot (TAC lexer).

#![deny(missing_docs)]

use pyo3::prelude::*;

/// Extension package version (mirrors `Cargo.toml`).
///
/// # Examples
///
/// ```
/// assert!(!_rust::extension_version().is_empty());
/// ```
#[pyfunction]
pub fn extension_version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

/// Health check used by CI / import smoke tests.
///
/// # Examples
///
/// ```
/// assert_eq!(_rust::ping(), "pong");
/// ```
#[pyfunction]
pub fn ping() -> &'static str {
    "pong"
}

/// Split METAR/SPECI TAC into whitespace tokens (hotspot scaffold for T4.5+).
///
/// Strips a trailing ``=`` terminator when present. Does not yet implement a full
/// remark-aware lexer — that lands with further PyO3 work.
///
/// # Examples
///
/// ```
/// let tokens = _rust::scan_metar_tokens("METAR EGLL 121020Z =");
/// assert_eq!(tokens, ["METAR", "EGLL", "121020Z"]);
/// ```
#[pyfunction]
pub fn scan_metar_tokens(tac: &str) -> Vec<String> {
    let trimmed = tac.trim().trim_end_matches('=').trim();
    trimmed
        .split_whitespace()
        .map(|part| part.to_string())
        .collect()
}

/// Registers the compiled extension module (`tac2iwxxm._rust`).
#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_function(wrap_pyfunction!(extension_version, m)?)?;
    m.add_function(wrap_pyfunction!(ping, m)?)?;
    m.add_function(wrap_pyfunction!(scan_metar_tokens, m)?)?;
    Ok(())
}

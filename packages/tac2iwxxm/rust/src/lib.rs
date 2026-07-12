//! PyO3 native extension for `tac2iwxxm` (ADR-017).
//!
//! T4.3 scaffold + T4.5 `scan_metar_tokens` hotspot (TAC lexer).

use pyo3::prelude::*;

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

/// Split METAR/SPECI TAC into whitespace tokens (hotspot scaffold for T4.5+).
///
/// Strips a trailing ``=`` terminator when present. Does not yet implement a full
/// remark-aware lexer — that lands with further PyO3 work.
#[pyfunction]
fn scan_metar_tokens(tac: &str) -> Vec<String> {
    let trimmed = tac.trim().trim_end_matches('=').trim();
    trimmed
        .split_whitespace()
        .map(|part| part.to_string())
        .collect()
}

#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_function(wrap_pyfunction!(extension_version, m)?)?;
    m.add_function(wrap_pyfunction!(ping, m)?)?;
    m.add_function(wrap_pyfunction!(scan_metar_tokens, m)?)?;
    Ok(())
}

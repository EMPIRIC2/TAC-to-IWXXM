//! PyO3 native extension for `iwxxm-validate` (F13 / E10-36).
//!
//! T3.1 scaffold — well-formed / XSD / Schematron hotspots land in T3.3.

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

#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_function(wrap_pyfunction!(extension_version, m)?)?;
    m.add_function(wrap_pyfunction!(ping, m)?)?;
    Ok(())
}

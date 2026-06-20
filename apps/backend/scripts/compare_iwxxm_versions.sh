#!/usr/bin/env bash
# Run IWXXM version comparison tests and generate analysis report

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$BACKEND_DIR"

echo "================================================================================"
echo "IWXXM Version Comparison Test Suite"
echo "================================================================================"
echo ""

# Ensure report directories exist
mkdir -p test-reports/{local-test-failures,live-test-failures}

# Run 2023-1 tests (local/WMO reference)
echo "▶ Running 2023-1 (local) tests..."
echo "--------------------------------------------------------------------------------"
python3 -m pytest tests/test_metar_pairs_comprehensive.py::TestMetarConversionComprehensive::test_metar_converts_to_matching_iwxxm \
    -q --tb=no || echo "⚠️  Some 2023-1 tests failed (check reports)"
echo ""

# Run 2025-2 tests (live/aviation-weather-service)
echo "▶ Running 2025-2 (live) tests..."
echo "--------------------------------------------------------------------------------"
python3 -m pytest tests/test_metar_pairs_comprehensive.py::TestMetarConversionComprehensive::test_metar_converts_to_iwxxm_2025_2 \
    -q --tb=no || echo "⚠️  Some 2025-2 tests failed (check reports)"
echo ""

# Generate comparison analysis
echo "▶ Generating comparison analysis..."
echo "--------------------------------------------------------------------------------"
python3 scripts/analyze_version_comparisons.py

# Save analysis to file
echo ""
echo "▶ Saving analysis report..."
python3 scripts/analyze_version_comparisons.py > test-reports/comparison-summary.txt
echo "✅ Analysis saved to: test-reports/comparison-summary.txt"
echo ""

# Count reports
local_count=$(ls -1 test-reports/local-test-failures/*.json 2>/dev/null | wc -l)
live_count=$(ls -1 test-reports/live-test-failures/*.json 2>/dev/null | wc -l)

echo "================================================================================"
echo "Reports Generated"
echo "================================================================================"
echo "Local (2023-1): $local_count reports"
echo "Live (2025-2):  $live_count reports"
echo ""
echo "📁 View reports:"
echo "   - Local:  test-reports/local-test-failures/"
echo "   - Live:   test-reports/live-test-failures/"
echo "   - Summary: test-reports/comparison-summary.txt"
echo ""
echo "✅ Version comparison complete!"
echo "================================================================================"

#!/usr/bin/env python3
"""Compare test reports between local (2023-1) and live (2025-2) conversions.

This script analyzes the JSON reports in test-reports/ to identify:
- Tests that pass in one version but fail in another
- Common failure patterns
- Version-specific issues
- Improvement/regression trends
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict


def load_reports(report_dir: Path) -> Dict[str, dict]:
    """Load all JSON reports from a directory."""
    reports = {}
    if not report_dir.exists():
        return reports

    for json_file in report_dir.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                report = json.load(f)
                reports[json_file.stem] = report
        except Exception as e:
            print(f"Warning: Failed to load {json_file}: {e}")
    return reports


def extract_test_case(report_name: str) -> str:
    """Extract base test case name from report filename.
    
    Examples:
        "KJFK-290000Z_Amd79-80-2023" -> "KJFK-290000Z"
        "CYEK-290000Z_Amd79-80-2023-2025-2" -> "CYEK-290000Z"
    """
    # Remove version suffix
    parts = report_name.split("_")
    return parts[0] if parts else report_name


def compare_versions():
    """Compare local vs live test reports."""
    base_dir = Path(__file__).parent.parent / "test-reports"
    local_dir = base_dir / "local-test-failures"
    live_dir = base_dir / "live-test-failures"

    print("=" * 80)
    print("IWXXM Version Comparison: Local (2023-1) vs Live (2025-2)")
    print("=" * 80)
    print(f"Generated: {datetime.utcnow().isoformat()}\n")

    # Load reports
    local_reports = load_reports(local_dir)
    live_reports = load_reports(live_dir)

    if not local_reports and not live_reports:
        print("No reports found. Run tests first:")
        print("  pytest tests/test_metar_pairs_comprehensive.py -v")
        return

    # Extract test cases
    local_cases = set(extract_test_case(r) for r in local_reports.keys())
    live_cases = set(extract_test_case(r) for r in live_reports.keys())

    print(f"Local reports: {len(local_reports)} ({len(local_cases)} unique test cases)")
    print(f"Live reports:  {len(live_reports)} ({len(live_cases)} unique test cases)\n")

    # Compare by test case
    all_cases = local_cases | live_cases

    pass_both = []
    pass_local_fail_live = []
    fail_local_pass_live = []
    fail_both = []
    only_local = []
    only_live = []

    for case in sorted(all_cases):
        # Find matching reports for this case
        local_matches = [(k, r) for k, r in local_reports.items() if extract_test_case(k) == case]
        live_matches = [(k, r) for k, r in live_reports.items() if extract_test_case(k) == case]

        if not local_matches:
            only_live.append(case)
            continue
        if not live_matches:
            only_local.append(case)
            continue

        # Check status (use most recent amendment)
        _, local_report = local_matches[-1]
        _, live_report = live_matches[-1]

        local_status = local_report.get("status", "UNKNOWN")
        live_status = live_report.get("status", "UNKNOWN")

        if local_status == "PASS" and live_status == "PASS":
            pass_both.append(case)
        elif local_status == "PASS" and live_status == "FAIL":
            pass_local_fail_live.append((case, local_report, live_report))
        elif local_status == "FAIL" and live_status == "PASS":
            fail_local_pass_live.append((case, local_report, live_report))
        else:
            fail_both.append((case, local_report, live_report))

    # Print summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Pass in both versions:          {len(pass_both)}")
    print(f"⬆️  Pass local, fail live (2025-2): {len(pass_local_fail_live)}")
    print(f"⬇️  Fail local, pass live (2025-2): {len(fail_local_pass_live)}")
    print(f"❌ Fail in both versions:          {len(fail_both)}")
    print(f"📍 Only in local (2023-1):         {len(only_local)}")
    print(f"📍 Only in live (2025-2):          {len(only_live)}\n")

    # Detailed analysis: Regressions (Pass→Fail)
    if pass_local_fail_live:
        print("=" * 80)
        print("⚠️  REGRESSIONS: Tests passing in 2023-1 but failing in 2025-2")
        print("=" * 80)
        for case, local_report, live_report in pass_local_fail_live[:10]:  # Show first 10
            print(f"\n{case}:")
            field_diffs = live_report.get('field_diffs', [])
            lat_lon_diffs = live_report.get('lat_lon_diffs', [])
            print(f"  Field diffs: {len(field_diffs)}")
            if field_diffs:
                for diff in field_diffs[:3]:
                    if isinstance(diff, dict):
                        print(f"    - {diff.get('path', 'unknown')}: {diff.get('reason', 'no reason')}")
                    else:
                        print(f"    - {diff}")
            print(f"  Lat/Lon diffs: {len(lat_lon_diffs)}")
            if lat_lon_diffs:
                for diff in lat_lon_diffs[:3]:
                    if isinstance(diff, dict):
                        print(f"    - {diff.get('element_id', 'unknown')}: {diff.get('distance_meters', 0):.2f}m")
                    else:
                        print(f"    - {diff}")

        if len(pass_local_fail_live) > 10:
            print(f"\n  ... and {len(pass_local_fail_live) - 10} more regressions")

    # Detailed analysis: Improvements (Fail→Pass)
    if fail_local_pass_live:
        print("\n" + "=" * 80)
        print("✨ IMPROVEMENTS: Tests failing in 2023-1 but passing in 2025-2")
        print("=" * 80)
        for case, local_report, live_report in fail_local_pass_live[:10]:
            print(f"\n{case}:")
            print("  Previous issues resolved:")
            field_diffs = local_report.get('field_diffs', [])
            lat_lon_diffs = local_report.get('lat_lon_diffs', [])
            if field_diffs:
                print(f"    - Field diffs: {len(field_diffs)}")
            if lat_lon_diffs:
                print(f"    - Lat/Lon diffs: {len(lat_lon_diffs)}")

        if len(fail_local_pass_live) > 10:
            print(f"\n  ... and {len(fail_local_pass_live) - 10} more improvements")

    # Common failure patterns
    if fail_both:
        print("\n" + "=" * 80)
        print("🔍 PERSISTENT FAILURES: Common issues in both versions")
        print("=" * 80)

        field_issue_counts = defaultdict(int)
        for case, local_report, live_report in fail_both:
            for diff in local_report.get('field_diffs', []) + live_report.get('field_diffs', []):
                if isinstance(diff, dict):
                    path = diff.get('path', '')
                    if path:
                        # Extract field name from path
                        field_name = path.split('/')[-1] if '/' in path else path
                        field_issue_counts[field_name] += 1
                elif isinstance(diff, str):
                    # Try to extract field name from string diff
                    if "field" in diff:
                        parts = diff.split("field")
                        if len(parts) > 1:
                            field_name = parts[1].split()[0].strip(":[]")
                            field_issue_counts[field_name] += 1

        print("\nMost common field issues:")
        for field, count in sorted(field_issue_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {field}: {count} occurrences")

    # Version-specific metadata differences
    print("\n" + "=" * 80)
    print("📊 VERSION METADATA DIFFERENCES")
    print("=" * 80)

    metadata_patterns = defaultdict(int)
    for _, local_report, live_report in fail_both + pass_local_fail_live:
        for diff in live_report.get('metadata_diffs', []):
            if isinstance(diff, dict):
                attr = diff.get('attr', 'unknown')
                metadata_patterns[attr] += 1

    if metadata_patterns:
        print("\nCommon metadata attribute differences:")
        for attr, count in sorted(metadata_patterns.items(), key=lambda x: -x[1])[:10]:
            print(f"  {attr}: {count} occurrences")
    else:
        print("\nNo significant metadata differences detected.")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    compare_versions()

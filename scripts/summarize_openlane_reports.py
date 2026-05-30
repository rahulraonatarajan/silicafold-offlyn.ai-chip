#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# SilicaFold V0 - OpenLane Report Summarizer
#
# Scans a downloaded reports directory and prints a summary of key metrics.
# Gracefully handles missing files.
#
# Usage: python scripts/summarize_openlane_reports.py [reports_dir]
# Default reports_dir: ./artifacts/reports

import os
import sys
import re
from pathlib import Path


def find_files(base_dir, pattern):
    """Find files matching a glob pattern."""
    return list(Path(base_dir).rglob(pattern))


def read_file_safe(filepath):
    """Read file contents, return None if not found."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except (FileNotFoundError, PermissionError):
        return None


def extract_metric(content, pattern, group=1):
    """Extract a metric using regex, return None if not found."""
    if content is None:
        return None
    match = re.search(pattern, content)
    if match:
        return match.group(group)
    return None


def summarize_synthesis(reports_dir):
    """Summarize synthesis reports."""
    print("\n=== Synthesis Summary ===")
    
    # Look for synthesis reports
    synth_files = find_files(reports_dir, "*synthesis*stat*.rpt")
    synth_files += find_files(reports_dir, "*yosys*stat*")
    
    if not synth_files:
        print("  Synthesis reports: not found")
        return
    
    for f in synth_files[:2]:
        content = read_file_safe(f)
        if content:
            # Try to extract cell count
            cells = extract_metric(content, r"Number of cells:\s*(\d+)")
            if cells:
                print(f"  Cell count: {cells}")
            
            # Try to extract wire count
            wires = extract_metric(content, r"Number of wires:\s*(\d+)")
            if wires:
                print(f"  Wire count: {wires}")
            
            print(f"  Report: {f.name}")


def summarize_timing(reports_dir):
    """Summarize timing reports."""
    print("\n=== Timing Summary ===")
    
    timing_files = find_files(reports_dir, "*timing*.rpt")
    timing_files += find_files(reports_dir, "*sta*.rpt")
    
    if not timing_files:
        print("  Timing reports: not found")
        return
    
    for f in timing_files[:2]:
        content = read_file_safe(f)
        if content:
            # Look for slack
            slack = extract_metric(content, r"slack\s*[:\(]\s*([-\d.]+)")
            if slack:
                slack_val = float(slack)
                status = "MET" if slack_val >= 0 else "VIOLATED"
                print(f"  Slack: {slack} ns ({status})")
            
            # Look for WNS (worst negative slack)
            wns = extract_metric(content, r"wns\s*[:\(]\s*([-\d.]+)", 1)
            if wns:
                print(f"  WNS: {wns} ns")
            
            print(f"  Report: {f.name}")


def summarize_utilization(reports_dir):
    """Summarize utilization/area reports."""
    print("\n=== Utilization Summary ===")
    
    util_files = find_files(reports_dir, "*utilization*.rpt")
    util_files += find_files(reports_dir, "*area*.rpt")
    
    if not util_files:
        print("  Utilization reports: not found")
        return
    
    for f in util_files[:2]:
        content = read_file_safe(f)
        if content:
            # Look for utilization percentage
            util = extract_metric(content, r"utilization[:\s]+(\d+\.?\d*)%?")
            if util:
                print(f"  Utilization: {util}%")
            
            # Look for area
            area = extract_metric(content, r"total.*area[:\s]+([\d.]+)")
            if area:
                print(f"  Total area: {area}")
            
            print(f"  Report: {f.name}")


def summarize_drc(reports_dir):
    """Summarize DRC reports."""
    print("\n=== DRC Summary ===")
    
    drc_files = find_files(reports_dir, "*drc*.rpt")
    drc_files += find_files(reports_dir, "*drc*.log")
    
    if not drc_files:
        print("  DRC reports: not found")
        return
    
    for f in drc_files[:2]:
        content = read_file_safe(f)
        if content:
            # Look for violation count
            violations = extract_metric(content, r"(\d+)\s*violations?")
            if violations:
                status = "CLEAN" if violations == "0" else "VIOLATIONS"
                print(f"  DRC violations: {violations} ({status})")
            elif "clean" in content.lower() or "no violations" in content.lower():
                print("  DRC: CLEAN")
            
            print(f"  Report: {f.name}")


def summarize_lvs(reports_dir):
    """Summarize LVS reports."""
    print("\n=== LVS Summary ===")
    
    lvs_files = find_files(reports_dir, "*lvs*.rpt")
    lvs_files += find_files(reports_dir, "*lvs*.log")
    
    if not lvs_files:
        print("  LVS reports: not found")
        return
    
    for f in lvs_files[:2]:
        content = read_file_safe(f)
        if content:
            if "match" in content.lower() and "unique" in content.lower():
                print("  LVS: MATCH")
            elif "mismatch" in content.lower() or "error" in content.lower():
                print("  LVS: MISMATCH (check report)")
            
            print(f"  Report: {f.name}")


def main():
    reports_dir = sys.argv[1] if len(sys.argv) > 1 else "./artifacts/reports"
    
    print("=" * 50)
    print("SilicaFold V0 - OpenLane Report Summary")
    print("=" * 50)
    print(f"Reports directory: {reports_dir}")
    
    if not os.path.isdir(reports_dir):
        print(f"\nERROR: Directory not found: {reports_dir}")
        print("\nTo use this script:")
        print("  1. Download the 'reports' artifact from GitHub Actions")
        print("  2. Extract it to ./artifacts/reports (or specify path)")
        print("  3. Run: python scripts/summarize_openlane_reports.py")
        return 1
    
    summarize_synthesis(reports_dir)
    summarize_timing(reports_dir)
    summarize_utilization(reports_dir)
    summarize_drc(reports_dir)
    summarize_lvs(reports_dir)
    
    print("\n" + "=" * 50)
    print("NOTE: These are extracted summaries. Always verify")
    print("against the full reports for submission.")
    print("=" * 50)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

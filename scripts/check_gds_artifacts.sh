#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# SilicaFold V0 - Check GDS Artifacts
#
# This script checks whether expected artifacts exist after downloading
# from GitHub Actions. Run this after downloading the CI artifacts.
#
# Usage: ./scripts/check_gds_artifacts.sh [artifacts_dir]
# Default artifacts_dir: ./artifacts

set -e

ARTIFACTS_DIR="${1:-./artifacts}"

echo "========================================"
echo "SilicaFold V0 - GDS Artifact Checker"
echo "========================================"
echo ""
echo "Checking directory: $ARTIFACTS_DIR"
echo ""

# Track what was found
FOUND=0
MISSING=0

check_file() {
    local pattern="$1"
    local desc="$2"
    
    if compgen -G "$ARTIFACTS_DIR/$pattern" > /dev/null 2>&1; then
        echo "[FOUND]   $desc"
        FOUND=$((FOUND + 1))
        # List matching files
        find "$ARTIFACTS_DIR" -path "$ARTIFACTS_DIR/$pattern" 2>/dev/null | head -3 | while read f; do
            echo "          -> $f"
        done
    else
        echo "[MISSING] $desc"
        MISSING=$((MISSING + 1))
    fi
}

check_dir() {
    local dir="$1"
    local desc="$2"
    
    if [ -d "$ARTIFACTS_DIR/$dir" ]; then
        echo "[FOUND]   $desc"
        FOUND=$((FOUND + 1))
    else
        echo "[MISSING] $desc"
        MISSING=$((MISSING + 1))
    fi
}

echo "--- GDS Files ---"
check_file "*/final/gds/*.gds" "Final GDS file"
check_file "*/final/gds/*.gds.gz" "Compressed GDS file"

echo ""
echo "--- Reports ---"
check_dir "reports" "Reports directory"
check_file "*/reports/synthesis/*.rpt" "Synthesis reports"
check_file "*/reports/routing/*.rpt" "Routing reports"
check_file "*/reports/signoff/*.rpt" "Signoff reports"

echo ""
echo "--- Timing ---"
check_file "*/reports/*timing*" "Timing reports"
check_file "*/reports/*slack*" "Slack reports"

echo ""
echo "--- Utilization ---"
check_file "*/reports/*utilization*" "Utilization reports"
check_file "*/reports/*area*" "Area reports"

echo ""
echo "--- DRC/LVS ---"
check_file "*/reports/*drc*" "DRC reports"
check_file "*/reports/*lvs*" "LVS reports"
check_file "*/results/signoff/*" "Signoff results"

echo ""
echo "--- Renders ---"
check_file "*.png" "PNG renders"
check_file "*.svg" "SVG renders"
check_file "*.html" "HTML viewer"

echo ""
echo "========================================"
echo "Summary: $FOUND found, $MISSING missing"
echo "========================================"
echo ""

if [ ! -d "$ARTIFACTS_DIR" ]; then
    echo "NOTE: Artifacts directory does not exist."
    echo ""
    echo "To download artifacts from GitHub Actions:"
    echo "  1. Go to your repository's Actions tab"
    echo "  2. Click on the GDS workflow run"
    echo "  3. Download the 'gds', 'reports', and 'openlane-run' artifacts"
    echo "  4. Extract them to $ARTIFACTS_DIR"
    echo "  5. Run this script again"
    echo ""
fi

if [ $MISSING -gt 0 ]; then
    echo "Some artifacts are missing. This is normal if:"
    echo "  - The GDS workflow hasn't run yet"
    echo "  - You haven't downloaded all artifact ZIPs"
    echo "  - The workflow failed before generating some files"
    echo ""
    echo "Check the GitHub Actions logs for details."
fi

exit 0

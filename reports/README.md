# Reports Directory

## Purpose

This directory stores actual OpenLane/Tiny Tapeout reports copied from CI artifacts after successful hardening runs.

**Reports in this directory should be actual outputs, not estimates or placeholders.**

## Expected Contents

After successful GDS generation, copy key reports here:

### Synthesis Reports
- `synthesis_stats.rpt` - Cell counts, area estimates
- `synthesis_check.rpt` - Synthesis verification

### Timing Reports  
- `timing_summary.rpt` - Setup/hold slack summary
- `worst_paths.rpt` - Critical path analysis

### Utilization Reports
- `utilization.rpt` - Area breakdown
- `core_area.rpt` - Die dimensions

### Signoff Reports
- `drc_summary.rpt` - Design rule check results
- `lvs_summary.rpt` - Layout vs schematic results

## How to Populate

1. Run GDS workflow in GitHub Actions
2. Download the `reports` artifact
3. Extract relevant reports
4. Copy summaries here with clear naming
5. Update README with run information

## Report Naming Convention

Use descriptive names with dates/versions:
```
YYYY-MM-DD_synthesis_stats.rpt
YYYY-MM-DD_timing_summary.rpt
```

## Current Status

```
Run Date: [Not yet run]
Workflow Run ID: [N/A]
Status: [Pending first GDS build]
```

## Important Notes

- Do not fabricate or estimate report contents
- Always include the workflow run ID for traceability
- Reports may change between runs
- Final submission reports should match Tiny Tapeout requirements

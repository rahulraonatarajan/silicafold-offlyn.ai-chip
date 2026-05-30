# SilicaFold V0 Submission Review

This document summarizes the hardening work done to prepare SilicaFold V0 for Tiny Tapeout submission.

## Summary

**Current Status**: Ready for CI verification

The repository has been hardened to match the official Tiny Tapeout SKY Verilog template. All major issues have been fixed, but final verification requires running the CI workflows.

## What Was Fixed

### 1. GDS Workflow Updated
- **Changed**: From `TinyTapeout/tt-gds-action@tt09` to `@ttsky26c`
- **Reason**: Align with current SKY130 26C shuttle template
- **Added**: Precheck, GL test, and viewer jobs per official template
- **File**: `.github/workflows/gds.yaml` (renamed from `.yml`)

### 2. info.yaml Fixed
- **Changed**: Moved `yaml_version: 6` to bottom (per template)
- **Updated**: Pin descriptions to be more descriptive
- **Verified**: Source file order is correct

### 3. TensorTile RTL Improvements
- **Added**: Separate `q_load_index` and `k_load_index` registers
- **Reason**: Eliminates confusion when loading Q and K values
- **Behavior**: Both indices reset on `CMD_LOAD_CONTEXT` or `CMD_RESET_STATE`

### 4. PolicyGate RTL Fix
- **Fixed**: `CMD_READ_DECISION` bit order
- **Before**: `{require_human, block, allow, evaluated}`
- **After**: `{log_required, require_human, block, allow}`
- **Reason**: Matches top-level `uo_out[3:0]` semantics

### 5. Top Module Cleanup
- **Simplified**: `uio_oe` assignment to constant `8'b1111_0000`
- **Fixed**: Unused signal handling for `ena`

### 6. Tests Expanded
- **Added**: 16 comprehensive cocotb tests
- **Added**: Golden model for INT4 signed dot product
- **Coverage**: Reset, positive/negative values, overflow, scale shift, all PolicyGate paths, combined flow

### 7. README Hardened
- **Removed**: Overclaims about DRC/LVS status
- **Added**: Submission Readiness Status section
- **Added**: Conservative language about GDS generation
- **Fixed**: Workflow badge URLs

### 8. Documentation Added
- `docs/current_submission_status.md` - Live checklist
- `docs/submission_review.md` - This document

## What Still Needs Verification

The following must be verified by running CI:

1. **Verilog syntax check passes** - Test workflow
2. **All 16 cocotb tests pass** - Test workflow
3. **GDS workflow completes** - GDS workflow
4. **Precheck passes** - GDS workflow
5. **GL test passes** - GDS workflow
6. **No severe Yosys warnings** - Review synthesis logs
7. **Design not optimized away** - Check utilization report

## How to Verify

### Run Tests Locally

```bash
cd test
make SIM=icarus
```

### Trigger CI

Push to main branch or use workflow_dispatch:

```bash
git add .
git commit -m "Harden SilicaFold V0 for Tiny Tapeout submission"
git push origin main
```

### Check CI Results

1. Go to [GitHub Actions](https://github.com/rahulraonatarajan/silicafold-offlyn.ai-chip/actions)
2. Verify Test workflow passes
3. Verify GDS workflow passes (all 4 jobs)
4. Download and inspect artifacts

## Artifacts to Inspect

After GDS workflow succeeds:

| Artifact | Check For |
|----------|-----------|
| GDS file | File exists, reasonable size |
| Synthesis report | No errors, acceptable utilization |
| Timing report | No setup/hold violations |
| DRC report | Clean (from precheck) |
| LVS report | Clean (from precheck) |

## Ready for Submission?

**Not yet.** Wait until:

1. ✅ This commit is pushed
2. ⏳ Test workflow passes
3. ⏳ GDS workflow passes (all jobs)
4. ⏳ Artifacts are inspected
5. ⏳ `docs/current_submission_status.md` is updated with evidence

## Next Actions

1. Push this commit
2. Monitor CI at https://github.com/rahulraonatarajan/silicafold-offlyn.ai-chip/actions
3. If tests fail, fix issues and iterate
4. Once all CI passes, update `docs/current_submission_status.md`
5. Submit to Tiny Tapeout at https://tinytapeout.com

## Template Compliance

This repository follows the official Tiny Tapeout SKY Verilog template:
https://github.com/TinyTapeout/ttsky-verilog-template

Key compliance points:
- ✅ Uses `@ttsky26c` action
- ✅ `yaml_version: 6` at end of info.yaml
- ✅ Source files in `src/` directory
- ✅ Top module matches `tt_um_<username>_<project>` pattern
- ✅ Exact TT interface (ui_in, uo_out, uio_in, uio_out, uio_oe, ena, clk, rst_n)

## IP Boundary

This submission maintains the public/commercial IP boundary:

**Public (in this repo)**:
- Simplified TensorTile RTL
- Simplified PolicyGate RTL
- Testbench
- Documentation
- Generated GDS for the toy design

**Private (not disclosed)**:
- Production runtime
- Signed policy lifecycle
- Grant-token execution
- Secure policy storage
- Customer workflows
- Optimized commercial IP

# Current Submission Status

This document tracks the submission readiness of SilicaFold V0 for Tiny Tapeout.

**Last updated**: All CI workflows passing

## Checklist

| Item | Status | Evidence |
|------|--------|----------|
| Verilog syntax check | ✅ Passed | [Test workflow](https://github.com/rahulraonatarajan/silicafold-offlyn.ai-chip/actions/workflows/test.yml) |
| cocotb tests (16 tests) | ✅ Passed | [Test workflow](https://github.com/rahulraonatarajan/silicafold-offlyn.ai-chip/actions/workflows/test.yml) |
| GDS workflow passes | ✅ Passed | [GDS workflow](https://github.com/rahulraonatarajan/silicafold-offlyn.ai-chip/actions/workflows/gds.yaml) |
| GDS artifact generated | ✅ Passed | `tt_submission` artifact |
| Precheck | ✅ Passed | precheck job in GDS workflow |
| GL Test | ✅ Passed | gl_test job in GDS workflow |
| DRC report | ✅ Clean | Precheck reports |
| LVS report | ✅ Clean | Precheck reports |
| Yosys warnings reviewed | ✅ Done | No critical warnings |
| README claims verified | ✅ Done | Claims match artifacts |
| info.yaml validated | ✅ Done | Matches official template format |
| Template alignment | ✅ Done | Uses `@ttsky26c` action |
| Top module interface | ✅ Done | Exact TT interface |
| uio_oe configuration | ✅ Done | `8'b1111_0000` |
| No latches inferred | ✅ Verified | Synthesis passed |
| No combinational loops | ✅ Verified | Synthesis passed |
| No multiple drivers | ✅ Verified | Synthesis passed |

## How to Update This Document

After each CI run:

1. Check the [Test workflow](https://github.com/rahulraonatarajan/silicafold-offlyn.ai-chip/actions/workflows/test.yml) status
2. Check the [GDS workflow](https://github.com/rahulraonatarajan/silicafold-offlyn.ai-chip/actions/workflows/gds.yaml) status
3. Download artifacts and verify reports exist
4. Update the status column accordingly
5. Add links to specific runs as evidence

## Do Not Submit Unless

- [ ] All ⏳ items above are ✅
- [ ] No severe Yosys warnings remain
- [ ] Design is not optimized away (check utilization)
- [ ] All 16 cocotb tests pass
- [ ] GDS file is generated
- [ ] DRC and LVS are clean
- [ ] Timing meets 25 MHz target

## Workflow Information

### GDS Workflow (`gds.yaml`)

Uses the official Tiny Tapeout SKY130 action:

```yaml
uses: TinyTapeout/tt-gds-action@ttsky26c
```

This corresponds to the SKY130 26C shuttle. Verify the shuttle version at [tinytapeout.com](https://tinytapeout.com) before final submission.

### Test Workflow (`test.yml`)

Runs:
1. Verilog syntax check with Icarus Verilog
2. 16 cocotb tests covering TensorTile and PolicyGate

## Report Locations

After a successful GDS run, reports are located at:

| Report | Location |
|--------|----------|
| Synthesis | `runs/wokwi/*/reports/synthesis/` |
| Timing | `runs/wokwi/*/reports/signoff/` |
| DRC | Precheck job output |
| LVS | Precheck job output |
| Utilization | `runs/wokwi/*/reports/floorplan/` |

## Contact

If you need help with submission:
- Tiny Tapeout Discord: https://discord.gg/tinytapeout
- Documentation: https://tinytapeout.com/guides/

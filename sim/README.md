# Simulation Directory

## Purpose

This directory can store simulation outputs, waveform dumps, and related artifacts from local testing.

## Running Simulations

### Cocotb Tests

The primary simulation method uses cocotb:

```bash
cd test
make SIM=icarus
```

This will:
- Compile the Verilog with Icarus Verilog
- Run the Python testbench
- Report pass/fail status

### Waveform Generation

To generate waveforms (VCD format):

```bash
cd test
make SIM=icarus WAVES=1
```

The VCD file will be in `test/sim_build/`.

### Viewing Waveforms

Use GTKWave to view VCD files:

```bash
gtkwave test/sim_build/dump.vcd
```

Or use the VSCode VCD viewer extension.

## Directory Contents

You might store here:
- `*.vcd` - Waveform dumps (large, consider .gitignore)
- `*.log` - Simulation logs
- `*.txt` - Test output summaries
- Analysis scripts

## .gitignore Recommendations

Consider adding to `.gitignore`:
```
sim/*.vcd
sim/*.log
sim/build/
```

Waveform files can be large and are easily regenerated.

## Verification Checklist

```
[ ] All 10 cocotb tests pass
[ ] No Verilog syntax warnings
[ ] No X (unknown) states in simulation
[ ] Reset behavior correct
[ ] Timing reasonable (no zero-time loops)
```

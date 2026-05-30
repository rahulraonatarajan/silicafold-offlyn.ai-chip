# OpenROAD PPA Analysis Plan

## Overview

This document outlines the methodology for comparing architectural variants of TensorTile using OpenROAD to quantify area, timing, and power trade-offs.

## Objective

Compare three TensorTile variants to guide production architecture decisions:

1. **8-lane Unfurled**: Maximum parallelism, single-cycle computation
2. **4-lane Folded**: Balanced trade-off (current V0 implementation)
3. **2-lane Ultra-Folded**: Minimum area, multi-cycle computation

## Variants Description

### 8-Lane Unfurled Reference

```
Architecture:
- 8 parallel multipliers
- 8-input adder tree
- Single-cycle dot product
- Higher area, lower latency
```

Expected characteristics:
- Largest silicon area
- Highest power consumption
- Lowest latency (1 cycle)
- Highest throughput

### 4-Lane Folded (V0 Current)

```
Architecture:
- 4 parallel multipliers
- 4-input adder tree
- 2-cycle dot product
- Balanced area/latency
```

Expected characteristics:
- Medium silicon area
- Medium power consumption
- Medium latency (2 cycles)
- Medium throughput

### 2-Lane Ultra-Folded

```
Architecture:
- 2 parallel multipliers
- 2-input adder
- 4-cycle dot product
- Minimum area
```

Expected characteristics:
- Smallest silicon area
- Lowest power consumption
- Highest latency (4 cycles)
- Lowest throughput

## Metrics to Collect

### Area Metrics
- Total cell area (um²)
- Combinational logic area
- Sequential logic area
- Buffer/inverter overhead
- Routing overhead estimate

### Timing Metrics
- Critical path delay (ns)
- Setup slack at target frequency
- Hold slack
- Maximum achievable frequency
- Cycles per operation

### Power Metrics
- Total estimated power (mW)
- Dynamic power
- Leakage power
- Power at target frequency
- Energy per operation (pJ/op)

### Routing Metrics
- Total wirelength (um)
- Congestion hotspots
- Layer utilization
- Via count

### Composite Metrics
- Area-Latency Product (ALP)
- Energy-Delay Product (EDP)
- Area efficiency (ops/mm²/s)
- Power efficiency (ops/mW)

## Experimental Setup

### Tools
- Yosys for synthesis
- OpenROAD for place and route
- OpenSTA for timing analysis
- SKY130 PDK

### Process
1. Create RTL for each variant
2. Synthesize with identical constraints
3. Run floorplanning
4. Place and route
5. Extract metrics
6. Compare results

### Constraints
- Target frequency: 25 MHz (same as V0)
- Same I/O constraints
- Same power grid
- Same standard cell library

## Expected Results Template

| Metric | 8-Lane | 4-Lane | 2-Lane | Unit |
|--------|--------|--------|--------|------|
| Cell Area | - | - | - | um² |
| Combinational | - | - | - | um² |
| Sequential | - | - | - | um² |
| Critical Path | - | - | - | ns |
| Max Frequency | - | - | - | MHz |
| Cycles/Op | 1 | 2 | 4 | cycles |
| Total Power | - | - | - | mW |
| Dynamic Power | - | - | - | mW |
| Wirelength | - | - | - | um |
| ALP | - | - | - | um²·cycles |
| EDP | - | - | - | pJ·ns |

## Analysis Questions

1. **Area scaling**: Does area scale linearly with lanes?
2. **Timing closure**: Can all variants meet 25 MHz?
3. **Power efficiency**: Which is most energy-efficient per operation?
4. **Routing impact**: How does folding affect congestion?
5. **Optimal point**: For offline SLM agents, which trade-off is best?

## Presentation of Results

### Visualization
- Bar charts comparing metrics
- Pareto frontier (area vs latency)
- Power breakdown pie charts
- Layout comparison screenshots

### Publication-Ready
- Clear methodology section
- Reproducible results
- Statistical significance (multiple runs)
- Comparison with related work

## Automation Script Outline

```bash
#!/bin/bash
# PPA comparison automation

VARIANTS="unfurled_8lane folded_4lane ultrafolded_2lane"
RESULTS_DIR="ppa_results"

for variant in $VARIANTS; do
    echo "Processing $variant..."
    
    # Synthesis
    yosys -c synth_${variant}.tcl
    
    # Place and route
    openroad -c pnr_${variant}.tcl
    
    # Extract metrics
    python extract_metrics.py ${variant} > ${RESULTS_DIR}/${variant}.json
done

# Compare results
python compare_variants.py ${RESULTS_DIR}/*.json > comparison_report.md
```

## Important Notes

1. **Do not fabricate comparison variants** - This is simulation/synthesis study only

2. **V0 metrics come from Tiny Tapeout** - Do not substitute with local OpenROAD runs

3. **Results are estimates** - Actual silicon may differ

4. **Process-dependent** - Results specific to SKY130; other processes may differ

5. **Context matters** - "Best" depends on application requirements

## Next Steps After Analysis

Based on PPA results:
- Select architecture for V1 MPW
- Identify optimization opportunities
- Guide power budget allocation
- Inform memory interface design
- Prepare for commercial discussions

## References

- [OpenROAD Documentation](https://openroad.readthedocs.io/)
- [SKY130 PDK](https://skywater-pdk.readthedocs.io/)
- [OpenLane Flow](https://openlane.readthedocs.io/)

# SilicaFold - Long-Term ASIC Roadmap

## Overview

This roadmap outlines the evolution from V0 proof-of-silicon to potential commercial silicon IP for offline SLM agent systems.

## V0: Tiny Tapeout (Current)

**Status**: In Development

**Objectives**:
- Prove architectural concept in silicon
- Validate Tiny Tapeout flow
- Create public reference implementation
- Build open-source credibility

**Deliverables**:
- Simplified TensorTile (8-element INT4 dot product)
- Simplified PolicyGate (priority-based decision tree)
- Cocotb testbench
- Fabricated silicon via Tiny Tapeout
- Open-source documentation

**Limitations**:
- Educational only, not production-optimized
- No cryptographic security
- Limited throughput
- No SRAM/cache

## V0.5: FPGA Demonstration

**Status**: Planned

**Objectives**:
- Demonstrate hardware-in-loop operation
- Integrate with live SLM runtime
- Validate real-time PolicyGate decisions
- Collect performance data

**Deliverables**:
- FPGA bitstream (targeting accessible boards)
- Host software integration
- Live demo with offline SLM
- Performance characterization

**Target Platforms**:
- iCE40 (low-cost, open toolchain)
- ECP5 (more resources)
- Arty A7 (Xilinx, well-documented)

## V0.6: OpenROAD PPA Analysis

**Status**: Planned

**Objectives**:
- Compare architectural variants
- Quantify area/timing/power trade-offs
- Guide production architecture decisions
- Generate publication-quality data

**Comparisons**:
| Variant | Lanes | Cycles | Expected Trade-off |
|---------|-------|--------|-------------------|
| Unfurled 8-lane | 8 | 1 | Largest area, lowest latency |
| Folded 4-lane | 4 | 2 | Balanced (current V0) |
| Ultra-folded 2-lane | 2 | 4 | Smallest area, highest latency |

**Metrics**:
- Cell area (um²)
- Timing slack (ns)
- Estimated power (mW)
- Routed wirelength (um)
- Area-latency product

## V0.7: Open3DBench Research

**Status**: Research Phase

**Objectives**:
- Explore 3D integration concepts
- Study memory-near-compute benefits
- Investigate thermal implications
- Prepare for future 3D technology

**Study Configurations**:
1. 2D flat folded TensorTile (baseline)
2. 2D unfurled reference
3. 3D memory-on-logic (context buffer over TensorTile)
4. 3D logic-on-logic (TensorTile + control split)

**Metrics**:
- Wirelength reduction
- Timing improvement
- Power distribution
- Thermal hotspots
- Context bytes moved per score

**Note**: V0 does NOT prove 3D benefits. Open3DBench is a future research path.

## V1: MPW Prototype

**Status**: Future

**Objectives**:
- Production-oriented design
- Include essential peripherals
- Validate at larger scale
- Prepare for commercial development

**Features**:
- SRAM context buffer
- DMA controller
- Host bus interface (SPI/I2C or parallel)
- PolicyGate register file
- Telemetry/debug interface
- Multiple TensorTile instances

**Target Process**:
- SKY130 (open PDK) or
- Commercial process (GF, TSMC)

**Fabrication**:
- Google/Efabless MPW shuttle or
- Commercial MPW run

## V2: Commercial IP

**Status**: Long-term Vision

**Objectives**:
- Licensable silicon IP block
- Integration with edge SoCs
- OEM partnerships
- Revenue generation

**Potential Forms**:
- Soft IP (RTL for customer synthesis)
- Hard IP (GDSII for specific processes)
- FPGA IP core
- Chiplet for integration

**Features** (proprietary):
- Optimized TensorTile array
- Cryptographic PolicyGate
- Context attestation
- Secure audit logging
- High-bandwidth memory interface
- Power management

**Target Markets**:
- Industrial IoT
- Remote/field devices
- Edge AI appliances
- Automotive (future)
- Aerospace/defense (future)

## Timeline (Indicative)

```
2024 Q4: V0 Tiny Tapeout submission
2025 Q1: V0 silicon bring-up
2025 Q2: V0.5 FPGA demo
2025 Q3: V0.6 PPA analysis
2025 Q4: V0.7 3D research
2026 Q1: V1 MPW design
2026 Q3: V1 tape-out
2027+:   V2 commercial development
```

*Timeline is indicative and subject to change based on resources and priorities.*

## Investment Stages

| Stage | Investment | Output |
|-------|------------|--------|
| V0 | ~€1K | Proof of concept |
| V0.5 | ~€1K | Live demo |
| V0.6-V0.7 | Compute time | Research data |
| V1 | ~$50K-100K | MPW prototype |
| V2 | $1M+ | Commercial IP |

## Key Decisions Ahead

1. **Process selection for V1**: Stay with SKY130 or move to commercial?
2. **IP business model**: Sell IP or integrate into products?
3. **Security level**: What cryptographic features are required?
4. **Performance targets**: What throughput is commercially viable?
5. **Market focus**: Which vertical to prioritize?

## Risk Factors

- Tiny Tapeout shuttle delays
- Silicon bugs requiring re-spin
- Market timing for offline AI
- Competitive landscape changes
- Funding availability

## Success Metrics

**V0 Success**:
- Fabricated silicon works
- Tests pass on hardware
- Community engagement
- Learning objectives met

**V1 Success**:
- Production-viable performance
- Clean DRC/LVS
- Power within target
- Customer interest

**V2 Success**:
- Licensing revenue
- OEM partnerships
- Design wins
- Market presence

## Conclusion

SilicaFold V0 is the first step on a long road from educational proof-of-concept to commercial silicon IP. Each stage builds on the previous, validating assumptions and reducing risk before larger investments.

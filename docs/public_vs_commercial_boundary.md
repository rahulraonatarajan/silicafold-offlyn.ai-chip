# Public vs Commercial Boundary

## Overview

This document clarifies what is publicly shared in this repository versus what remains proprietary to Offlyn.ai's commercial development.

## Public (This Repository)

The following are intentionally public and safe to share:

### RTL Design
- Simplified TensorTile implementation
- Simplified PolicyGate implementation
- Top-level integration module
- Educational, non-optimized Verilog

### Infrastructure
- Tiny Tapeout metadata (info.yaml)
- Cocotb testbench
- GitHub Actions workflows
- Build scripts

### Documentation
- Architecture overview
- Limitations acknowledgment
- Cost estimates
- Bring-up plan
- Educational diagrams

### Generated Artifacts
- GDS from Tiny Tapeout flow
- OpenLane reports
- Synthesis results
- Layout renders

## Private / Commercial (Not in This Repository)

The following are NOT included and remain proprietary:

### Production Runtime
- Offlyn.ai SLM runtime integration
- Context management system
- KV cache optimization
- Model loading and inference
- Memory management

### Policy Infrastructure
- Signed policy lifecycle system
- Cryptographic grant tokens
- Secure policy storage
- Policy distribution network
- Customer-specific policy logic

### Security Systems
- Context validity attestation
- Audit digest infrastructure
- Tamper detection mechanisms
- Secure boot implementation
- Key management

### Commercial Silicon IP
- Optimized TensorTile variants
- Production PolicyGate with crypto
- High-performance MAC arrays
- Advanced context residency algorithms
- Memory movement optimization

### Business Systems
- Customer deployment workflows
- Field service integration
- Telemetry and monitoring
- P2P synchronization
- Licensing infrastructure

## Future Patentable Architecture

The following concepts may have patent potential and should be discussed with counsel before public disclosure:

- Context-gated tool execution
- Signed policy enforcement at silicon level
- Grant-token execution model
- Audit digest generation
- Context validity attestation

**This repository intentionally avoids detailed implementation of these concepts.**

## Investor Narrative

When discussing with investors:

### Safe to Share
- Public V0 demonstrates architectural feasibility
- Tiny Tapeout provides low-cost silicon validation
- Open-source approach builds community credibility
- Technical skills are proven through tape-out

### Position Carefully
- V0 is not the commercial product
- Real value is in the full stack (runtime, policy, audit)
- Silicon IP will be optimized and proprietary
- Public V0 supports broader IP strategy

### Do Not Disclose
- Specific commercial architecture details
- Customer-specific implementations
- Patent-pending innovations
- Production performance targets

## Resume Narrative

When presenting on resume or LinkedIn:

### Appropriate
- "Designed proof-of-silicon for offline SLM agents"
- "Completed Tiny Tapeout tape-out"
- "Implemented folded INT4 tensor primitive"
- "Built deterministic policy enforcement gate"

### Avoid
- Claiming production-grade design
- Overstating security properties
- Suggesting commercial readiness
- Revealing proprietary details

## Generated Public GDS

The GDS generated from this public repository:
- Is for the simplified, educational V0 design only
- Does not contain production Offlyn.ai IP
- Is safe to share with Tiny Tapeout and publicly
- Demonstrates fabrication feasibility, not commercial architecture

## Maintaining the Boundary

### When Contributing
- Do not add production code to this repository
- Keep all implementations simplified and educational
- Avoid optimization that could reveal commercial approaches
- Document limitations clearly

### When Forking
- Forks inherit the Apache-2.0 license
- Commercial derivatives should be developed separately
- Do not merge proprietary code into public forks

### When Discussing
- Clearly distinguish V0 from production plans
- Emphasize educational and research nature
- Do not speculate about commercial implementation details
- Refer questions about production to Offlyn.ai

## Summary

| Category | Status | Location |
|----------|--------|----------|
| Simplified RTL | Public | This repo |
| Testbench | Public | This repo |
| Documentation | Public | This repo |
| Generated GDS | Public | CI artifacts |
| Production runtime | Private | Offlyn.ai internal |
| Policy system | Private | Offlyn.ai internal |
| Security implementation | Private | Offlyn.ai internal |
| Optimized silicon IP | Private | Offlyn.ai internal |

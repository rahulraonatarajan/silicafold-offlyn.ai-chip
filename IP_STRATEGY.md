# IP Strategy

## Overview

This document outlines the intellectual property strategy for SilicaFold V0, distinguishing between public educational content and proprietary commercial IP.

## What Is Safe to Publish

The following are intentionally public and included in this repository:

### Public RTL
- **Simplified TensorTile RTL**: Basic 8-element INT4 dot product with 4-lane folded MAC
- **Simplified PolicyGate RTL**: Priority-based decision tree without cryptographic security
- **Top-level integration**: Simple multiplexing between blocks

### Public Infrastructure  
- **Tiny Tapeout metadata**: info.yaml, pinout configuration
- **Testbench**: Cocotb tests demonstrating functionality
- **Documentation**: Architecture overview, limitations, usage guides
- **CI/CD workflows**: GitHub Actions for testing and GDS generation
- **Educational diagrams**: Block diagrams, data flow illustrations

### Public Artifacts
- **Generated GDS**: From the simplified public design only
- **OpenLane reports**: Synthesis, timing, area from public design
- **Test results**: Simulation outputs

## What Should Remain Private

The following are proprietary Offlyn.ai IP and are NOT included:

### Production Runtime
- SLM runtime integration code
- Context management algorithms
- KV cache optimization strategies
- Memory movement optimization
- Model serving infrastructure

### Policy Infrastructure
- Signed policy lifecycle system
- Cryptographic grant-token architecture
- Secure policy storage implementation
- Policy distribution protocols
- Customer-specific policy logic

### Security Systems
- Context validity/attestation system
- Audit digest generation algorithms
- Tamper detection mechanisms
- Secure boot implementation
- Key management infrastructure
- P2P synchronization protocols

### Commercial Silicon IP
- Optimized TensorTile implementations
- Production PolicyGate with crypto
- Advanced MAC array architectures
- Memory controller designs
- High-performance variants

### Business Systems
- Customer deployment workflows
- Field service integration
- Telemetry and monitoring systems
- Licensing infrastructure
- Pricing and packaging

## Patent-Sensitive Areas

The following concepts may have patent potential. **Consult legal counsel before public disclosure of detailed implementations:**

- Context-gated tool execution
- Signed policy enforcement at silicon level
- Grant-token execution model
- Audit digest generation for offline agents
- Context validity attestation
- Hardware-assisted SLM agent safety

**This repository intentionally uses simplified implementations that avoid disclosing potential patent claims.**

## How to Avoid Over-Disclosure

When contributing to or extending this repository:

1. **Keep implementations simple**: Don't optimize in ways that reveal commercial architecture
2. **Avoid security details**: Don't add cryptographic implementations
3. **Use generic patterns**: Prefer common techniques over novel approaches
4. **Document limitations**: Make clear what V0 does NOT include
5. **Review before committing**: Consider IP implications of changes

## Public Description Guidelines

### For Technical Audiences
> "SilicaFold V0 is a proof-of-silicon artifact demonstrating simplified primitives for offline SLM agent systems. It includes a folded INT4 tensor computation unit and a deterministic policy gate, implemented as a Tiny Tapeout project."

### For Investors
> "SilicaFold V0 validates key architectural concepts for Offlyn.ai's offline SLM agent platform. The public V0 demonstrates feasibility without disclosing production IP. The commercial value lies in the full stack: runtime integration, secure policy enforcement, and optimized silicon IP."

### For Resume/LinkedIn
> "Designed SilicaFold V0, an open-silicon Tiny Tapeout prototype for offline SLM-agent infrastructure, combining a folded INT4 tensor/context primitive with a deterministic PolicyGate for chip-level tool-call authorization."

## What NOT to Claim

Do not claim that SilicaFold V0:
- Is production-ready
- Implements secure policy enforcement
- Provides cryptographic guarantees
- Represents Offlyn.ai's commercial architecture
- Competes with commercial AI accelerators
- Contains novel patentable implementations

## IP Protection Measures

### For This Repository
- Apache-2.0 license (permissive, but requires attribution)
- Clear documentation of limitations
- Simplified implementations only
- No production code

### For Commercial Development
- Separate repositories (private)
- Different module names
- Independent development history
- Proper IP assignment agreements

## Summary Table

| Content | Status | Location |
|---------|--------|----------|
| Simplified TensorTile | Public | This repo |
| Simplified PolicyGate | Public | This repo |
| Testbench | Public | This repo |
| Documentation | Public | This repo |
| Generated GDS | Public | CI artifacts |
| Production runtime | Private | Offlyn internal |
| Policy system | Private | Offlyn internal |
| Security implementation | Private | Offlyn internal |
| Optimized silicon IP | Private | Offlyn internal |
| Patent-sensitive details | Private | Offlyn internal |

## Contact

For questions about IP strategy or commercial licensing:
- Internal: Contact Offlyn.ai leadership
- External: Inquire through official Offlyn.ai channels

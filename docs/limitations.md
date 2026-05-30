# SilicaFold V0 - Limitations

## What SilicaFold V0 Does NOT Do

This document clarifies what SilicaFold V0 is NOT and what it does NOT implement. This is important for setting correct expectations and understanding the scope of this proof-of-silicon artifact.

### Not an AI Chip

SilicaFold V0 does NOT:
- Run an SLM (Small Language Model)
- Perform neural network inference
- Understand natural language
- Generate text or responses
- Implement attention mechanisms beyond simple QK dot product

The SLM runs on the host system. SilicaFold only computes a small math primitive (TensorTile) and evaluates structured policy decisions (PolicyGate).

### Not a Transformer Accelerator

SilicaFold V0 does NOT implement:
- Full multi-head attention
- Softmax computation
- Layer normalization
- Feed-forward networks (MLP)
- RoPE (Rotary Position Embedding)
- KV cache management
- Token embedding lookups
- Full transformer layers

TensorTile is a simplified QK dot-product primitive, not a complete transformer accelerator.

### Not a TPU/NPU Replacement

SilicaFold V0 does NOT:
- Replace Google TPU
- Replace Apple Neural Engine
- Replace NVIDIA CUDA cores
- Replace Google Coral EdgeTPU
- Replace NVIDIA Jetson
- Compete with commercial AI accelerators
- Provide competitive TOPS (Tera Operations Per Second)

This is a Tiny Tapeout educational project, not a commercial AI accelerator.

### Not Security Hardware

SilicaFold V0 does NOT implement:
- Cryptographic policy verification
- Digital signatures for policy enforcement
- Secure boot
- Hardware root of trust
- Tamper detection or resistance
- Secure key storage
- Hardware security module (HSM) features
- Side-channel attack resistance

PolicyGate is a toy demonstration of the concept. Production security requires proper cryptographic implementation.

### Not Production-Ready

SilicaFold V0 does NOT:
- Prove commercial performance
- Demonstrate production-grade reliability
- Include proper error handling for all edge cases
- Implement power management
- Support high-speed interfaces
- Include self-test or BIST
- Meet automotive/aerospace/medical certification

This is a proof-of-concept, not a production design.

### Not Offlyn.ai Production IP

This repository does NOT contain:
- Offlyn.ai production runtime code
- Proprietary policy lifecycle system
- Signed grant-token architecture
- Context validity/attestation system
- Audit digest infrastructure
- Customer-specific workflows
- Optimized commercial silicon IP
- Advanced memory movement algorithms
- P2P synchronization logic

Those are proprietary Offlyn.ai systems outside the scope of this public V0.

## What SilicaFold V0 DOES Do

For clarity, here's what V0 actually demonstrates:

1. **Folded INT4 QK Computation**: An 8-element dot product using 4-lane folded MAC over 2 cycles

2. **Deterministic Policy Gate**: A priority-ordered decision tree for allow/block/require-human outcomes

3. **Tiny Tapeout Integration**: Compliance with the Tiny Tapeout interface for actual silicon fabrication

4. **Architectural Concept**: Separation of compute (TensorTile) from authority (PolicyGate) for offline SLM agents

5. **Open-Source Reference**: A starting point for research into silicon-assisted SLM agent safety

## Summary

| Capability | V0 Status |
|------------|-----------|
| Run SLM inference | No |
| Full transformer | No |
| Cryptographic security | No |
| Commercial performance | No |
| Production reliability | No |
| INT4 dot product | Yes |
| Policy decision tree | Yes |
| Tiny Tapeout compatible | Yes |
| Educational reference | Yes |
| Open source | Yes |

This is an educational proof-of-silicon, not a commercial product.

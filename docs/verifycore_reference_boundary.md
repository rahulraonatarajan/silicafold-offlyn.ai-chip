# VerifyCore Reference Boundary

## Purpose

SilicaFold V0 is a narrow hardware-backed reference artifact that can support future VerifyCore patent and paper work. This document defines how SilicaFold connects to VerifyCore without overclaiming.

SilicaFold demonstrates that a deterministic policy-gated actuation primitive is hardware-reducible and synthesizes cleanly on a TinyTapeout-scale die. It provides simulation-verified RTL evidence for a subset of the broader VerifyCore architecture. SilicaFold does not claim to be the complete VerifyCore system.

## Repository Relationship

| Repository | Role |
|------------|------|
| **SilicaFold** — [github.com/offlyn-ai/silicafold-offlyn.ai-chip](https://github.com/offlyn-ai/silicafold-offlyn.ai-chip) | Hardware primitive / evidence artifact |
| **VerifyCore** — [github.com/rahulraonatarajan/offlyn-verify-core](https://github.com/rahulraonatarajan/offlyn-verify-core) | Broader policy-at-actuation-boundary architecture |

**Relationship:**

- SilicaFold is the hardware primitive and evidence artifact.
- VerifyCore is the broader policy-at-actuation-boundary architecture.
- SilicaFold should be cited as supporting evidence, not as the full VerifyCore implementation.
- Broader system claims (signed policies, context attestation, authenticated command channels, audit integrity) belong to VerifyCore materials.

## What SilicaFold Can Support

| SilicaFold Evidence | VerifyCore Claim Theme | Safe Interpretation | Limitation |
|---------------------|------------------------|---------------------|------------|
| PolicyGate RTL decision tree | Deterministic policy enforcement at actuation boundary | A priority-ordered decision tree implements in combinational logic and synthesizes cleanly | Single evaluation only; no state machine for multi-step authorization |
| HIGH risk requires human approval | Human-in-the-loop gating for high-risk actions | `risk_class=HIGH` without `human_approved` triggers `REQUIRE_HUMAN` | Runtime sets `risk_class`; hardware does not independently classify risk |
| EMERGENCY path scoped to safety-critical tools | Bounded emergency override | Priority 5 applies only to tool IDs 0x1–0x3 and always sets `log_required` | No time-limited tokens or per-session counters |
| Offline medium-risk logging | Audit trail for offline actions | `offline_mode=1` + `risk_class >= MEDIUM` sets `log_required` | 4-bit counter only; no cryptographic audit digest |
| Audit counter persistence | Tamper evidence via counter | `audit_counter` survives `CMD_RESET_STATE` | Counter wraps at 15; not cryptographically protected |
| TensorTile context scoring | Hardware-assisted context validity | Folded INT4 dot product produces a context score | Score interpretation and threshold are runtime responsibility |
| Compute/authority separation | Separation of concerns on-die | `BLOCK_SELECT` muxes TensorTile and PolicyGate | Single die only; no inter-chip authority delegation |
| TinyTapeout hardware publication path | Open-silicon feasibility evidence | GDS, DRC, LVS, and gate-level tests pass | Educational proof-of-silicon; not production-certified |

## What SilicaFold Does Not Prove

SilicaFold V0 is an educational proof-of-concept. It does **not** prove:

- **Production security** — No formal security analysis or penetration testing
- **Cryptographic policy verification** — `policy_ok` is a single bit set by trusted runtime
- **Secure boot** — No measured boot chain; PolicyGate trusts its initial state
- **Authenticated pins** — No challenge-response or signed command packets on `ui_in`
- **Replay protection** — No nonce or timestamp; same packet can be re-evaluated
- **Append-only audit digests** — 4-bit counter only; no cryptographic log chaining
- **Tamper resistance** — No physical countermeasures; direct pin access bypasses runtime
- **Full VerifyCore system behavior** — Missing signed policies, context attestation, networked enforcement
- **Regulatory or safety certification** — Not evaluated against any safety standard (IEC 61508, ISO 26262, etc.)

These limitations are expected for a TinyTapeout-scale educational artifact. Production VerifyCore implementations address them through extensions described in [offlyn_verify_core_integration.md](offlyn_verify_core_integration.md) and [long_term_asic_roadmap.md](long_term_asic_roadmap.md).

## Patent and Publication Safety

This repository is intended as hardware-backed feasibility evidence. It is **not** a patent filing.

**Key guidance:**

- Public docs should not be treated as a substitute for provisional or non-provisional patent applications.
- Public disclosure timing and claim scope should be coordinated with patent counsel before publishing claims broader than the V0 implementation.
- Broad system claims (signed policy lifecycle, context attestation, authenticated command channels, hardware audit digests) should live in VerifyCore patent materials and the VerifyCore repo.
- SilicaFold should be used as hardware-backed feasibility evidence only where accurate.
- Do not claim production security, tamper resistance, or certification based on V0 artifacts alone.

**Safe public claims:**

- "SilicaFold demonstrates a deterministic RTL decision tree for tool-call authorization."
- "The PolicyGate primitive synthesizes cleanly on SKY130 via the TinyTapeout flow."
- "Simulation tests validate the documented priority behavior against RTL."

**Unsafe claims (avoid without patent/paper coordination):**

- "SilicaFold provides cryptographically secure policy enforcement."
- "The hardware guarantees safe AI actuation."
- "SilicaFold is a complete VerifyCore implementation."

## Related Documents

| Document | Purpose |
|----------|---------|
| [offlyn_verify_core_integration.md](offlyn_verify_core_integration.md) | Layered architecture and V0.5 integration plan |
| [policygate_threat_model.md](policygate_threat_model.md) | Threat landscape and V0 defenses |
| [use_cases.md](use_cases.md) | RTL-validated offline-agent scenarios |
| [limitations.md](limitations.md) | V0 non-goals |
| [tinytapeout_paper_readiness.md](tinytapeout_paper_readiness.md) | Paper publication checklist |
| [patent_publication_sequence.md](patent_publication_sequence.md) | Publication and patent coordination |

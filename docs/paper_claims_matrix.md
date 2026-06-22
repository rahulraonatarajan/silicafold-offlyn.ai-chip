# Paper Claims Matrix

## Purpose

This document keeps SilicaFold paper claims evidence-backed. Every claim in a paper or public document should be traceable to a specific artifact in this repository. Use this matrix to ensure accurate wording and avoid overclaims.

## Claims Matrix

| Paper Claim | Evidence in Repo | Test or Artifact | Safe Wording | Unsafe Wording to Avoid |
|-------------|------------------|------------------|--------------|-------------------------|
| **Deterministic hardware policy gate** | `src/sf_policygate_core.v` | `test/test_combined.py` (16 tests pass) | "The priority-ordered decision tree implements in combinational Verilog and produces deterministic outputs for a given input state." | "The hardware guarantees safe AI actuation." / "Cryptographically secure policy enforcement." |
| **Structured tool-call packet evaluation** | `src/sf_policygate_core.v` command encoding | `test/test_combined.py` CMD_LOAD/CMD_EVALUATE tests | "PolicyGate evaluates structured 4-bit tool ID, 2-bit risk class, and flag fields loaded via a defined command sequence." | "The chip understands AI intent." / "Natural language policy enforcement." |
| **Human approval gating for HIGH risk** | Priority 3 in `sf_policygate_core.v` | `test_use_case_2_field_drone_motor_actuation`, `test_use_case_1_disaster_response_high_risk_requires_human` | "When `risk_class=HIGH` and `human_approved=0`, PolicyGate returns `REQUIRE_HUMAN` regardless of `emergency_mode`." | "The hardware prevents all unsafe high-risk actions." / "Human-in-the-loop is cryptographically enforced." |
| **Emergency path scoped to safety-critical tools** | Priority 5 in `sf_policygate_core.v`, `tool_is_safety_critical` signal | `test_use_case_1_disaster_response_emergency_risk` | "The emergency allow path (Priority 5) applies only to safety-critical tool IDs (0x1–0x3) and always sets `log_required`." | "Emergency mode bypasses all safety checks." / "Any tool can use emergency override." |
| **Offline medium-risk logging** | Priority 6 default allow logic | `test_use_case_3_enterprise_export_offline_log` | "`offline_mode=1` combined with `risk_class >= MEDIUM` sets `log_required` on the default allow path." | "All offline actions are securely logged." / "Audit trail is tamper-proof." |
| **Battery-aware blocking of nonessential tools** | Priority 4 in `sf_policygate_core.v`, `tool_is_nonessential` signal | `test_use_case_4_battery_low_nonessential_block` | "When `battery_low=1`, nonessential tool IDs (0x8–0xF) are blocked with `log_required`." | "Power management is cryptographically enforced." |
| **Audit counter persistence across soft reset** | `audit_counter` register, reset logic | `test_audit_counter_persists_across_soft_reset` in baseline tests | "The 4-bit `audit_counter` increments on logged evaluations and is not cleared by `CMD_RESET_STATE`." | "Tamper-proof audit trail." / "Cryptographic audit integrity." |
| **TensorTile context scoring** | `src/sf_tensortile_core.v` | `test_use_case_5_tensortile_context_scoring_then_policygate`, folded QK tests | "TensorTile computes an 8-element INT4 dot product in 2 cycles using a folded 4-lane MAC." | "AI context understanding in hardware." / "Semantic context verification." |
| **Compute/authority separation** | `BLOCK_SELECT` mux in top module | Tests alternate between BLOCK_TENSORTILE and BLOCK_POLICYGATE | "Compute (TensorTile) and authority (PolicyGate) are separated via `BLOCK_SELECT` on a single die." | "Secure isolation between compute and policy." / "Hardware-enforced privilege separation." |
| **TinyTapeout hardware evidence** | GDS workflow, DRC/LVS reports | GitHub Actions `gds` workflow passes | "The design passes OpenLane synthesis, DRC, and LVS on the TinyTapeout SKY130 flow." | "Production-ready silicon." / "Certified hardware." |

## Risk Class Nuance

**Critical distinction:** `risk_class=HIGH` + `emergency_mode=1` does **not** automatically allow actuation.

| Scenario | Risk Class | Emergency Mode | Human Approved | Decision | Test |
|----------|------------|----------------|----------------|----------|------|
| Emergency beacon, EMERGENCY risk | EMERGENCY (3) | 1 | 0 | ALLOW + emergency_path + log | `test_use_case_1_disaster_response_emergency_risk` |
| Emergency beacon, HIGH risk | HIGH (2) | 1 | 0 | REQUIRE_HUMAN + log | `test_use_case_1_disaster_response_high_risk_requires_human` |
| Motor actuation, HIGH risk | HIGH (2) | 0 | 0 | REQUIRE_HUMAN + log | `test_use_case_2_field_drone_motor_actuation` |

**Safe wording:** "The emergency allow path requires `risk_class=EMERGENCY` (3), not `risk_class=HIGH` (2). Priority 3 (HIGH risk without approval) fires before Priority 5 (emergency) in the decision tree."

**Unsafe wording:** "Emergency mode allows high-risk actions."

## Wording Guidelines

### Use These Phrases

- "proof-of-concept"
- "prototype"
- "hardware-backed evidence"
- "deterministic policy primitive"
- "educational artifact"
- "TinyTapeout-scale"
- "simulation-validated"
- "synthesizes cleanly"
- "future production direction"
- "candidate architecture"
- "requires further validation"

### Avoid These Phrases

- "tamper-proof"
- "secure chip"
- "cryptographically secure"
- "production ready"
- "certified"
- "guarantees safety"
- "prevents malicious agents"
- "full hardware VerifyCore"
- "patented" (unless referencing an actual filing)
- "AI safety solution"
- "complete policy enforcement"

## Claim Review Checklist

Before adding a claim to a paper or public document:

1. ☐ Is there a specific source file in the repo that implements the claimed behavior?
2. ☐ Is there a passing test that validates the behavior?
3. ☐ Does the wording match what the test actually checks?
4. ☐ Does the claim avoid implying security, certification, or production readiness?
5. ☐ Does the claim avoid disclosing proprietary VerifyCore implementation details?
6. ☐ Has the claim been reviewed against the "Unsafe Wording" column above?

## Related Documents

| Document | Purpose |
|----------|---------|
| [tinytapeout_paper_readiness.md](tinytapeout_paper_readiness.md) | Paper publication checklist |
| [verifycore_reference_boundary.md](verifycore_reference_boundary.md) | What SilicaFold can and cannot support |
| [patent_publication_sequence.md](patent_publication_sequence.md) | Publication and patent coordination |
| [use_cases.md](use_cases.md) | RTL-validated scenarios |
| [limitations.md](limitations.md) | V0 non-goals |
| [policygate_threat_model.md](policygate_threat_model.md) | Threat landscape and V0 defenses |

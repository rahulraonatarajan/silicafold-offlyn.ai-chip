# TinyTapeout Paper Readiness

## Paper Goal

**"SilicaFold: A TinyTapeout Hardware Primitive for Policy-Gated Offline AI Actuation"**

This document tracks readiness for a narrow hardware-backed data paper describing the SilicaFold V0 TinyTapeout design. The paper should demonstrate that a deterministic policy-gated actuation primitive is hardware-reducible and synthesizes cleanly on an open-source silicon flow.

## Evidence Status

| Evidence Item | Current Status | File / Artifact | Paper-Safe Claim | Remaining Work |
|---------------|----------------|-----------------|------------------|----------------|
| RTL implementation | ✅ Complete | `src/sf_policygate_core.v`, `src/sf_tensortile_core.v` | "A 6-priority decision tree synthesizes in combinational Verilog." | None |
| cocotb baseline tests | ✅ Complete | `test/test_combined.py` (16 tests) | "Baseline RTL behavior validated via cocotb simulation." | None |
| Use-case validation tests | ✅ Complete | `test/test_use_cases.py` (6 tests) | "Five documented scenarios match RTL outputs in simulation." | None |
| Synthesis/gate-level evidence | ✅ GDS passes | GitHub Actions `gds` workflow, DRC/LVS clean | "The design passes OpenLane synthesis and verification on SKY130." | Include synthesis metrics (area, cell count) in paper |
| TinyTapeout submission status | 🟡 Pre-submission | `docs/current_submission_status.md` | "Design targets TinyTapeout fabrication." | Complete submission; update status after tape-out |
| Post-silicon bring-up status | ⬜ Not started | `docs/bringup_plan.md` | N/A until silicon arrives | Execute bring-up after fabrication |
| Measured RTL outputs | ✅ Complete | `docs/use_cases.md` Simulation Validation table | "Simulation outputs match documented decision priorities." | None |
| Known limitations | ✅ Documented | `docs/limitations.md`, `docs/policygate_threat_model.md` | "V0 is an educational proof-of-silicon, not production security." | Ensure paper includes limitations section |
| VerifyCore reference boundary | ✅ Documented | `docs/verifycore_reference_boundary.md` | "SilicaFold is a hardware primitive supporting broader VerifyCore work." | None |

## Claim Discipline

### What SilicaFold Proves

The paper may safely claim:

- A priority-ordered policy decision tree implements in combinational logic and synthesizes on SKY130.
- Simulation tests (22/22 passing) validate deterministic allow/block/require-human behavior.
- HIGH-risk actions without human approval trigger `REQUIRE_HUMAN`.
- EMERGENCY path is scoped to safety-critical tool IDs (0x1–0x3) and always logs.
- Offline medium-risk actions set `LOG_REQUIRED` for audit.
- Battery-low mode blocks nonessential tools (IDs 0x8–0xF).
- `audit_counter` survives soft reset, providing basic tamper evidence.
- TensorTile computes a folded INT4 dot product for context scoring.
- Compute (TensorTile) and authority (PolicyGate) are separated via `BLOCK_SELECT`.
- The design passes DRC and LVS on the TinyTapeout/OpenLane flow.

### What SilicaFold Does Not Prove

The paper must **not** claim:

- Production-grade security or performance.
- Cryptographic policy verification or signed policy enforcement.
- Tamper resistance, secure boot, or authenticated pins.
- Replay protection or append-only audit digests.
- Full VerifyCore system behavior.
- Regulatory or safety certification (IEC 61508, ISO 26262, etc.).
- Guaranteed AI safety or prevention of malicious agents.

### What Belongs to Future VerifyCore Work

Broader claims belong to VerifyCore patent materials and the VerifyCore paper:

- Signed policy lifecycle and cryptographic verification at load time.
- Context attestation via signed hash before `context_valid` is set.
- Authenticated command channels (challenge-response, signed packets).
- Hardware audit digests with cryptographic chaining.
- Secure boot and measured boot chain.
- Multi-chip or networked policy enforcement.
- Runtime integration beyond trusted flag-setting.

## Publication Sequence

| Step | Action | Status |
|------|--------|--------|
| 1 | Merge RTL-backed PR with tests passing | ✅ Done (PR #2) |
| 2 | Confirm tests and TinyTapeout flow | ✅ CI passing |
| 3 | Complete TinyTapeout submission | 🟡 Pending |
| 4 | Draft/publish SilicaFold as narrow hardware-backed paper | ⬜ Not started |
| 5 | Use SilicaFold as supporting evidence for VerifyCore | ⬜ After SilicaFold paper |
| 6 | Coordinate VerifyCore patent materials before broad public disclosure | ⬜ With patent counsel |
| 7 | Publish VerifyCore paper after claim boundaries are clear | ⬜ After patent coordination |

## Suggested Paper Outline

1. **Abstract** — One-paragraph summary of the hardware primitive and its role in offline AI safety.
2. **Introduction** — Motivation: policy-at-actuation-boundary for offline agents.
3. **Design** — TensorTile and PolicyGate architecture, decision tree, signal definitions.
4. **Implementation** — TinyTapeout flow, SKY130, area/utilization, OpenLane synthesis.
5. **Validation** — cocotb test methodology, use-case scenarios, measured outputs table.
6. **Limitations** — Explicit statement of what V0 does not prove (see above).
7. **Future Work** — VerifyCore extensions, signed policies, context attestation, audit digests.
8. **Conclusion** — Hardware-reducibility of deterministic policy gating demonstrated.

## Artifacts Checklist for Paper Submission

| Artifact | Location | Ready |
|----------|----------|-------|
| RTL source | `src/*.v` | ✅ |
| Test suite | `test/test_combined.py`, `test/test_use_cases.py` | ✅ |
| GDS render | `assets/gds_render.png` | ✅ |
| Synthesis reports | GitHub Actions `gds` workflow | ✅ |
| DRC/LVS reports | GitHub Actions precheck | ✅ |
| Use-case validation table | `docs/use_cases.md` | ✅ |
| Limitations doc | `docs/limitations.md` | ✅ |
| Threat model | `docs/policygate_threat_model.md` | ✅ |
| VerifyCore boundary doc | `docs/verifycore_reference_boundary.md` | ✅ |

## Related Documents

| Document | Purpose |
|----------|---------|
| [verifycore_reference_boundary.md](verifycore_reference_boundary.md) | What SilicaFold can and cannot support |
| [paper_claims_matrix.md](paper_claims_matrix.md) | Evidence-backed claim wording |
| [patent_publication_sequence.md](patent_publication_sequence.md) | Publication and patent coordination |
| [use_cases.md](use_cases.md) | RTL-validated scenarios |
| [limitations.md](limitations.md) | V0 non-goals |

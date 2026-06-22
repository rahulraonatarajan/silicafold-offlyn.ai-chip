# Patent and Publication Sequence

## Purpose

This document aligns SilicaFold publication with VerifyCore patent strategy. It defines a clear sequence for public disclosure to preserve patent claim scope while demonstrating hardware feasibility.

## Publication Strategy Overview

| Order | Artifact | Purpose |
|-------|----------|---------|
| **1. SilicaFold first** | Narrow hardware-backed TinyTapeout data paper | Demonstrate hardware-reducibility of a deterministic policy primitive |
| **2. VerifyCore second** | Broader patent and paper architecture | Claim the full policy-at-actuation-boundary architecture |

**Key principle:** SilicaFold should support VerifyCore as evidence, not replace it.

## Sequence Table

| Stage | Artifact | Repo | Purpose | Risk if Overclaimed | Safe Next Step |
|-------|----------|------|---------|---------------------|----------------|
| 1 | SilicaFold RTL validation | [silicafold-offlyn.ai-chip](https://github.com/offlyn-ai/silicafold-offlyn.ai-chip) | Prove hardware-reducibility of a policy primitive | Disclosure of broader claims before patent filing | Keep claims narrow to V0 implementation |
| 2 | SilicaFold TinyTapeout paper | SilicaFold repo | Publish narrow hardware-backed data paper | Over-claiming may establish prior art against own patent | Use paper claims matrix; avoid security/certification language |
| 3 | VerifyCore provisional/patent materials | [offlyn-verify-core](https://github.com/rahulraonatarajan/offlyn-verify-core) (private sections) | File patent claims for broader architecture | Public disclosure before filing loses patent rights | File provisional before broad public claims |
| 4 | VerifyCore paper | VerifyCore repo | Publish architecture paper after claim protection | Disclosure of implementation details before filing | Coordinate with patent counsel on timing |
| 5 | Future production implementation | Private/commercial | Deploy production-grade system | Public disclosure of proprietary methods | Keep production IP separate from public repos |

## Patent Safety Guidelines

### Before Publishing SilicaFold Paper

1. **Review claim scope:** Ensure paper claims are limited to what V0 actually implements.
2. **Avoid broader claims:** Do not claim signed policies, context attestation, authenticated channels, or audit digests.
3. **Use "future work" framing:** Extensions belong to VerifyCore, not SilicaFold claims.
4. **Reference, don't disclose:** Link to VerifyCore repo without disclosing proprietary implementation details.

### Before Publishing VerifyCore Claims

1. **Consult patent counsel:** Coordinate public disclosure timing with provisional or non-provisional filing.
2. **Identify claim scope:** Distinguish between:
   - Claims supported by SilicaFold evidence (hardware primitive)
   - Claims broader than SilicaFold (system architecture, cryptographic enforcement)
3. **Protect novel methods:** Do not publish implementation details for novel methods before filing.
4. **Use SilicaFold as evidence:** Cite SilicaFold to support feasibility claims where accurate.

## What Belongs Where

| Claim Type | Appropriate Location | Notes |
|------------|----------------------|-------|
| Deterministic RTL decision tree | SilicaFold paper | Supported by V0 evidence |
| TinyTapeout synthesis feasibility | SilicaFold paper | Supported by GDS/DRC/LVS |
| Simulation-validated use cases | SilicaFold paper | Supported by cocotb tests |
| Policy-at-actuation-boundary architecture | VerifyCore patent/paper | Broader than V0 |
| Signed policy lifecycle | VerifyCore patent/paper | Not implemented in V0 |
| Context attestation | VerifyCore patent/paper | Not implemented in V0 |
| Authenticated command channels | VerifyCore patent/paper | Not implemented in V0 |
| Hardware audit digests | VerifyCore patent/paper | Not implemented in V0 |
| Production security claims | VerifyCore patent/paper (after validation) | Not supported by V0 |

## Disclosure Timeline Guidance

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DISCLOSURE TIMELINE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [NOW]  SilicaFold V0 RTL and tests in public repo                  │
│         ├── Safe: Narrow implementation details                     │
│         └── Safe: TinyTapeout-scale hardware evidence               │
│                                                                     │
│  [NEXT] SilicaFold TinyTapeout paper submission                     │
│         ├── Safe: Deterministic policy primitive                    │
│         ├── Safe: Simulation validation                             │
│         └── Caution: Keep claims narrow to V0                       │
│                                                                     │
│  [BEFORE VERIFYCORE PAPER] File VerifyCore provisional              │
│         ├── Required: Claims broader than V0 implementation         │
│         ├── Required: Signed policies, context attestation          │
│         └── Required: Novel methods not disclosed in SilicaFold     │
│                                                                     │
│  [AFTER FILING] VerifyCore paper publication                        │
│         ├── Safe: Architecture description                          │
│         ├── Safe: Cite SilicaFold as feasibility evidence           │
│         └── Caution: Implementation details per counsel advice      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Repository Links

| Repository | Role | Visibility |
|------------|------|------------|
| [SilicaFold](https://github.com/offlyn-ai/silicafold-offlyn.ai-chip) | Hardware primitive / evidence artifact | Public |
| [VerifyCore](https://github.com/rahulraonatarajan/offlyn-verify-core) | Broader policy-at-actuation-boundary architecture | Public (architecture) / Private (implementation details) |

## Claims Requiring Patent Counsel Review

The following claim areas should be reviewed with patent counsel before public disclosure:

1. **Novel priority decision tree** — Is the specific priority ordering patentable?
2. **Policy-at-actuation-boundary architecture** — System-level claims beyond V0.
3. **Context attestation methods** — Novel methods for context validity verification.
4. **Bounded emergency override** — Time-limited tokens, per-session counters.
5. **Hardware audit digests** — Append-only cryptographic logging in silicon.
6. **Authenticated command channels** — Challenge-response or signed packet methods.
7. **Compute/authority separation** — Architectural claim for on-die separation.

## Related Documents

| Document | Purpose |
|----------|---------|
| [verifycore_reference_boundary.md](verifycore_reference_boundary.md) | What SilicaFold can and cannot support |
| [tinytapeout_paper_readiness.md](tinytapeout_paper_readiness.md) | Paper publication checklist |
| [paper_claims_matrix.md](paper_claims_matrix.md) | Evidence-backed claim wording |
| [public_vs_commercial_boundary.md](public_vs_commercial_boundary.md) | Public vs proprietary IP boundary |
| [limitations.md](limitations.md) | V0 non-goals |

# SilicaFold V0 Use Cases

## Introduction

SilicaFold V0 provides two silicon primitives for offline agent systems:

- **TensorTile** — a folded 4-lane INT4 dot-product for compact context scoring
- **PolicyGate** — a deterministic tool-call authorization gate returning allow, block, or require-human decisions

These are building blocks, not a complete agent stack. The host system runs the SLM, normalizes model output into structured packets, and executes or blocks actions based on PolicyGate results. This document describes five concrete scenarios showing how the primitives support real offline-agent safety patterns.

For the decision tree and signal definitions, see [architecture.md](architecture.md). For threat analysis, see [policygate_threat_model.md](policygate_threat_model.md).

## Use Case 1: Offline Disaster-Response Assistant

**Scenario:** A field responder carries a device with no connectivity. A local SLM assists with triage and may propose safety-critical actions such as sending an emergency beacon.

**Agent action:** Send emergency beacon (`tool_id=0x1`, safety-critical)

**PolicyGate inputs:**

| Field | Value |
|-------|-------|
| `tool_id` | 0x1 |
| `risk_class` | EMERGENCY (3) or HIGH (2) |
| `policy_ok` | 1 |
| `context_valid` | 1 |
| `emergency_mode` | 1 |
| `offline_mode` | 1 |

**Decision:** Priority 5 — `ALLOW` + `EMERGENCY_PATH` + `LOG_REQUIRED`

**Why it matters:** The responder gets immediate action without cloud connectivity. The emergency path is scoped to safety-critical tools (IDs 0x1–0x3), and every emergency evaluation is logged via `audit_counter`.

## Use Case 2: Field Drone Tool Call

**Scenario:** An autonomous drone runs a local SLM for navigation and task planning. The model proposes motor actuation to reposition the drone.

**Agent action:** Actuate motor (`tool_id=0x2`, safety-critical, high physical risk)

**PolicyGate inputs:**

| Field | Value |
|-------|-------|
| `tool_id` | 0x2 |
| `risk_class` | HIGH (2) |
| `policy_ok` | 1 |
| `context_valid` | 1 |
| `human_approved` | 0 |

**Decision:** Priority 3 — `REQUIRE_HUMAN` + `LOG_REQUIRED`

**Why it matters:** High-risk physical actuation is gated on human confirmation. The drone runtime must obtain operator approval before the motor command executes, even if the SLM confidently proposes the action.

## Use Case 3: Local Enterprise AI Assistant

**Scenario:** An on-premises AI assistant processes documents inside a corporate network. The model proposes exporting a file containing sensitive data.

**Agent action:** Export sensitive file (`tool_id=0x5`, medium risk)

**PolicyGate inputs:**

| Field | Value |
|-------|-------|
| `tool_id` | 0x5 |
| `risk_class` | MEDIUM (1) |
| `policy_ok` | 1 |
| `context_valid` | 1 |
| `human_approved` | 0 |
| `offline_mode` | 1 |

**Decision:** Priority 6 (default allow) — `ALLOW` + `LOG_REQUIRED`

**Why it matters:** The action proceeds because policy and context checks pass and risk is not HIGH. However, `offline_mode=1` combined with `risk_class >= MEDIUM` triggers mandatory logging. Every offline medium-risk export is recorded in the audit trail.

## Use Case 4: Battery-Constrained Edge Device

**Scenario:** An IoT sensor hub on a remote site has critically low battery. The local agent proposes running a nonessential analytics report.

**Agent action:** Run analytics report (`tool_id=0xA`, nonessential)

**PolicyGate inputs:**

| Field | Value |
|-------|-------|
| `tool_id` | 0xA (>= 0x8, nonessential) |
| `risk_class` | LOW (0) |
| `policy_ok` | 1 |
| `context_valid` | 1 |
| `battery_low` | 1 |

**Decision:** Priority 4 — `BLOCK` + `LOG_REQUIRED`

**Why it matters:** Power-aware policy preserves remaining battery for safety-critical operations. Nonessential tools (IDs 0x8–0xF) are blocked when `battery_low=1`, regardless of risk class.

## Use Case 5: TensorTile Context Scoring

**Scenario:** Before evaluating a tool call, the runtime wants to check whether the current conversation context is close to a known-good reference context. TensorTile computes a signed INT4 dot product as a lightweight similarity score.

**Flow:**

1. Load 8 INT4 query nibbles (`CMD_LOAD_Q_NIBBLE` x8) representing the current context
2. Load 8 INT4 key nibbles (`CMD_LOAD_K_NIBBLE` x8) representing the reference context
3. Run folded QK dot product (`CMD_RUN_FOLDED_QK`) — completes in 2 cycles
4. Read result (`CMD_READ_RESULT_LOW` / `CMD_READ_RESULT_HIGH`)
5. Runtime sets `context_valid` based on the score threshold
6. Switch to PolicyGate (`BLOCK_SELECT=1`) and evaluate the pending tool call

**Combined example (mirrors `test_combined_flow`):**

1. TensorTile computes a context score with `BLOCK_SELECT=0`
2. Runtime sets `context_valid=1` based on the score
3. Runtime loads a high-risk tool call into PolicyGate with `BLOCK_SELECT=1`
4. PolicyGate returns `REQUIRE_HUMAN` because `risk_class=HIGH` and `human_approved=0`

**Why it matters:** This demonstrates compute/authority separation on a single die. TensorTile handles the math primitive; PolicyGate handles the authorization decision. The SLM still performs reasoning — the chip assists with scoring and enforcement.

## Mapping Summary

| Use Case | Primary Block | Priority Hit | Decision | Key Outputs |
|----------|---------------|--------------|----------|-------------|
| Disaster response | PolicyGate | 5 (Emergency) | ALLOW | `allow`, `emergency_path`, `log_required` |
| Field drone | PolicyGate | 3 (High risk) | REQUIRE_HUMAN | `require_human`, `log_required` |
| Enterprise export | PolicyGate | 6 (Default) | ALLOW + log | `allow`, `log_required` |
| Battery-constrained IoT | PolicyGate | 4 (Battery) | BLOCK | `block`, `log_required` |
| Context scoring | TensorTile + PolicyGate | 3 (after scoring) | REQUIRE_HUMAN | TensorTile `done`; PolicyGate `require_human` |

## Tool Classification Reference

PolicyGate V0 classifies tools by ID:

| Tool ID Range | Classification | Examples in Use Cases |
|---------------|----------------|----------------------|
| 0x1 – 0x3 | Safety-critical | Emergency beacon (0x1), motor actuation (0x2) |
| 0x4 – 0x7 | Standard | File export (0x5) |
| 0x8 – 0xF | Nonessential | Analytics report (0xA) |

Safety-critical tools can use the emergency override path (Priority 5). Nonessential tools are blocked when battery is low (Priority 4).

## Related Documents

| Document | Purpose |
|----------|---------|
| [architecture.md](architecture.md) | Decision tree and data flow |
| [offlyn_verify_core_integration.md](offlyn_verify_core_integration.md) | Verify Core layered architecture |
| [policygate_threat_model.md](policygate_threat_model.md) | Threat landscape and defenses |
| [limitations.md](limitations.md) | What V0 does not implement |
| [bringup_plan.md](bringup_plan.md) | Post-silicon validation plan |

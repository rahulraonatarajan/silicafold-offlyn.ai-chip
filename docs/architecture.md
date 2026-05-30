# SilicaFold V0 - Architecture

## System Overview

SilicaFold V0 separates computation from authority:
- **TensorTile** performs compact low-bit tensor/context math
- **PolicyGate** authorizes whether structured model-generated tool calls may execute
- The SLM/runtime performs reasoning and converts model output into structured packets
- **The chip does not understand natural language**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Offline SLM Runtime (Host)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ SLM Inference│  │ Context Mgmt │  │ Tool Call Generator  │   │
│  │  (Reasoning) │  │ (KV Cache)   │  │ (Structured Packets) │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │
│         │                 │                     │               │
└─────────┼─────────────────┼─────────────────────┼───────────────┘
          │                 │                     │
          ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SilicaFold V0 (Chip)                        │
│  ┌─────────────────────┐      ┌─────────────────────────────┐   │
│  │     TensorTile      │      │        PolicyGate           │   │
│  │  ─────────────────  │      │  ─────────────────────────  │   │
│  │  INT4 Q/K Registers │      │  Tool ID + Risk Class       │   │
│  │  4-Lane Folded MAC  │      │  Context/Policy Flags       │   │
│  │  16-bit Accumulator │      │  Decision Logic             │   │
│  │  Scale/Shift        │      │  Audit Counter              │   │
│  └─────────────────────┘      └─────────────────────────────┘   │
│              │                             │                    │
│              ▼                             ▼                    │
│       Context Score               Allow/Block/RequireHuman      │
└─────────────────────────────────────────────────────────────────┘
```

## TensorTile Data Flow

```
                        LOAD_Q_NIBBLE (x8)
                              │
                              ▼
┌─────────────────────────────────────────────────────┐
│  Q Registers: [Q0][Q1][Q2][Q3][Q4][Q5][Q6][Q7]     │
│               (8 x INT4, signed two's complement)   │
└─────────────────────────────────────────────────────┘

                        LOAD_K_NIBBLE (x8)
                              │
                              ▼
┌─────────────────────────────────────────────────────┐
│  K Registers: [K0][K1][K2][K3][K4][K5][K6][K7]     │
│               (8 x INT4, signed two's complement)   │
└─────────────────────────────────────────────────────┘

                        RUN_FOLDED_QK
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│      Cycle 1            │     │      Cycle 2            │
│  Q0*K0 + Q1*K1 +        │     │  Q4*K4 + Q5*K5 +        │
│  Q2*K2 + Q3*K3          │     │  Q6*K6 + Q7*K7          │
│      (4-lane MAC)       │     │      (4-lane MAC)       │
└───────────┬─────────────┘     └───────────┬─────────────┘
            │                               │
            └───────────┬───────────────────┘
                        ▼
              ┌─────────────────┐
              │   Accumulator   │
              │   (16-bit)      │
              └────────┬────────┘
                       │
                       ▼ (scale_shift)
              ┌─────────────────┐
              │     Result      │
              │  [7:4] | [3:0]  │
              └─────────────────┘
```

## PolicyGate Decision Flow

```
                    LOAD_TOOL_ID
                    LOAD_RISK_CLASS
                    LOAD_FLAGS
                    LOAD_POWER_EMERG
                          │
                          ▼
                    ┌───────────┐
                    │  EVALUATE │
                    └─────┬─────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Priority │    │ Priority │    │ Priority │
    │ Checks   │    │ Checks   │    │ Checks   │
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
         ▼               ▼               ▼

Priority 1: !policy_ok
         └──► BLOCK + POLICY_ERROR + LOG_REQUIRED

Priority 2: !context_valid && risk >= MEDIUM
         └──► BLOCK + LOG_REQUIRED

Priority 3: risk == HIGH && !human_approved
         └──► REQUIRE_HUMAN + LOG_REQUIRED

Priority 4: battery_low && tool_is_nonessential
         └──► BLOCK + LOG_REQUIRED

Priority 5: emergency_mode && tool_is_safety_critical
         └──► ALLOW + EMERGENCY_PATH + LOG_REQUIRED

Priority 6: (default)
         └──► ALLOW
              (+ LOG_REQUIRED if offline && risk >= MEDIUM)
```

## Host Runtime Integration

The chip requires a trusted host runtime to:

1. **Run the SLM** - Perform inference and generate text/reasoning
2. **Manage context** - Track conversation state, KV cache
3. **Convert to packets** - Transform model output to structured tool calls
4. **Interface with chip** - Send commands, read results

```
┌─────────────────────────────────────────────────────────────────┐
│                        Host Runtime                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   User Query ──► SLM Inference ──► Model Output                 │
│                       │                 │                        │
│                       ▼                 ▼                        │
│              Context Update    Tool Call Detected?               │
│                   │                     │                        │
│                   ▼                 YES │                        │
│            ┌─────────────┐              ▼                        │
│            │ TensorTile  │    ┌─────────────────┐               │
│            │ (optional   │    │ Parse Tool Call │               │
│            │  context    │    │ - tool_id       │               │
│            │  scoring)   │    │ - risk_class    │               │
│            └─────────────┘    │ - parameters    │               │
│                               └────────┬────────┘               │
│                                        │                        │
│                                        ▼                        │
│                               ┌─────────────────┐               │
│                               │   PolicyGate    │               │
│                               │   Evaluation    │               │
│                               └────────┬────────┘               │
│                                        │                        │
│                    ┌───────────────────┼───────────────────┐    │
│                    ▼                   ▼                   ▼    │
│               ┌────────┐         ┌──────────┐        ┌───────┐  │
│               │ ALLOW  │         │  BLOCK   │        │REQUIRE│  │
│               └────┬───┘         └────┬─────┘        │ HUMAN │  │
│                    │                  │              └───┬───┘  │
│                    ▼                  ▼                  ▼      │
│              Execute Tool      Reject Tool      Await Approval  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Block Selection

The top module multiplexes between TensorTile and PolicyGate based on `BLOCK_SELECT` (uio_in[2]):

```
                    ui_in[7:0]
                         │
                    ┌────┴────┐
                    │ Command │
                    │ Decoder │
                    └────┬────┘
                         │
         BLOCK_SELECT────┼────────────────────┐
         (uio_in[2])     │                    │
                    ┌────┴────┐          ┌────┴────┐
                    │    0    │          │    1    │
                    └────┬────┘          └────┬────┘
                         │                    │
                         ▼                    ▼
                ┌─────────────────┐  ┌─────────────────┐
                │   TensorTile   │  │   PolicyGate    │
                └────────┬────────┘  └────────┬────────┘
                         │                    │
                    ┌────┴────┐          ┌────┴────┐
                    │   MUX   │◄─────────│   MUX   │
                    └────┬────┘          └────┬────┘
                         │                    │
                         └────────┬───────────┘
                                  │
                             ┌────┴────┐
                             │ uo_out  │
                             │ uio_out │
                             └─────────┘
```

## Important Notes

1. **The chip does not understand natural language.** The trusted runtime converts SLM outputs into structured tool-call packets. PolicyGate evaluates those structured fields.

2. **This is a V0 proof-of-silicon.** It demonstrates the architectural concept but does not include production-grade security, optimized performance, or commercial IP.

3. **TensorTile computes; the SLM reasons.** Do not confuse the tensor primitive with AI inference. TensorTile is a math accelerator for context operations.

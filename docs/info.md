# SilicaFold V0 - Tiny Tapeout Project Information

## Overview

SilicaFold V0 is a proof-of-silicon artifact for Tiny Tapeout that combines two primitives for offline SLM (Small Language Model) agent infrastructure:

1. **TensorTile**: A folded 4-lane INT4 QK dot-product primitive
2. **PolicyGate**: A deterministic tool-call authorization gate

## How It Works

### TensorTile

TensorTile computes an 8-element INT4 dot product using a folded 4-lane MAC (Multiply-Accumulate) datapath. The computation completes in 2 cycles:

- **Cycle 1**: Compute Q[0:3] * K[0:3]
- **Cycle 2**: Compute Q[4:7] * K[4:7] and accumulate

The result is a signed 16-bit value that can be scaled via arithmetic right shift.

### PolicyGate

PolicyGate evaluates structured tool-call requests and returns one of:
- **ALLOW**: Tool may execute
- **BLOCK**: Tool must not execute
- **REQUIRE_HUMAN**: Human approval needed before execution

The decision is based on:
- Policy validity
- Context validity
- Risk classification (low/medium/high/emergency)
- Human approval status
- Battery state (for power conservation)
- Emergency mode (for safety-critical overrides)

## Pin Configuration

### Inputs (ui_in)
| Pin | Name | Description |
|-----|------|-------------|
| ui_in[3:0] | CMD | 4-bit command nibble |
| ui_in[7:4] | DIN | 4-bit data nibble |

### Outputs (uo_out)
| Pin | TensorTile | PolicyGate |
|-----|------------|------------|
| uo_out[0] | busy | allow |
| uo_out[1] | done | block |
| uo_out[2] | overflow | require_human |
| uo_out[3] | context_valid | log_required |
| uo_out[7:4] | result nibble | decision nibble |

### Bidirectional (uio)
| Pin | Direction | Name |
|-----|-----------|------|
| uio[0] | Input | WR_STB |
| uio[1] | Input | RD_STB |
| uio[2] | Input | BLOCK_SELECT |
| uio[3] | Input | DEBUG_MODE |
| uio[7:4] | Output | Extended status |

## Command Reference

### TensorTile Commands
| CMD | Name | Description |
|-----|------|-------------|
| 0x0 | NOP | No operation |
| 0x1 | LOAD_Q_NIBBLE | Load INT4 Q value |
| 0x2 | LOAD_K_NIBBLE | Load INT4 K value |
| 0x3 | LOAD_CONTEXT | Load context slot ID |
| 0x4 | LOAD_SCALE | Set scale shift amount |
| 0x5 | RUN_FOLDED_QK | Execute dot product |
| 0x6 | READ_RESULT_LOW | Read result[3:0] |
| 0x7 | READ_RESULT_HIGH | Read result[7:4] |
| 0x8 | READ_CYCLE | Read cycle count |
| 0x9 | READ_STATUS | Read status bits |
| 0xA | RESET_STATE | Soft reset |

### PolicyGate Commands
| CMD | Name | Description |
|-----|------|-------------|
| 0x0 | NOP | No operation |
| 0x1 | LOAD_TOOL_ID | Set tool identifier |
| 0x2 | LOAD_RISK_CLASS | Set risk level |
| 0x3 | LOAD_FLAGS | Set context/policy flags |
| 0x4 | LOAD_POWER_EMERG | Set power/emergency flags |
| 0x5 | EVALUATE | Run decision logic |
| 0x6 | READ_DECISION | Read decision output |
| 0x7 | READ_AUDIT | Read audit counter |
| 0x8 | RESET_STATE | Soft reset |

## External Hardware

No external hardware is required for basic operation. The design expects:
- 25 MHz clock
- Active-low reset

## Testing

Run the cocotb testbench:
```bash
cd test
make
```

## Resources

- [Tiny Tapeout](https://tinytapeout.com)
- [Project Repository](https://github.com/rahulraonatarajan/silicafold-offlyn.ai-chip)

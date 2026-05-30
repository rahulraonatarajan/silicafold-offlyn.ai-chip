# SilicaFold V0 - Bring-Up Plan

## Overview

This document describes the plan for testing SilicaFold V0 after receiving fabricated silicon from Tiny Tapeout.

## Hardware Requirements

### From Tiny Tapeout
- Fabricated chip on Tiny Tapeout PCB/DevKit
- USB connection for programming/control

### Additional Equipment
- USB cable (type depends on DevKit version)
- Computer with Python 3.x
- Logic analyzer (optional, for debugging)
- Oscilloscope (optional, for signal integrity)

## Software Requirements

- Python 3.8+
- pyserial or equivalent for USB communication
- Test scripts (to be developed based on DevKit interface)

## Bring-Up Phases

### Phase 1: Power-On Verification

**Objective**: Verify chip powers up correctly

1. Connect DevKit to USB
2. Check power LED indicators
3. Verify no excessive current draw
4. Confirm USB enumeration

**Pass Criteria**:
- Stable power consumption
- USB device recognized
- No smoke or heat issues

### Phase 2: Reset Test

**Objective**: Verify reset behavior

1. Apply reset (rst_n = 0)
2. Read all outputs
3. Verify all outputs are zero/default
4. Release reset (rst_n = 1)
5. Verify outputs remain stable

**Pass Criteria**:
- All status bits = 0 after reset
- uo_out = 0x00
- uio_out[7:4] = 0x0

### Phase 3: TensorTile Basic Test

**Objective**: Verify TensorTile responds to commands

Test sequence:
```
1. Set BLOCK_SELECT = 0
2. Send CMD_RESET_STATE
3. Load Q values: all 1s (8 iterations of CMD_LOAD_Q_NIBBLE with din=1)
4. Send CMD_LOAD_CONTEXT
5. Load K values: all 1s (8 iterations of CMD_LOAD_K_NIBBLE with din=1)
6. Send CMD_RUN_FOLDED_QK
7. Wait for done flag
8. Read result (expect 8)
```

**Pass Criteria**:
- busy flag asserts during computation
- done flag asserts after computation
- Result = 8 (1*1*8 = 8)
- cycle_count = 2

### Phase 4: TensorTile Signed Test

**Objective**: Verify signed INT4 arithmetic

Test sequence:
```
1. Load Q values: all -1 (0xF)
2. Load K values: all -1 (0xF)
3. Run computation
4. Expect result = 8 ((-1)*(-1)*8 = 8)
```

**Pass Criteria**:
- Correct handling of negative values
- Result = 8

### Phase 5: PolicyGate Basic Test

**Objective**: Verify PolicyGate responds to commands

Test sequence:
```
1. Set BLOCK_SELECT = 1
2. Send CMD_RESET_STATE
3. Load tool_id = 5
4. Load risk_class = 0 (LOW)
5. Load flags: context_valid=1, policy_ok=1
6. Send CMD_EVALUATE
7. Read decision
```

**Pass Criteria**:
- evaluated flag asserts
- allow = 1
- block = 0

### Phase 6: PolicyGate Policy Violation Test

**Objective**: Verify policy enforcement

Test sequence:
```
1. Load flags: policy_ok = 0
2. Evaluate
3. Expect BLOCK + POLICY_ERROR
```

**Pass Criteria**:
- block = 1
- allow = 0
- policy_error = 1
- log_required = 1

### Phase 7: Combined Flow Test

**Objective**: Verify TensorTile and PolicyGate work together

Test sequence:
```
1. Compute TensorTile QK score
2. Switch to PolicyGate
3. Evaluate high-risk tool
4. Verify REQUIRE_HUMAN response
```

**Pass Criteria**:
- Both blocks functional
- Block switching works correctly
- End-to-end flow completes

### Phase 8: Stress Testing

**Objective**: Verify reliability under sustained operation

Tests:
- Repeated computations (1000+ iterations)
- Rapid block switching
- Edge case inputs (max/min values)
- Long-duration operation (hours)

**Pass Criteria**:
- No hangs or crashes
- Consistent results
- No bit errors

## Debugging Guide

### Symptom: No response to commands

Possible causes:
- Clock not running
- Reset stuck low
- USB communication issue
- Chip not powered

Debug steps:
1. Check clock with oscilloscope
2. Verify reset signal
3. Test USB loopback
4. Check power rails

### Symptom: Incorrect results

Possible causes:
- Command timing issue
- WR_STB not properly asserted
- BLOCK_SELECT incorrect
- Silicon defect

Debug steps:
1. Slow down command rate
2. Verify strobe timing
3. Check block select state
4. Compare with simulation

### Symptom: Stuck busy flag

Possible causes:
- State machine stuck
- Clock glitch
- Silicon defect

Debug steps:
1. Apply reset
2. Check clock stability
3. Try different command sequences

## Test Automation

Develop Python scripts for automated testing:

```python
# Example test script structure
class SilicaFoldTester:
    def __init__(self, port):
        self.serial = serial.Serial(port, 115200)
    
    def reset(self):
        # Send reset sequence
        pass
    
    def write_cmd(self, block_sel, cmd, data):
        # Send command to chip
        pass
    
    def read_output(self):
        # Read chip outputs
        pass
    
    def test_tensortile_basic(self):
        # Run basic TensorTile test
        pass
    
    def test_policygate_basic(self):
        # Run basic PolicyGate test
        pass
```

## Success Criteria

SilicaFold V0 bring-up is considered successful when:

1. All Phase 1-7 tests pass
2. Phase 8 stress tests show no failures over 1 hour
3. Results match cocotb simulation
4. No unexplained behaviors

## Documentation

After successful bring-up:
1. Record actual test results
2. Document any deviations from expected behavior
3. Note silicon-specific observations
4. Update README with bring-up status
5. Share results with Tiny Tapeout community

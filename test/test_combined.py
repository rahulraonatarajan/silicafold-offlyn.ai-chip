# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 Rahul Rao Natarajan / Offlyn.ai
#
# SilicaFold V0 - Combined Cocotb Testbench
# Tests both TensorTile and PolicyGate functionality

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, Timer

# =============================================================================
# Constants
# =============================================================================

# TensorTile Commands
TT_CMD_NOP              = 0x0
TT_CMD_LOAD_Q_NIBBLE    = 0x1
TT_CMD_LOAD_K_NIBBLE    = 0x2
TT_CMD_LOAD_CONTEXT     = 0x3
TT_CMD_LOAD_SCALE       = 0x4
TT_CMD_RUN_FOLDED_QK    = 0x5
TT_CMD_READ_RESULT_LOW  = 0x6
TT_CMD_READ_RESULT_HIGH = 0x7
TT_CMD_READ_CYCLE       = 0x8
TT_CMD_READ_STATUS      = 0x9
TT_CMD_RESET_STATE      = 0xA

# PolicyGate Commands
PG_CMD_NOP              = 0x0
PG_CMD_LOAD_TOOL_ID     = 0x1
PG_CMD_LOAD_RISK_CLASS  = 0x2
PG_CMD_LOAD_FLAGS       = 0x3
PG_CMD_LOAD_POWER_EMERG = 0x4
PG_CMD_EVALUATE         = 0x5
PG_CMD_READ_DECISION    = 0x6
PG_CMD_READ_AUDIT       = 0x7
PG_CMD_RESET_STATE      = 0x8

# Risk Classes
RISK_LOW       = 0
RISK_MEDIUM    = 1
RISK_HIGH      = 2
RISK_EMERGENCY = 3

# Block Select
BLOCK_TENSORTILE = 0
BLOCK_POLICYGATE = 1


# =============================================================================
# Helper Functions
# =============================================================================

async def reset_dut(dut):
    """Apply reset to the DUT."""
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.ena.value = 1
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)


async def write_cmd(dut, block_sel, cmd, data):
    """Write a command with data to the selected block."""
    # Set block select, command, and data
    uio_val = (block_sel << 2) | 0x01  # WR_STB=1, RD_STB=0
    ui_val = (data << 4) | cmd
    
    dut.uio_in.value = uio_val
    dut.ui_in.value = ui_val
    await RisingEdge(dut.clk)
    
    # Clear strobe
    dut.uio_in.value = block_sel << 2
    await RisingEdge(dut.clk)


async def read_cmd(dut, block_sel, cmd):
    """Read from the selected block with a command."""
    # Set block select, command, RD_STB
    uio_val = (block_sel << 2) | 0x02  # WR_STB=0, RD_STB=1
    ui_val = cmd
    
    dut.uio_in.value = uio_val
    dut.ui_in.value = ui_val
    await RisingEdge(dut.clk)
    
    # Clear strobe and read output
    dut.uio_in.value = block_sel << 2
    await RisingEdge(dut.clk)
    
    return int(dut.uo_out.value)


def int4_to_signed(val):
    """Convert 4-bit unsigned to signed (-8 to 7)."""
    if val & 0x8:
        return val - 16
    return val


def signed_to_int4(val):
    """Convert signed value to 4-bit unsigned representation."""
    if val < 0:
        return val + 16
    return val & 0xF


# =============================================================================
# Test 1: Reset Behavior
# =============================================================================

@cocotb.test()
async def test_reset(dut):
    """Test 1: Verify all outputs cleared after reset."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Check TensorTile outputs (block_sel = 0)
    dut.uio_in.value = BLOCK_TENSORTILE << 2
    await ClockCycles(dut.clk, 1)
    
    uo = int(dut.uo_out.value)
    uio = int(dut.uio_out.value)
    
    # All status bits should be 0
    assert (uo & 0x0F) == 0, f"TensorTile status bits not cleared: {uo & 0x0F}"
    assert (uio >> 4) == 0, f"TensorTile cycle_count not cleared: {uio >> 4}"
    
    # Check PolicyGate outputs (block_sel = 1)
    dut.uio_in.value = BLOCK_POLICYGATE << 2
    await ClockCycles(dut.clk, 1)
    
    uo = int(dut.uo_out.value)
    uio = int(dut.uio_out.value)
    
    assert (uo & 0x0F) == 0, f"PolicyGate status bits not cleared: {uo & 0x0F}"
    
    dut._log.info("Test 1 PASSED: Reset clears all outputs")


# =============================================================================
# Test 2: TensorTile Positive QK Dot Product
# =============================================================================

@cocotb.test()
async def test_tensortile_positive_qk(dut):
    """Test 2: Positive INT4 dot product (all 1s = 8)."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Load Q values: all 1s (0x1 as INT4 = +1)
    for i in range(8):
        await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_Q_NIBBLE, 0x1)
    
    # Load context to reset index
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_CONTEXT, 0x0)
    
    # Load K values: all 1s
    for i in range(8):
        await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_K_NIBBLE, 0x1)
    
    # Run folded QK
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_RUN_FOLDED_QK, 0x0)
    
    # Wait for computation (3 cycles for state machine)
    await ClockCycles(dut.clk, 5)
    
    # Read result low nibble (should be 8 = 0x08, low nibble = 0x8)
    result_low = await read_cmd(dut, BLOCK_TENSORTILE, TT_CMD_READ_RESULT_LOW)
    result_high = await read_cmd(dut, BLOCK_TENSORTILE, TT_CMD_READ_RESULT_HIGH)
    
    result = ((result_high >> 4) << 4) | (result_low >> 4)
    
    dut._log.info(f"Dot product result: {result} (expected 8)")
    assert result == 8, f"Expected dot product of 8, got {result}"
    
    dut._log.info("Test 2 PASSED: Positive QK dot product correct")


# =============================================================================
# Test 3: TensorTile Signed Negative INT4 Values
# =============================================================================

@cocotb.test()
async def test_tensortile_signed_negative(dut):
    """Test 3: Negative INT4 values handled correctly."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Load Q values: -1 (0xF as INT4 two's complement)
    # -1 * -1 = 1, so 8 * 1 = 8
    for i in range(8):
        await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_Q_NIBBLE, 0xF)  # -1
    
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_CONTEXT, 0x0)
    
    # Load K values: -1 (0xF)
    for i in range(8):
        await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_K_NIBBLE, 0xF)  # -1
    
    # Run folded QK
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_RUN_FOLDED_QK, 0x0)
    await ClockCycles(dut.clk, 5)
    
    # Read result
    result_low = await read_cmd(dut, BLOCK_TENSORTILE, TT_CMD_READ_RESULT_LOW)
    result_high = await read_cmd(dut, BLOCK_TENSORTILE, TT_CMD_READ_RESULT_HIGH)
    
    result = ((result_high >> 4) << 4) | (result_low >> 4)
    
    dut._log.info(f"Negative dot product result: {result} (expected 8)")
    assert result == 8, f"Expected (-1)*(-1)*8 = 8, got {result}"
    
    dut._log.info("Test 3 PASSED: Signed negative INT4 values correct")


# =============================================================================
# Test 4: TensorTile Cycle Count
# =============================================================================

@cocotb.test()
async def test_tensortile_cycle_count(dut):
    """Test 4: Verify cycle_count equals 2 after RUN_FOLDED_QK."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Load minimal Q and K (just need to run computation)
    for i in range(8):
        await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_Q_NIBBLE, 0x1)
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_CONTEXT, 0x0)
    for i in range(8):
        await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_K_NIBBLE, 0x1)
    
    # Run folded QK
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_RUN_FOLDED_QK, 0x0)
    await ClockCycles(dut.clk, 5)
    
    # Check cycle count from uio_out[7:4]
    dut.uio_in.value = BLOCK_TENSORTILE << 2
    await ClockCycles(dut.clk, 1)
    
    uio = int(dut.uio_out.value)
    cycle_count = (uio >> 4) & 0xF
    
    dut._log.info(f"Cycle count: {cycle_count} (expected 2)")
    assert cycle_count == 2, f"Expected cycle_count=2, got {cycle_count}"
    
    dut._log.info("Test 4 PASSED: Cycle count equals 2")


# =============================================================================
# Test 5: TensorTile Overflow Flag
# =============================================================================

@cocotb.test()
async def test_tensortile_overflow(dut):
    """Test 5: Verify overflow flag on accumulator saturation."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Load Q values: max positive (0x7 = +7)
    for i in range(8):
        await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_Q_NIBBLE, 0x7)
    
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_CONTEXT, 0x0)
    
    # Load K values: max positive (0x7 = +7)
    # Result = 8 * 7 * 7 = 392, which exceeds signed 8-bit range (-128 to 127)
    for i in range(8):
        await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_K_NIBBLE, 0x7)
    
    # Run folded QK
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_RUN_FOLDED_QK, 0x0)
    await ClockCycles(dut.clk, 5)
    
    # Check overflow bit (uo_out[2] when BLOCK_SELECT=0)
    dut.uio_in.value = BLOCK_TENSORTILE << 2
    await ClockCycles(dut.clk, 1)
    
    uo = int(dut.uo_out.value)
    overflow = (uo >> 2) & 0x1
    
    dut._log.info(f"Overflow flag: {overflow} (expected 1)")
    assert overflow == 1, f"Expected overflow=1 for 392 > 127, got {overflow}"
    
    dut._log.info("Test 5 PASSED: Overflow flag set correctly")


# =============================================================================
# Test 6: PolicyGate Invalid Policy Blocks
# =============================================================================

@cocotb.test()
async def test_policygate_invalid_policy(dut):
    """Test 6: policy_ok=0 results in BLOCK + POLICY_ERROR."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Load tool ID
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_TOOL_ID, 0x5)
    
    # Load flags with policy_ok=0
    # din[0]=context_valid, din[1]=policy_ok, din[2]=human_approved, din[3]=offline
    flags = 0b0001  # context_valid=1, policy_ok=0
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_FLAGS, flags)
    
    # Evaluate
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_EVALUATE, 0x0)
    await ClockCycles(dut.clk, 2)
    
    # Check outputs
    dut.uio_in.value = BLOCK_POLICYGATE << 2
    await ClockCycles(dut.clk, 1)
    
    uo = int(dut.uo_out.value)
    uio = int(dut.uio_out.value)
    
    allow = uo & 0x1
    block = (uo >> 1) & 0x1
    log_required = (uo >> 3) & 0x1
    policy_error = (uio >> 4) & 0x1
    
    dut._log.info(f"allow={allow}, block={block}, policy_error={policy_error}, log_required={log_required}")
    
    assert block == 1, "Expected block=1 when policy_ok=0"
    assert allow == 0, "Expected allow=0 when policy_ok=0"
    assert policy_error == 1, "Expected policy_error=1 when policy_ok=0"
    assert log_required == 1, "Expected log_required=1 when policy_ok=0"
    
    dut._log.info("Test 6 PASSED: Invalid policy blocks correctly")


# =============================================================================
# Test 7: PolicyGate High-Risk Without Human Approval
# =============================================================================

@cocotb.test()
async def test_policygate_high_risk_no_human(dut):
    """Test 7: High-risk without human approval returns REQUIRE_HUMAN."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Load tool ID
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_TOOL_ID, 0x5)
    
    # Load risk class = HIGH (2)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_RISK_CLASS, RISK_HIGH)
    
    # Load flags: context_valid=1, policy_ok=1, human_approved=0
    flags = 0b0011  # context_valid=1, policy_ok=1, human_approved=0, offline=0
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_FLAGS, flags)
    
    # Evaluate
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_EVALUATE, 0x0)
    await ClockCycles(dut.clk, 2)
    
    # Check outputs
    dut.uio_in.value = BLOCK_POLICYGATE << 2
    await ClockCycles(dut.clk, 1)
    
    uo = int(dut.uo_out.value)
    
    allow = uo & 0x1
    block = (uo >> 1) & 0x1
    require_human = (uo >> 2) & 0x1
    log_required = (uo >> 3) & 0x1
    
    dut._log.info(f"allow={allow}, block={block}, require_human={require_human}, log_required={log_required}")
    
    assert require_human == 1, "Expected require_human=1 for high-risk without approval"
    assert allow == 0, "Expected allow=0 when require_human"
    assert block == 0, "Expected block=0 when require_human"
    assert log_required == 1, "Expected log_required=1"
    
    dut._log.info("Test 7 PASSED: High-risk without human requires human approval")


# =============================================================================
# Test 8: PolicyGate High-Risk With Human Approval
# =============================================================================

@cocotb.test()
async def test_policygate_high_risk_with_human(dut):
    """Test 8: High-risk with human approval allows and logs."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Load tool ID
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_TOOL_ID, 0x5)
    
    # Load risk class = HIGH (2)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_RISK_CLASS, RISK_HIGH)
    
    # Load flags: context_valid=1, policy_ok=1, human_approved=1, offline=1
    flags = 0b1111  # All set
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_FLAGS, flags)
    
    # Evaluate
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_EVALUATE, 0x0)
    await ClockCycles(dut.clk, 2)
    
    # Check outputs
    dut.uio_in.value = BLOCK_POLICYGATE << 2
    await ClockCycles(dut.clk, 1)
    
    uo = int(dut.uo_out.value)
    
    allow = uo & 0x1
    block = (uo >> 1) & 0x1
    require_human = (uo >> 2) & 0x1
    log_required = (uo >> 3) & 0x1
    
    dut._log.info(f"allow={allow}, block={block}, require_human={require_human}, log_required={log_required}")
    
    assert allow == 1, "Expected allow=1 with human approval"
    assert block == 0, "Expected block=0"
    assert require_human == 0, "Expected require_human=0 with human approval"
    # Log is required because offline_mode=1 and risk >= medium
    assert log_required == 1, "Expected log_required=1 in offline mode with high risk"
    
    dut._log.info("Test 8 PASSED: High-risk with human approval allows and logs")


# =============================================================================
# Test 9: PolicyGate Emergency Safety-Critical Path
# =============================================================================

@cocotb.test()
async def test_policygate_emergency_safety(dut):
    """Test 9: Emergency mode with safety-critical tool allows with emergency_path."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Load safety-critical tool ID (0x1, 0x2, or 0x3)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_TOOL_ID, 0x1)
    
    # Load risk class = LOW (to avoid other blocking conditions)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_RISK_CLASS, RISK_LOW)
    
    # Load flags: context_valid=1, policy_ok=1
    flags = 0b0011
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_FLAGS, flags)
    
    # Load power/emergency: emergency_mode=1
    power_flags = 0b0010  # battery_low=0, emergency_mode=1
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_POWER_EMERG, power_flags)
    
    # Evaluate
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_EVALUATE, 0x0)
    await ClockCycles(dut.clk, 2)
    
    # Check outputs
    dut.uio_in.value = BLOCK_POLICYGATE << 2
    await ClockCycles(dut.clk, 1)
    
    uo = int(dut.uo_out.value)
    uio = int(dut.uio_out.value)
    
    allow = uo & 0x1
    log_required = (uo >> 3) & 0x1
    emergency_path = (uio >> 6) & 0x1
    
    dut._log.info(f"allow={allow}, log_required={log_required}, emergency_path={emergency_path}")
    
    assert allow == 1, "Expected allow=1 for emergency safety-critical"
    assert log_required == 1, "Expected log_required=1 for emergency path"
    assert emergency_path == 1, "Expected emergency_path=1"
    
    dut._log.info("Test 9 PASSED: Emergency safety-critical path works correctly")


# =============================================================================
# Test 10: Combined Flow
# =============================================================================

@cocotb.test()
async def test_combined_flow(dut):
    """Test 10: TensorTile computes, then PolicyGate evaluates high-risk tool."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # --- TensorTile Phase: Compute a QK score ---
    dut._log.info("Phase 1: TensorTile computing QK score...")
    
    # Load Q values: simple pattern [1, 2, 1, 2, 1, 2, 1, 2]
    for i in range(8):
        val = 1 if i % 2 == 0 else 2
        await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_Q_NIBBLE, val)
    
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_CONTEXT, 0x1)
    
    # Load K values: same pattern
    for i in range(8):
        val = 1 if i % 2 == 0 else 2
        await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_K_NIBBLE, val)
    
    # Run folded QK
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_RUN_FOLDED_QK, 0x0)
    await ClockCycles(dut.clk, 5)
    
    # Verify done
    dut.uio_in.value = BLOCK_TENSORTILE << 2
    await ClockCycles(dut.clk, 1)
    uo = int(dut.uo_out.value)
    done = (uo >> 1) & 0x1
    context_valid = (uo >> 3) & 0x1
    
    assert done == 1, "TensorTile should be done"
    assert context_valid == 1, "Context should be valid"
    
    dut._log.info(f"TensorTile done={done}, context_valid={context_valid}")
    
    # --- PolicyGate Phase: Evaluate high-risk tool call ---
    dut._log.info("Phase 2: PolicyGate evaluating high-risk tool call...")
    
    # Load tool ID (some tool, not safety-critical, not nonessential)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_TOOL_ID, 0x5)
    
    # Load risk class = HIGH
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_RISK_CLASS, RISK_HIGH)
    
    # Load flags: context_valid=1, policy_ok=1, human_approved=0 (no approval)
    flags = 0b0011
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_FLAGS, flags)
    
    # Evaluate
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_EVALUATE, 0x0)
    await ClockCycles(dut.clk, 2)
    
    # Check PolicyGate decision
    dut.uio_in.value = BLOCK_POLICYGATE << 2
    await ClockCycles(dut.clk, 1)
    
    uo = int(dut.uo_out.value)
    uio = int(dut.uio_out.value)
    
    allow = uo & 0x1
    block = (uo >> 1) & 0x1
    require_human = (uo >> 2) & 0x1
    log_required = (uo >> 3) & 0x1
    evaluated = (uio >> 7) & 0x1
    
    dut._log.info(f"PolicyGate: allow={allow}, block={block}, require_human={require_human}, log_required={log_required}, evaluated={evaluated}")
    
    assert evaluated == 1, "PolicyGate should have evaluated"
    assert require_human == 1, "Expected REQUIRE_HUMAN for high-risk without approval"
    assert log_required == 1, "Expected LOG_REQUIRED"
    assert allow == 0, "Should not allow without human approval"
    
    dut._log.info("Test 10 PASSED: Combined TensorTile + PolicyGate flow works")

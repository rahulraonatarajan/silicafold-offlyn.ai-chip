# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 Rahul Rao Natarajan / Offlyn.ai
#
# SilicaFold V0 - Combined Cocotb Testbench
# Tests both TensorTile and PolicyGate functionality
#
# IMPORTANT: The chip does NOT understand natural language.
# The host runtime creates structured packets; the chip computes and authorizes.

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

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
# Golden Model: INT4 Signed Dot Product
# =============================================================================

def int4_to_signed(val):
    """Convert 4-bit unsigned to signed (-8 to +7)."""
    val = val & 0xF
    if val & 0x8:
        return val - 16
    return val


def signed_to_int4(val):
    """Convert signed value to 4-bit unsigned representation."""
    if val < 0:
        return (val + 16) & 0xF
    return val & 0xF


def golden_int4_dot_product(q_values, k_values):
    """
    Golden model for INT4 dot product.
    
    Args:
        q_values: List of 8 INT4 values (0-15, interpreted as signed -8 to +7)
        k_values: List of 8 INT4 values (0-15, interpreted as signed -8 to +7)
    
    Returns:
        Signed 16-bit result of sum(Q[i] * K[i]) for i in 0..7
    """
    assert len(q_values) == 8 and len(k_values) == 8
    
    result = 0
    for i in range(8):
        q_signed = int4_to_signed(q_values[i])
        k_signed = int4_to_signed(k_values[i])
        result += q_signed * k_signed
    
    return result


def check_overflow(value):
    """Check if value exceeds signed 8-bit range (toy overflow detection)."""
    return value > 127 or value < -128


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
    uio_val = (block_sel << 2) | 0x02  # WR_STB=0, RD_STB=1
    ui_val = cmd
    
    dut.uio_in.value = uio_val
    dut.ui_in.value = ui_val
    await RisingEdge(dut.clk)
    
    # Clear strobe and read output
    dut.uio_in.value = block_sel << 2
    await RisingEdge(dut.clk)
    
    return int(dut.uo_out.value)


async def load_tensortile_vectors(dut, q_values, k_values):
    """Load Q and K vectors into TensorTile."""
    # Load Q values
    for val in q_values:
        await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_Q_NIBBLE, val & 0xF)
    
    # Load context to reset indices
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_CONTEXT, 0x1)
    
    # Load K values
    for val in k_values:
        await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_K_NIBBLE, val & 0xF)


async def run_tensortile_and_read(dut, scale_shift=0):
    """Run TensorTile computation and read result."""
    # Set scale
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_LOAD_SCALE, scale_shift)
    
    # Run folded QK
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_RUN_FOLDED_QK, 0x0)
    
    # Wait for computation (3 cycles for state machine)
    await ClockCycles(dut.clk, 5)
    
    # Read result
    result_low = await read_cmd(dut, BLOCK_TENSORTILE, TT_CMD_READ_RESULT_LOW)
    result_high = await read_cmd(dut, BLOCK_TENSORTILE, TT_CMD_READ_RESULT_HIGH)
    
    # Extract nibbles from uo_out[7:4]
    low_nibble = (result_low >> 4) & 0xF
    high_nibble = (result_high >> 4) & 0xF
    
    result = (high_nibble << 4) | low_nibble
    
    # Sign extend if negative (bit 7 set)
    if result & 0x80:
        result = result - 256
    
    return result


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
    
    assert (uo & 0x0F) == 0, f"TensorTile status bits not cleared: {uo & 0x0F:#x}"
    assert (uio >> 4) == 0, f"TensorTile cycle_count not cleared: {uio >> 4}"
    
    # Check PolicyGate outputs (block_sel = 1)
    dut.uio_in.value = BLOCK_POLICYGATE << 2
    await ClockCycles(dut.clk, 1)
    
    uo = int(dut.uo_out.value)
    
    assert (uo & 0x0F) == 0, f"PolicyGate status bits not cleared: {uo & 0x0F:#x}"
    
    dut._log.info("Test 1 PASSED: Reset clears all outputs")


# =============================================================================
# Test 2: TensorTile Positive QK Dot Product
# =============================================================================

@cocotb.test()
async def test_tensortile_positive_qk(dut):
    """Test 2: Positive INT4 dot product (all 1s)."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Q = [1,1,1,1,1,1,1,1], K = [1,1,1,1,1,1,1,1]
    q_values = [1] * 8
    k_values = [1] * 8
    
    expected = golden_int4_dot_product(q_values, k_values)
    
    await load_tensortile_vectors(dut, q_values, k_values)
    result = await run_tensortile_and_read(dut)
    
    dut._log.info(f"Dot product result: {result} (expected {expected})")
    assert result == expected, f"Expected {expected}, got {result}"
    
    dut._log.info("Test 2 PASSED: Positive QK dot product correct")


# =============================================================================
# Test 3: TensorTile Signed Negative INT4 Values
# =============================================================================

@cocotb.test()
async def test_tensortile_signed_negative(dut):
    """Test 3: Negative INT4 values handled correctly (-1 * -1 * 8 = 8)."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Q = [-1,-1,-1,-1,-1,-1,-1,-1] (0xF), K = [-1,-1,-1,-1,-1,-1,-1,-1]
    q_values = [0xF] * 8  # -1 in INT4
    k_values = [0xF] * 8  # -1 in INT4
    
    expected = golden_int4_dot_product(q_values, k_values)
    
    await load_tensortile_vectors(dut, q_values, k_values)
    result = await run_tensortile_and_read(dut)
    
    dut._log.info(f"Negative dot product result: {result} (expected {expected})")
    assert result == expected, f"Expected {expected}, got {result}"
    
    dut._log.info("Test 3 PASSED: Signed negative INT4 values correct")


# =============================================================================
# Test 4: TensorTile Mixed Signed Vector Test
# =============================================================================

@cocotb.test()
async def test_tensortile_mixed_signed(dut):
    """Test 4: Mixed positive and negative INT4 values."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Q = [2, -2, 3, -3, 4, -4, 5, -5]
    # K = [1, 1, 1, 1, 1, 1, 1, 1]
    # Expected: 2-2+3-3+4-4+5-5 = 0
    q_values = [2, 0xE, 3, 0xD, 4, 0xC, 5, 0xB]  # -2=0xE, -3=0xD, -4=0xC, -5=0xB
    k_values = [1] * 8
    
    expected = golden_int4_dot_product(q_values, k_values)
    
    await load_tensortile_vectors(dut, q_values, k_values)
    result = await run_tensortile_and_read(dut)
    
    dut._log.info(f"Mixed signed result: {result} (expected {expected})")
    assert result == expected, f"Expected {expected}, got {result}"
    
    dut._log.info("Test 4 PASSED: Mixed signed vector test correct")


# =============================================================================
# Test 5: TensorTile Cycle Count Equals 2
# =============================================================================

@cocotb.test()
async def test_tensortile_cycle_count(dut):
    """Test 5: Verify cycle_count equals 2 after RUN_FOLDED_QK."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    q_values = [1] * 8
    k_values = [1] * 8
    
    await load_tensortile_vectors(dut, q_values, k_values)
    
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_RUN_FOLDED_QK, 0x0)
    await ClockCycles(dut.clk, 5)
    
    # Check cycle count from uio_out[7:4]
    dut.uio_in.value = BLOCK_TENSORTILE << 2
    await ClockCycles(dut.clk, 1)
    
    uio = int(dut.uio_out.value)
    cycle_count = (uio >> 4) & 0xF
    
    dut._log.info(f"Cycle count: {cycle_count} (expected 2)")
    assert cycle_count == 2, f"Expected cycle_count=2, got {cycle_count}"
    
    dut._log.info("Test 5 PASSED: Cycle count equals 2")


# =============================================================================
# Test 6: TensorTile Overflow Flag
# =============================================================================

@cocotb.test()
async def test_tensortile_overflow(dut):
    """Test 6: Verify overflow flag on accumulator saturation."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Q = [7,7,7,7,7,7,7,7], K = [7,7,7,7,7,7,7,7]
    # Result = 8 * 49 = 392, which exceeds signed 8-bit range
    q_values = [7] * 8
    k_values = [7] * 8
    
    expected = golden_int4_dot_product(q_values, k_values)
    should_overflow = check_overflow(expected)
    
    await load_tensortile_vectors(dut, q_values, k_values)
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_RUN_FOLDED_QK, 0x0)
    await ClockCycles(dut.clk, 5)
    
    # Check overflow bit (uo_out[2] when BLOCK_SELECT=0)
    dut.uio_in.value = BLOCK_TENSORTILE << 2
    await ClockCycles(dut.clk, 1)
    
    uo = int(dut.uo_out.value)
    overflow = (uo >> 2) & 0x1
    
    dut._log.info(f"Result={expected}, Overflow flag: {overflow} (expected {int(should_overflow)})")
    assert overflow == int(should_overflow), f"Expected overflow={int(should_overflow)}, got {overflow}"
    
    dut._log.info("Test 6 PASSED: Overflow flag set correctly")


# =============================================================================
# Test 7: TensorTile Scale Shift Behavior
# =============================================================================

@cocotb.test()
async def test_tensortile_scale_shift(dut):
    """Test 7: Verify scale shift (arithmetic right shift)."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Q = [4,4,4,4,4,4,4,4], K = [2,2,2,2,2,2,2,2]
    # Result without shift = 8 * 8 = 64
    # With shift=2: 64 >> 2 = 16
    q_values = [4] * 8
    k_values = [2] * 8
    
    await load_tensortile_vectors(dut, q_values, k_values)
    result = await run_tensortile_and_read(dut, scale_shift=2)
    
    expected_raw = golden_int4_dot_product(q_values, k_values)
    expected_shifted = expected_raw >> 2
    
    dut._log.info(f"Scale shift result: {result} (raw={expected_raw}, expected shifted={expected_shifted})")
    assert result == expected_shifted, f"Expected {expected_shifted}, got {result}"
    
    dut._log.info("Test 7 PASSED: Scale shift behavior correct")


# =============================================================================
# Test 8: TensorTile Read Status Behavior
# =============================================================================

@cocotb.test()
async def test_tensortile_read_status(dut):
    """Test 8: Verify TensorTile status read command."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    q_values = [1] * 8
    k_values = [1] * 8
    
    await load_tensortile_vectors(dut, q_values, k_values)
    await write_cmd(dut, BLOCK_TENSORTILE, TT_CMD_RUN_FOLDED_QK, 0x0)
    await ClockCycles(dut.clk, 5)
    
    # Read status via command
    status = await read_cmd(dut, BLOCK_TENSORTILE, TT_CMD_READ_STATUS)
    status_nibble = (status >> 4) & 0xF
    
    # Status = {context_valid, overflow, done, busy}
    busy = status_nibble & 0x1
    done = (status_nibble >> 1) & 0x1
    overflow = (status_nibble >> 2) & 0x1
    context_valid = (status_nibble >> 3) & 0x1
    
    dut._log.info(f"Status: busy={busy}, done={done}, overflow={overflow}, context_valid={context_valid}")
    
    assert done == 1, "Expected done=1 after computation"
    assert busy == 0, "Expected busy=0 after completion"
    assert context_valid == 1, "Expected context_valid=1 after LOAD_CONTEXT"
    
    dut._log.info("Test 8 PASSED: Read status behavior correct")


# =============================================================================
# Test 9: PolicyGate Invalid Policy Blocks
# =============================================================================

@cocotb.test()
async def test_policygate_invalid_policy(dut):
    """Test 9: policy_ok=0 results in BLOCK + POLICY_ERROR."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_TOOL_ID, 0x5)
    
    # Flags: context_valid=1, policy_ok=0
    flags = 0b0001
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_FLAGS, flags)
    
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_EVALUATE, 0x0)
    await ClockCycles(dut.clk, 2)
    
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
    
    dut._log.info("Test 9 PASSED: Invalid policy blocks correctly")


# =============================================================================
# Test 10: PolicyGate Invalid Context + Medium/High Risk Blocks
# =============================================================================

@cocotb.test()
async def test_policygate_invalid_context_medium_risk(dut):
    """Test 10: Invalid context with medium+ risk blocks."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_TOOL_ID, 0x5)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_RISK_CLASS, RISK_MEDIUM)
    
    # Flags: context_valid=0, policy_ok=1
    flags = 0b0010
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_FLAGS, flags)
    
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_EVALUATE, 0x0)
    await ClockCycles(dut.clk, 2)
    
    dut.uio_in.value = BLOCK_POLICYGATE << 2
    await ClockCycles(dut.clk, 1)
    
    uo = int(dut.uo_out.value)
    
    allow = uo & 0x1
    block = (uo >> 1) & 0x1
    
    dut._log.info(f"Invalid context + medium risk: allow={allow}, block={block}")
    
    assert block == 1, "Expected block=1 for invalid context + medium risk"
    assert allow == 0, "Expected allow=0"
    
    dut._log.info("Test 10 PASSED: Invalid context + medium risk blocks")


# =============================================================================
# Test 11: PolicyGate High-Risk Without Human Approval Requires Human
# =============================================================================

@cocotb.test()
async def test_policygate_high_risk_no_human(dut):
    """Test 11: High-risk without human approval returns REQUIRE_HUMAN."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_TOOL_ID, 0x5)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_RISK_CLASS, RISK_HIGH)
    
    # Flags: context_valid=1, policy_ok=1, human_approved=0
    flags = 0b0011
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_FLAGS, flags)
    
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_EVALUATE, 0x0)
    await ClockCycles(dut.clk, 2)
    
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
    
    dut._log.info("Test 11 PASSED: High-risk without human requires human approval")


# =============================================================================
# Test 12: PolicyGate High-Risk With Human Approval Allows and Logs
# =============================================================================

@cocotb.test()
async def test_policygate_high_risk_with_human(dut):
    """Test 12: High-risk with human approval allows and logs."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_TOOL_ID, 0x5)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_RISK_CLASS, RISK_HIGH)
    
    # Flags: context_valid=1, policy_ok=1, human_approved=1, offline=1
    flags = 0b1111
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_FLAGS, flags)
    
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_EVALUATE, 0x0)
    await ClockCycles(dut.clk, 2)
    
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
    assert log_required == 1, "Expected log_required=1 in offline mode with high risk"
    
    dut._log.info("Test 12 PASSED: High-risk with human approval allows and logs")


# =============================================================================
# Test 13: PolicyGate Battery Low + Nonessential Tool Blocks
# =============================================================================

@cocotb.test()
async def test_policygate_battery_low_nonessential(dut):
    """Test 13: Battery low with nonessential tool blocks."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Tool ID 0x8+ is nonessential
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_TOOL_ID, 0x8)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_RISK_CLASS, RISK_LOW)
    
    # Flags: context_valid=1, policy_ok=1
    flags = 0b0011
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_FLAGS, flags)
    
    # Power flags: battery_low=1
    power_flags = 0b0001
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_POWER_EMERG, power_flags)
    
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_EVALUATE, 0x0)
    await ClockCycles(dut.clk, 2)
    
    dut.uio_in.value = BLOCK_POLICYGATE << 2
    await ClockCycles(dut.clk, 1)
    
    uo = int(dut.uo_out.value)
    
    allow = uo & 0x1
    block = (uo >> 1) & 0x1
    
    dut._log.info(f"Battery low + nonessential: allow={allow}, block={block}")
    
    assert block == 1, "Expected block=1 for battery_low + nonessential"
    assert allow == 0, "Expected allow=0"
    
    dut._log.info("Test 13 PASSED: Battery low + nonessential tool blocks")


# =============================================================================
# Test 14: PolicyGate Emergency Safety-Critical Path Allows and Logs
# =============================================================================

@cocotb.test()
async def test_policygate_emergency_safety(dut):
    """Test 14: Emergency mode with safety-critical tool allows with emergency_path."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # Safety-critical tool ID (0x1, 0x2, or 0x3)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_TOOL_ID, 0x1)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_RISK_CLASS, RISK_LOW)
    
    # Flags: context_valid=1, policy_ok=1
    flags = 0b0011
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_FLAGS, flags)
    
    # Power flags: emergency_mode=1
    power_flags = 0b0010
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_POWER_EMERG, power_flags)
    
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_EVALUATE, 0x0)
    await ClockCycles(dut.clk, 2)
    
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
    
    dut._log.info("Test 14 PASSED: Emergency safety-critical path works correctly")


# =============================================================================
# Test 15: PolicyGate Read Decision Bit Order
# =============================================================================

@cocotb.test()
async def test_policygate_read_decision_order(dut):
    """Test 15: Verify READ_DECISION bit order matches top-level outputs."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_TOOL_ID, 0x5)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_RISK_CLASS, RISK_HIGH)
    
    # Flags that trigger require_human + log_required
    flags = 0b0011  # context_valid=1, policy_ok=1, human_approved=0
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_FLAGS, flags)
    
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_EVALUATE, 0x0)
    await ClockCycles(dut.clk, 2)
    
    # Read decision via command
    decision = await read_cmd(dut, BLOCK_POLICYGATE, PG_CMD_READ_DECISION)
    decision_nibble = (decision >> 4) & 0xF
    
    # Decision nibble = {log_required, require_human, block, allow}
    allow = decision_nibble & 0x1
    block = (decision_nibble >> 1) & 0x1
    require_human = (decision_nibble >> 2) & 0x1
    log_required = (decision_nibble >> 3) & 0x1
    
    # Compare with direct outputs
    dut.uio_in.value = BLOCK_POLICYGATE << 2
    await ClockCycles(dut.clk, 1)
    
    uo_direct = int(dut.uo_out.value)
    allow_direct = uo_direct & 0x1
    block_direct = (uo_direct >> 1) & 0x1
    require_human_direct = (uo_direct >> 2) & 0x1
    log_required_direct = (uo_direct >> 3) & 0x1
    
    dut._log.info(f"READ_DECISION: allow={allow}, block={block}, require_human={require_human}, log_required={log_required}")
    dut._log.info(f"Direct outputs: allow={allow_direct}, block={block_direct}, require_human={require_human_direct}, log_required={log_required_direct}")
    
    assert allow == allow_direct, "allow bit mismatch"
    assert block == block_direct, "block bit mismatch"
    assert require_human == require_human_direct, "require_human bit mismatch"
    assert log_required == log_required_direct, "log_required bit mismatch"
    
    dut._log.info("Test 15 PASSED: Read decision bit order correct")


# =============================================================================
# Test 16: Combined Flow - TensorTile + PolicyGate
# =============================================================================

@cocotb.test()
async def test_combined_flow(dut):
    """Test 16: TensorTile computes, then PolicyGate evaluates high-risk tool."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    await reset_dut(dut)
    
    # --- Phase 1: TensorTile computes QK score ---
    dut._log.info("Phase 1: TensorTile computing QK score...")
    
    q_values = [1, 2, 1, 2, 1, 2, 1, 2]
    k_values = [1, 2, 1, 2, 1, 2, 1, 2]
    
    expected = golden_int4_dot_product(q_values, k_values)
    
    await load_tensortile_vectors(dut, q_values, k_values)
    result = await run_tensortile_and_read(dut)
    
    dut._log.info(f"TensorTile result: {result} (expected {expected})")
    assert result == expected, f"TensorTile: expected {expected}, got {result}"
    
    # Verify done and context_valid
    dut.uio_in.value = BLOCK_TENSORTILE << 2
    await ClockCycles(dut.clk, 1)
    uo = int(dut.uo_out.value)
    done = (uo >> 1) & 0x1
    context_valid = (uo >> 3) & 0x1
    
    assert done == 1, "TensorTile should be done"
    assert context_valid == 1, "Context should be valid"
    
    # --- Phase 2: PolicyGate evaluates high-risk tool call ---
    dut._log.info("Phase 2: PolicyGate evaluating high-risk tool call...")
    
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_TOOL_ID, 0x5)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_RISK_CLASS, RISK_HIGH)
    
    # Flags: context_valid=1, policy_ok=1, human_approved=0 (no approval)
    flags = 0b0011
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_FLAGS, flags)
    
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_EVALUATE, 0x0)
    await ClockCycles(dut.clk, 2)
    
    dut.uio_in.value = BLOCK_POLICYGATE << 2
    await ClockCycles(dut.clk, 1)
    
    uo = int(dut.uo_out.value)
    uio = int(dut.uio_out.value)
    
    allow = uo & 0x1
    require_human = (uo >> 2) & 0x1
    log_required = (uo >> 3) & 0x1
    evaluated = (uio >> 7) & 0x1
    
    dut._log.info(f"PolicyGate: allow={allow}, require_human={require_human}, log_required={log_required}, evaluated={evaluated}")
    
    assert evaluated == 1, "PolicyGate should have evaluated"
    assert require_human == 1, "Expected REQUIRE_HUMAN for high-risk without approval"
    assert log_required == 1, "Expected LOG_REQUIRED"
    assert allow == 0, "Should not allow without human approval"
    
    dut._log.info("Test 16 PASSED: Combined TensorTile + PolicyGate flow works")

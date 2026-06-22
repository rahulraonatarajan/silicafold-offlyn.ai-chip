# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 Rahul Rao Natarajan / Offlyn.ai
#
# SilicaFold V0 - Use Case Validation Tests
# Validates the five scenarios documented in docs/use_cases.md against RTL.

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

from test_combined import (
    BLOCK_POLICYGATE,
    BLOCK_TENSORTILE,
    PG_CMD_EVALUATE,
    PG_CMD_LOAD_FLAGS,
    PG_CMD_LOAD_POWER_EMERG,
    PG_CMD_LOAD_RISK_CLASS,
    PG_CMD_LOAD_TOOL_ID,
    RISK_EMERGENCY,
    RISK_HIGH,
    RISK_LOW,
    RISK_MEDIUM,
    golden_int4_dot_product,
    load_tensortile_vectors,
    reset_dut,
    run_tensortile_and_read,
    write_cmd,
)


async def load_policygate_state(
    dut,
    tool_id,
    risk_class,
    flags,
    power_flags=0,
):
    """Load PolicyGate registers before evaluation."""
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_TOOL_ID, tool_id)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_RISK_CLASS, risk_class)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_FLAGS, flags)
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_LOAD_POWER_EMERG, power_flags)


async def evaluate_policygate(dut):
    """Evaluate PolicyGate and return decision/status dict."""
    await write_cmd(dut, BLOCK_POLICYGATE, PG_CMD_EVALUATE, 0x0)
    await ClockCycles(dut.clk, 2)

    dut.uio_in.value = BLOCK_POLICYGATE << 2
    await ClockCycles(dut.clk, 1)

    uo = int(dut.uo_out.value)
    uio = int(dut.uio_out.value)

    return {
        "allow": uo & 0x1,
        "block": (uo >> 1) & 0x1,
        "require_human": (uo >> 2) & 0x1,
        "log_required": (uo >> 3) & 0x1,
        "policy_error": (uio >> 4) & 0x1,
        "high_risk": (uio >> 5) & 0x1,
        "emergency_path": (uio >> 6) & 0x1,
        "evaluated": (uio >> 7) & 0x1,
    }


def flags(context_valid=0, policy_ok=0, human_approved=0, offline_mode=0):
    """Pack LOAD_FLAGS din nibble."""
    return (
        (context_valid & 0x1)
        | ((policy_ok & 0x1) << 1)
        | ((human_approved & 0x1) << 2)
        | ((offline_mode & 0x1) << 3)
    )


def power_flags(battery_low=0, emergency_mode=0):
    """Pack LOAD_POWER_EMERG din nibble."""
    return (battery_low & 0x1) | ((emergency_mode & 0x1) << 1)


@cocotb.test()
async def test_use_case_1_disaster_response_emergency_risk(dut):
    """Use Case 1: Emergency beacon with RISK_EMERGENCY hits Priority 5."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    await load_policygate_state(
        dut,
        tool_id=0x1,
        risk_class=RISK_EMERGENCY,
        flags=flags(context_valid=1, policy_ok=1, offline_mode=1),
        power_flags=power_flags(emergency_mode=1),
    )

    decision = await evaluate_policygate(dut)

    dut._log.info(f"Use Case 1 (EMERGENCY risk): {decision}")
    assert decision["allow"] == 1
    assert decision["block"] == 0
    assert decision["require_human"] == 0
    assert decision["log_required"] == 1
    assert decision["emergency_path"] == 1
    assert decision["evaluated"] == 1


@cocotb.test()
async def test_use_case_1_disaster_response_high_risk_requires_human(dut):
    """Use Case 1 nuance: RISK_HIGH + emergency_mode still hits Priority 3 first."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    await load_policygate_state(
        dut,
        tool_id=0x1,
        risk_class=RISK_HIGH,
        flags=flags(context_valid=1, policy_ok=1, offline_mode=1),
        power_flags=power_flags(emergency_mode=1),
    )

    decision = await evaluate_policygate(dut)

    dut._log.info(f"Use Case 1 (HIGH risk + emergency_mode): {decision}")
    assert decision["allow"] == 0
    assert decision["require_human"] == 1
    assert decision["log_required"] == 1
    assert decision["emergency_path"] == 0


@cocotb.test()
async def test_use_case_2_field_drone_motor_actuation(dut):
    """Use Case 2: High-risk motor actuation requires human approval."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    await load_policygate_state(
        dut,
        tool_id=0x2,
        risk_class=RISK_HIGH,
        flags=flags(context_valid=1, policy_ok=1, human_approved=0),
    )

    decision = await evaluate_policygate(dut)

    dut._log.info(f"Use Case 2: {decision}")
    assert decision["allow"] == 0
    assert decision["block"] == 0
    assert decision["require_human"] == 1
    assert decision["log_required"] == 1
    assert decision["high_risk"] == 1


@cocotb.test()
async def test_use_case_3_enterprise_export_offline_log(dut):
    """Use Case 3: Offline medium-risk export allows with mandatory logging."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    await load_policygate_state(
        dut,
        tool_id=0x5,
        risk_class=RISK_MEDIUM,
        flags=flags(context_valid=1, policy_ok=1, human_approved=0, offline_mode=1),
    )

    decision = await evaluate_policygate(dut)

    dut._log.info(f"Use Case 3: {decision}")
    assert decision["allow"] == 1
    assert decision["block"] == 0
    assert decision["require_human"] == 0
    assert decision["log_required"] == 1


@cocotb.test()
async def test_use_case_4_battery_low_nonessential_block(dut):
    """Use Case 4: Battery low blocks nonessential analytics report."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    await load_policygate_state(
        dut,
        tool_id=0xA,
        risk_class=RISK_LOW,
        flags=flags(context_valid=1, policy_ok=1),
        power_flags=power_flags(battery_low=1),
    )

    decision = await evaluate_policygate(dut)

    dut._log.info(f"Use Case 4: {decision}")
    assert decision["allow"] == 0
    assert decision["block"] == 1
    assert decision["require_human"] == 0
    assert decision["log_required"] == 1


@cocotb.test()
async def test_use_case_5_tensortile_context_scoring_then_policygate(dut):
    """Use Case 5: TensorTile scores context, then PolicyGate requires human."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    q_values = [1, 2, 1, 2, 1, 2, 1, 2]
    k_values = [1, 2, 1, 2, 1, 2, 1, 2]
    expected = golden_int4_dot_product(q_values, k_values)

    await load_tensortile_vectors(dut, q_values, k_values)
    result = await run_tensortile_and_read(dut)
    assert result == expected

    dut.uio_in.value = BLOCK_TENSORTILE << 2
    await ClockCycles(dut.clk, 1)
    tt_uo = int(dut.uo_out.value)
    assert ((tt_uo >> 1) & 0x1) == 1, "TensorTile done expected"
    assert ((tt_uo >> 3) & 0x1) == 1, "TensorTile context_valid expected"

    await load_policygate_state(
        dut,
        tool_id=0x2,
        risk_class=RISK_HIGH,
        flags=flags(context_valid=1, policy_ok=1, human_approved=0),
    )

    decision = await evaluate_policygate(dut)

    dut._log.info(f"Use Case 5 PolicyGate phase: {decision}")
    assert decision["require_human"] == 1
    assert decision["log_required"] == 1
    assert decision["allow"] == 0
    assert decision["evaluated"] == 1

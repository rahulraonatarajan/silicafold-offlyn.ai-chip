# SPDX-License-Identifier: Apache-2.0
# Makefile for SilicaFold V0 cocotb tests

# Defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Source files
VERILOG_SOURCES += $(PWD)/../src/sf_tensortile_core.v
VERILOG_SOURCES += $(PWD)/../src/sf_policygate_core.v
VERILOG_SOURCES += $(PWD)/../src/tt_um_rahulraonatarajan_silicafold_v0.v

# Top level module
TOPLEVEL = tt_um_rahulraonatarajan_silicafold_v0

# Python test modules
COCOTB_TEST_MODULES := test_combined,test_use_cases

# Compiler flags for Icarus Verilog
COMPILE_ARGS += -g2005

# Include cocotb's make rules
include $(shell cocotb-config --makefiles)/Makefile.sim

# Clean target
clean::
	rm -rf __pycache__ results.xml *.vcd sim_build

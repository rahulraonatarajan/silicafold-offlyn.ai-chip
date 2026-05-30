// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 Rahul Rao Natarajan / Offlyn.ai
//
// SilicaFold V0 - Top Module for Tiny Tapeout
// Combines TensorTile (folded INT4 QK) + PolicyGate (tool authorization)
//
// This is a proof-of-silicon artifact for offline SLM agents.
// The chip does not understand natural language. It computes and authorizes.
//
// Pin Interface:
//   ui_in[3:0]  = command nibble
//   ui_in[7:4]  = data nibble
//   uio_in[0]   = WR_STB (write strobe)
//   uio_in[1]   = RD_STB (read strobe)  
//   uio_in[2]   = BLOCK_SELECT (0=TensorTile, 1=PolicyGate)
//   uio_in[3]   = DEBUG_MODE (reserved)
//   uio_oe      = 8'b1111_0000 (upper nibble outputs, lower nibble inputs)

`default_nettype none

module tt_um_rahulraonatarajan_silicafold_v0 (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // =========================================================================
    // Pin Decoding
    // =========================================================================
    wire [3:0] cmd       = ui_in[3:0];   // Command nibble
    wire [3:0] din       = ui_in[7:4];   // Data nibble
    wire       wr_stb    = uio_in[0];    // Write strobe
    wire       rd_stb    = uio_in[1];    // Read strobe
    wire       blk_sel   = uio_in[2];    // Block select: 0=TensorTile, 1=PolicyGate
    wire       dbg_mode  = uio_in[3];    // Debug mode (reserved for future use)

    // =========================================================================
    // uio_oe Configuration  
    // Lower nibble [3:0] are inputs, upper nibble [7:4] are outputs
    // Use combinational logic through ena to create routable paths
    // This prevents synthesis from creating unroutable tie cells
    // When ena=1: lower nibble = ~1 = 0 (input mode)
    //             upper nibble = 1 = 1 (output mode)  
    // =========================================================================
    assign uio_oe[0] = ~ena;  // 0 when powered (input mode)
    assign uio_oe[1] = ~ena;  // 0 when powered (input mode)
    assign uio_oe[2] = ~ena;  // 0 when powered (input mode)
    assign uio_oe[3] = ~ena;  // 0 when powered (input mode)
    assign uio_oe[4] = ena;   // 1 when powered (output mode)
    assign uio_oe[5] = ena;   // 1 when powered (output mode)
    assign uio_oe[6] = ena;   // 1 when powered (output mode)
    assign uio_oe[7] = ena;   // 1 when powered (output mode)

    // =========================================================================
    // TensorTile Instance
    // =========================================================================
    wire        tt_busy;
    wire        tt_done;
    wire        tt_overflow;
    wire        tt_context_valid;
    wire [3:0]  tt_dout;
    wire [3:0]  tt_cycle_count;

    sf_tensortile_core u_tensortile (
        .clk           (clk),
        .rst_n         (rst_n),
        .cmd           (cmd),
        .din           (din),
        .wr_stb        (wr_stb && !blk_sel),  // Route WR only when selected
        .rd_stb        (rd_stb && !blk_sel),  // Route RD only when selected
        .busy          (tt_busy),
        .done          (tt_done),
        .overflow      (tt_overflow),
        .context_valid (tt_context_valid),
        .dout          (tt_dout),
        .cycle_count   (tt_cycle_count)
    );

    // =========================================================================
    // PolicyGate Instance
    // =========================================================================
    wire        pg_allow;
    wire        pg_block;
    wire        pg_require_human;
    wire        pg_log_required;
    wire        pg_policy_error;
    wire        pg_high_risk;
    wire        pg_emergency_path;
    wire        pg_evaluated;
    wire [3:0]  pg_dout;
    wire [3:0]  pg_audit_counter;

    sf_policygate_core u_policygate (
        .clk           (clk),
        .rst_n         (rst_n),
        .cmd           (cmd),
        .din           (din),
        .wr_stb        (wr_stb && blk_sel),   // Route WR only when selected
        .rd_stb        (rd_stb && blk_sel),   // Route RD only when selected
        .allow         (pg_allow),
        .block         (pg_block),
        .require_human (pg_require_human),
        .log_required  (pg_log_required),
        .policy_error  (pg_policy_error),
        .high_risk     (pg_high_risk),
        .emergency_path(pg_emergency_path),
        .evaluated     (pg_evaluated),
        .dout          (pg_dout),
        .audit_counter (pg_audit_counter)
    );

    // =========================================================================
    // Output Multiplexing based on BLOCK_SELECT
    // =========================================================================
    // uo_out[3:0] = status bits (block-specific)
    // uo_out[7:4] = data output nibble (block-specific)
    // uio_out[3:0] = inputs (directly pass through as 0)
    // uio_out[7:4] = extended outputs (block-specific)

    // When BLOCK_SELECT = 0 (TensorTile):
    //   uo_out[0] = busy
    //   uo_out[1] = done
    //   uo_out[2] = overflow
    //   uo_out[3] = context_valid
    //   uo_out[7:4] = tensor output nibble
    //   uio_out[7:4] = cycle_count
    
    // When BLOCK_SELECT = 1 (PolicyGate):
    //   uo_out[0] = allow
    //   uo_out[1] = block
    //   uo_out[2] = require_human
    //   uo_out[3] = log_required
    //   uo_out[7:4] = policy output nibble
    //   uio_out[4] = policy_error
    //   uio_out[5] = high_risk
    //   uio_out[6] = emergency_path
    //   uio_out[7] = evaluated

    wire [3:0] status_mux = blk_sel ? 
        {pg_log_required, pg_require_human, pg_block, pg_allow} :
        {tt_context_valid, tt_overflow, tt_done, tt_busy};

    wire [3:0] dout_mux = blk_sel ? pg_dout : tt_dout;

    wire [3:0] ext_mux = blk_sel ?
        {pg_evaluated, pg_emergency_path, pg_high_risk, pg_policy_error} :
        tt_cycle_count;

    assign uo_out = {dout_mux, status_mux};
    
    // uio_out: lower nibble is 0 (inputs), upper nibble is ext_mux
    assign uio_out = {ext_mux, 4'b0000};

    // =========================================================================
    // Unused Signal Handling
    // dbg_mode is reserved for future use
    // ena is used for uio_oe configuration
    // =========================================================================
    wire _unused = &{dbg_mode, 1'b0};

endmodule

`default_nettype wire

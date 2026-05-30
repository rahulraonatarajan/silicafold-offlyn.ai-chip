// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 Rahul Rao Natarajan / Offlyn.ai
//
// SilicaFold V0 - TensorTile Core
// A folded 4-lane INT4 QK dot-product primitive for offline SLM context operations.
//
// This is a simplified educational V0 implementation. It does NOT represent
// production Offlyn.ai IP, optimized commercial silicon, or patentable architecture.
//
// The chip does not understand natural language. TensorTile computes;
// the SLM/runtime reasons.

`default_nettype none

module sf_tensortile_core (
    input  wire        clk,
    input  wire        rst_n,
    
    // Command interface
    input  wire [3:0]  cmd,           // Command nibble
    input  wire [3:0]  din,           // Data nibble
    input  wire        wr_stb,        // Write strobe
    input  wire        rd_stb,        // Read strobe
    
    // Status outputs
    output reg         busy,
    output reg         done,
    output reg         overflow,
    output reg         context_valid,
    
    // Data outputs
    output reg  [3:0]  dout,          // Selected output nibble
    output reg  [3:0]  cycle_count    // Compute cycle counter
);

    // =========================================================================
    // Command Encoding
    // =========================================================================
    localparam CMD_NOP              = 4'h0;
    localparam CMD_LOAD_Q_NIBBLE    = 4'h1;
    localparam CMD_LOAD_K_NIBBLE    = 4'h2;
    localparam CMD_LOAD_CONTEXT     = 4'h3;
    localparam CMD_LOAD_SCALE       = 4'h4;
    localparam CMD_RUN_FOLDED_QK    = 4'h5;
    localparam CMD_READ_RESULT_LOW  = 4'h6;
    localparam CMD_READ_RESULT_HIGH = 4'h7;
    localparam CMD_READ_CYCLE       = 4'h8;
    localparam CMD_READ_STATUS      = 4'h9;
    localparam CMD_RESET_STATE      = 4'hA;

    // =========================================================================
    // State Machine
    // =========================================================================
    localparam STATE_IDLE    = 2'd0;
    localparam STATE_PHASE1  = 2'd1;
    localparam STATE_PHASE2  = 2'd2;
    localparam STATE_DONE    = 2'd3;

    reg [1:0] state;

    // =========================================================================
    // Data Registers
    // =========================================================================
    // Q and K registers: 8 x INT4 values stored as 32-bit vectors
    // Each INT4 is signed two's complement: range -8 to +7
    reg [31:0] q_reg;   // q_reg[3:0]=Q0, q_reg[7:4]=Q1, ..., q_reg[31:28]=Q7
    reg [31:0] k_reg;   // k_reg[3:0]=K0, k_reg[7:4]=K1, ..., k_reg[31:28]=K7
    
    // Separate load indices for Q and K to avoid confusion
    // Each index auto-increments after each LOAD_Q_NIBBLE or LOAD_K_NIBBLE
    // CMD_LOAD_CONTEXT resets BOTH indices to 0
    reg [2:0]  q_load_index;
    reg [2:0]  k_load_index;
    
    // Context slot (toy field to demonstrate context tracking)
    reg [3:0]  context_slot;
    
    // Scale/shift amount for final result
    reg [2:0]  scale_shift;
    
    // 16-bit signed accumulator for dot product
    reg signed [15:0] accumulator;
    
    // Scaled result after arithmetic right shift
    reg signed [15:0] result;

    // =========================================================================
    // INT4 Sign Extension Helper
    // Convert 4-bit unsigned to signed 5-bit for multiplication
    // =========================================================================
    function signed [4:0] sign_extend_int4;
        input [3:0] val;
        begin
            sign_extend_int4 = {val[3], val};
        end
    endfunction

    // =========================================================================
    // 4-Lane MAC: Compute partial dot product for 4 elements
    // =========================================================================
    function signed [15:0] mac_4lane;
        input [15:0] q_4vals;  // 4 INT4 Q values packed
        input [15:0] k_4vals;  // 4 INT4 K values packed
        reg signed [4:0] q0, q1, q2, q3;
        reg signed [4:0] k0, k1, k2, k3;
        reg signed [9:0] p0, p1, p2, p3;
        begin
            // Extract and sign-extend each INT4
            q0 = sign_extend_int4(q_4vals[3:0]);
            q1 = sign_extend_int4(q_4vals[7:4]);
            q2 = sign_extend_int4(q_4vals[11:8]);
            q3 = sign_extend_int4(q_4vals[15:12]);
            
            k0 = sign_extend_int4(k_4vals[3:0]);
            k1 = sign_extend_int4(k_4vals[7:4]);
            k2 = sign_extend_int4(k_4vals[11:8]);
            k3 = sign_extend_int4(k_4vals[15:12]);
            
            // Multiply (5-bit * 5-bit = 10-bit result)
            p0 = q0 * k0;
            p1 = q1 * k1;
            p2 = q2 * k2;
            p3 = q3 * k3;
            
            // Sum all products
            mac_4lane = {{6{p0[9]}}, p0} + {{6{p1[9]}}, p1} + 
                        {{6{p2[9]}}, p2} + {{6{p3[9]}}, p3};
        end
    endfunction

    // =========================================================================
    // Overflow Detection
    // Simple toy overflow: check if accumulator exceeds signed 8-bit range
    // =========================================================================
    wire acc_overflow = (accumulator > 16'sd127) || (accumulator < -16'sd128);

    // =========================================================================
    // Main State Machine and Command Processing
    // =========================================================================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // Reset all state
            state         <= STATE_IDLE;
            q_reg         <= 32'd0;
            k_reg         <= 32'd0;
            q_load_index  <= 3'd0;
            k_load_index  <= 3'd0;
            context_slot  <= 4'd0;
            scale_shift   <= 3'd0;
            accumulator   <= 16'sd0;
            result        <= 16'sd0;
            busy          <= 1'b0;
            done          <= 1'b0;
            overflow      <= 1'b0;
            context_valid <= 1'b0;
            dout          <= 4'd0;
            cycle_count   <= 4'd0;
        end else begin
            // State machine for folded computation
            case (state)
                STATE_IDLE: begin
                    // Process commands when write strobe active
                    if (wr_stb) begin
                        case (cmd)
                            CMD_NOP: begin
                                // No operation
                            end
                            
                            CMD_LOAD_Q_NIBBLE: begin
                                // Load one INT4 Q value at q_load_index position
                                case (q_load_index)
                                    3'd0: q_reg[3:0]   <= din;
                                    3'd1: q_reg[7:4]   <= din;
                                    3'd2: q_reg[11:8]  <= din;
                                    3'd3: q_reg[15:12] <= din;
                                    3'd4: q_reg[19:16] <= din;
                                    3'd5: q_reg[23:20] <= din;
                                    3'd6: q_reg[27:24] <= din;
                                    3'd7: q_reg[31:28] <= din;
                                endcase
                                q_load_index <= q_load_index + 1'b1;
                            end
                            
                            CMD_LOAD_K_NIBBLE: begin
                                // Load one INT4 K value at k_load_index position
                                case (k_load_index)
                                    3'd0: k_reg[3:0]   <= din;
                                    3'd1: k_reg[7:4]   <= din;
                                    3'd2: k_reg[11:8]  <= din;
                                    3'd3: k_reg[15:12] <= din;
                                    3'd4: k_reg[19:16] <= din;
                                    3'd5: k_reg[23:20] <= din;
                                    3'd6: k_reg[27:24] <= din;
                                    3'd7: k_reg[31:28] <= din;
                                endcase
                                k_load_index <= k_load_index + 1'b1;
                            end
                            
                            CMD_LOAD_CONTEXT: begin
                                context_slot  <= din;
                                context_valid <= 1'b1;
                                q_load_index  <= 3'd0;  // Reset both load indices
                                k_load_index  <= 3'd0;
                            end
                            
                            CMD_LOAD_SCALE: begin
                                scale_shift <= din[2:0];
                            end
                            
                            CMD_RUN_FOLDED_QK: begin
                                // Start folded QK computation
                                busy        <= 1'b1;
                                done        <= 1'b0;
                                overflow    <= 1'b0;
                                accumulator <= 16'sd0;
                                cycle_count <= 4'd0;
                                state       <= STATE_PHASE1;
                            end
                            
                            CMD_RESET_STATE: begin
                                // Soft reset without full hardware reset
                                q_reg         <= 32'd0;
                                k_reg         <= 32'd0;
                                q_load_index  <= 3'd0;
                                k_load_index  <= 3'd0;
                                context_slot  <= 4'd0;
                                scale_shift   <= 3'd0;
                                accumulator   <= 16'sd0;
                                result        <= 16'sd0;
                                busy          <= 1'b0;
                                done          <= 1'b0;
                                overflow      <= 1'b0;
                                context_valid <= 1'b0;
                                cycle_count   <= 4'd0;
                            end
                            
                            default: begin
                                // Unknown command - ignore
                            end
                        endcase
                    end
                    
                    // Handle read commands
                    if (rd_stb) begin
                        case (cmd)
                            CMD_READ_RESULT_LOW: begin
                                dout <= result[3:0];
                            end
                            
                            CMD_READ_RESULT_HIGH: begin
                                dout <= result[7:4];
                            end
                            
                            CMD_READ_CYCLE: begin
                                dout <= cycle_count;
                            end
                            
                            CMD_READ_STATUS: begin
                                // Pack status bits into nibble
                                dout <= {context_valid, overflow, done, busy};
                            end
                            
                            default: begin
                                dout <= 4'd0;
                            end
                        endcase
                    end
                end
                
                STATE_PHASE1: begin
                    // Compute first 4 elements: Q[0:3] * K[0:3]
                    accumulator <= mac_4lane(q_reg[15:0], k_reg[15:0]);
                    cycle_count <= 4'd1;
                    state       <= STATE_PHASE2;
                end
                
                STATE_PHASE2: begin
                    // Compute second 4 elements: Q[4:7] * K[4:7] and add to accumulator
                    accumulator <= accumulator + mac_4lane(q_reg[31:16], k_reg[31:16]);
                    cycle_count <= 4'd2;
                    state       <= STATE_DONE;
                end
                
                STATE_DONE: begin
                    // Apply scale shift and set outputs
                    result   <= accumulator >>> scale_shift;
                    overflow <= acc_overflow;
                    busy     <= 1'b0;
                    done     <= 1'b1;
                    state    <= STATE_IDLE;
                end
            endcase
        end
    end

endmodule

`default_nettype wire

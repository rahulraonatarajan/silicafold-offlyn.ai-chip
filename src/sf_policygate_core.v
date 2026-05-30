// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 Rahul Rao Natarajan / Offlyn.ai
//
// SilicaFold V0 - PolicyGate Core
// A deterministic toy policy gate for offline SLM tool-call authorization.
//
// This is a simplified educational V0 implementation. It does NOT include:
// - Cryptographic policy verification
// - Signed grant tokens
// - Secure storage or tamper resistance
// - Model attestation
// - Customer-specific policy logic
// - Production Offlyn.ai IP
//
// Those are future commercial roadmap items.

`default_nettype none

module sf_policygate_core (
    input  wire        clk,
    input  wire        rst_n,
    
    // Command interface
    input  wire [3:0]  cmd,           // Command nibble
    input  wire [3:0]  din,           // Data nibble
    input  wire        wr_stb,        // Write strobe
    input  wire        rd_stb,        // Read strobe
    
    // Decision outputs
    output reg         allow,
    output reg         block,
    output reg         require_human,
    output reg         log_required,
    
    // Extended status outputs
    output reg         policy_error,
    output reg         high_risk,
    output reg         emergency_path,
    output reg         evaluated,
    
    // Data outputs
    output reg  [3:0]  dout,          // Selected output nibble
    output reg  [3:0]  audit_counter  // Audit event counter
);

    // =========================================================================
    // Command Encoding
    // =========================================================================
    localparam CMD_NOP               = 4'h0;
    localparam CMD_LOAD_TOOL_ID      = 4'h1;
    localparam CMD_LOAD_RISK_CLASS   = 4'h2;
    localparam CMD_LOAD_FLAGS        = 4'h3;
    localparam CMD_LOAD_POWER_EMERG  = 4'h4;
    localparam CMD_EVALUATE          = 4'h5;
    localparam CMD_READ_DECISION     = 4'h6;
    localparam CMD_READ_AUDIT        = 4'h7;
    localparam CMD_RESET_STATE       = 4'h8;

    // =========================================================================
    // Risk Class Encoding
    // =========================================================================
    localparam RISK_LOW       = 2'd0;
    localparam RISK_MEDIUM    = 2'd1;
    localparam RISK_HIGH      = 2'd2;
    localparam RISK_EMERGENCY = 2'd3;

    // =========================================================================
    // Policy Registers
    // =========================================================================
    reg [3:0] tool_id;        // Tool identifier (0-15)
    reg [1:0] risk_class;     // Risk classification
    
    // Context and policy flags (from LOAD_FLAGS)
    reg context_valid;        // Context has been validated
    reg policy_ok;            // Policy permits this action type
    reg human_approved;       // Human has pre-approved this action
    reg offline_mode;         // System is operating offline
    
    // Power and emergency flags (from LOAD_POWER_EMERG)
    reg battery_low;          // Battery is critically low
    reg emergency_mode;       // Emergency override active

    // =========================================================================
    // Tool Classification
    // - Safety-critical tools: 0x1, 0x2, 0x3
    // - Nonessential tools: 0x8 through 0xF
    // =========================================================================
    wire tool_is_safety_critical = (tool_id == 4'h1) || 
                                   (tool_id == 4'h2) || 
                                   (tool_id == 4'h3);
    
    wire tool_is_nonessential = (tool_id >= 4'h8);

    // =========================================================================
    // Decision Logic (Combinational for synthesis clarity)
    // Priority-ordered evaluation per specification
    // =========================================================================
    reg         next_allow;
    reg         next_block;
    reg         next_require_human;
    reg         next_log_required;
    reg         next_policy_error;
    reg         next_high_risk;
    reg         next_emergency_path;

    always @(*) begin
        // Default: no action
        next_allow         = 1'b0;
        next_block         = 1'b0;
        next_require_human = 1'b0;
        next_log_required  = 1'b0;
        next_policy_error  = 1'b0;
        next_high_risk     = 1'b0;
        next_emergency_path = 1'b0;
        
        // Mark high risk if risk_class is HIGH or EMERGENCY
        if (risk_class >= RISK_HIGH) begin
            next_high_risk = 1'b1;
        end
        
        // Priority 1: Policy check failed
        if (!policy_ok) begin
            next_block        = 1'b1;
            next_policy_error = 1'b1;
            next_log_required = 1'b1;
        end
        // Priority 2: Invalid context with medium+ risk
        else if (!context_valid && (risk_class >= RISK_MEDIUM)) begin
            next_block        = 1'b1;
            next_log_required = 1'b1;
        end
        // Priority 3: High risk without human approval
        else if ((risk_class == RISK_HIGH) && !human_approved) begin
            next_require_human = 1'b1;
            next_log_required  = 1'b1;
        end
        // Priority 4: Battery low and nonessential tool
        else if (battery_low && tool_is_nonessential) begin
            next_block        = 1'b1;
            next_log_required = 1'b1;
        end
        // Priority 5: Emergency mode with safety-critical tool
        else if (emergency_mode && tool_is_safety_critical) begin
            next_allow         = 1'b1;
            next_log_required  = 1'b1;
            next_emergency_path = 1'b1;
        end
        // Priority 6: Default allow
        else begin
            next_allow = 1'b1;
            // Log if offline and medium+ risk
            if (offline_mode && (risk_class >= RISK_MEDIUM)) begin
                next_log_required = 1'b1;
            end
        end
    end

    // =========================================================================
    // Command Processing
    // =========================================================================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // Reset all state
            tool_id        <= 4'd0;
            risk_class     <= 2'd0;
            context_valid  <= 1'b0;
            policy_ok      <= 1'b0;
            human_approved <= 1'b0;
            offline_mode   <= 1'b0;
            battery_low    <= 1'b0;
            emergency_mode <= 1'b0;
            
            allow          <= 1'b0;
            block          <= 1'b0;
            require_human  <= 1'b0;
            log_required   <= 1'b0;
            policy_error   <= 1'b0;
            high_risk      <= 1'b0;
            emergency_path <= 1'b0;
            evaluated      <= 1'b0;
            
            dout           <= 4'd0;
            audit_counter  <= 4'd0;
        end else begin
            // Process write commands
            if (wr_stb) begin
                case (cmd)
                    CMD_NOP: begin
                        // No operation
                    end
                    
                    CMD_LOAD_TOOL_ID: begin
                        tool_id   <= din;
                        evaluated <= 1'b0;  // Clear evaluation on new tool
                    end
                    
                    CMD_LOAD_RISK_CLASS: begin
                        risk_class <= din[1:0];
                        evaluated  <= 1'b0;
                    end
                    
                    CMD_LOAD_FLAGS: begin
                        // din[0] = context_valid
                        // din[1] = policy_ok
                        // din[2] = human_approved
                        // din[3] = offline_mode
                        context_valid  <= din[0];
                        policy_ok      <= din[1];
                        human_approved <= din[2];
                        offline_mode   <= din[3];
                        evaluated      <= 1'b0;
                    end
                    
                    CMD_LOAD_POWER_EMERG: begin
                        // din[0] = battery_low
                        // din[1] = emergency_mode
                        battery_low    <= din[0];
                        emergency_mode <= din[1];
                        evaluated      <= 1'b0;
                    end
                    
                    CMD_EVALUATE: begin
                        // Capture decision outputs
                        allow          <= next_allow;
                        block          <= next_block;
                        require_human  <= next_require_human;
                        log_required   <= next_log_required;
                        policy_error   <= next_policy_error;
                        high_risk      <= next_high_risk;
                        emergency_path <= next_emergency_path;
                        evaluated      <= 1'b1;
                        
                        // Increment audit counter if logging required
                        if (next_log_required) begin
                            audit_counter <= audit_counter + 1'b1;
                        end
                    end
                    
                    CMD_RESET_STATE: begin
                        // Soft reset
                        tool_id        <= 4'd0;
                        risk_class     <= 2'd0;
                        context_valid  <= 1'b0;
                        policy_ok      <= 1'b0;
                        human_approved <= 1'b0;
                        offline_mode   <= 1'b0;
                        battery_low    <= 1'b0;
                        emergency_mode <= 1'b0;
                        
                        allow          <= 1'b0;
                        block          <= 1'b0;
                        require_human  <= 1'b0;
                        log_required   <= 1'b0;
                        policy_error   <= 1'b0;
                        high_risk      <= 1'b0;
                        emergency_path <= 1'b0;
                        evaluated      <= 1'b0;
                        
                        // Note: audit_counter is NOT reset to preserve audit trail
                    end
                    
                    default: begin
                        // Unknown command - ignore
                    end
                endcase
            end
            
            // Process read commands
            if (rd_stb) begin
                case (cmd)
                    CMD_READ_DECISION: begin
                        // Pack decision bits: {require_human, block, allow, evaluated}
                        dout <= {require_human, block, allow, evaluated};
                    end
                    
                    CMD_READ_AUDIT: begin
                        dout <= audit_counter;
                    end
                    
                    default: begin
                        dout <= 4'd0;
                    end
                endcase
            end
        end
    end

endmodule

`default_nettype wire

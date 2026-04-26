/* File: good_example_nd.sv
*
* Company: IC Verimeter
*
* Author: icshunt.help@gmail.com
*
* Date: 2026-03-29
*
* Description: End-to-end NaturalDocs example on SystemVerilog and UVM (documentation / training).
*/

/* Title: SystemVerilog + UVM + NaturalDocs Example
 *
 * Group: Overview
 *   End-to-end example showing NaturalDocs comments attached to
 *   SystemVerilog and UVM constructs.
 *
 * About: License
 *   This file is for documentation and training purposes.
 */

// Group: Includes and Imports
//   Bring in UVM and shared package definitions.

//Macro: timescale
//   Timescale directive.
`timescale 1ns/1ps

// Macro: uvm_macros.svh
//   Makes UVM factory and reporting macros available.
`include "uvm_macros.svh"

// Package: svnd_example_pkg
//   Shared typedefs, enums, structs, unions, and utility tasks/functions.
package svnd_example_pkg;

  //Variable: DefaultTimeout
  //   Default timeout used in testbench waits.
  localparam time DefaultTimeout = 100ns;

  // Typedef: data_t
  //   Common 32-bit data type.
  typedef logic [31:0] data_t;

  // Enum: op_e
  //   Simple transaction operation enumeration.
  typedef enum logic [1:0] {
    OP_IDLE, //  Idle operation.
    OP_READ, // Read operation.
    OP_WRITE // Write operation.
  } op_e;

  // Struct: txn_t
  //   Packed transaction payload.
  typedef struct packed {
    logic [31:0] addr; // Address of the access.
    data_t       data;  // Data associated with the access.
    op_e         op;    // Operation kind.
  } txn_t;

  // Union: raw_data_t
  //   Union representing data as either a 32-bit word or an array of 4 bytes.
  typedef union packed {
    logic [31:0] word;
    logic [3:0][7:0] bytes;
  } raw_data_t;


  // variable: txn_done_ev
  //   Event triggered when a transaction completes.
  event txn_done_ev;

  // Macro: SVND_LOG
  //   Simple logging macro wrapping `uvm_info`.
  `define SVND_LOG(ID, MSG) \
    `uvm_info(ID, MSG, UVM_MEDIUM);

  // Function: parity
  //   Compute XOR parity of a data word.
  function automatic logic parity (input data_t value);

    // Note: Declare local parity accumulator
    logic p;

    // Note: Compute parity via reduction XOR.
    p = ^value;

    // Note: Return computed parity.
    return p;
  endfunction : parity

  // Function: wait_cycles
  //   Wait for a fixed number of rising clock edges.
  task automatic wait_cycles (input int cycles, ref logic clk);
    // Note: Use a for loop with timing control.
    for (int i = 0; i < cycles; i++) begin
      // Note: Wait for next positive edge of clk.
      @(posedge clk);
    end
  endtask : wait_cycles

endpackage : svnd_example_pkg


// Interface: bus_if
//   Simple bus interface with clocking, modports, properties, and covergroups.
interface bus_if (
  input  logic clk, // Variable: clk Bus clock.
  input  logic rst_n // Variable: rst_n Active-low reset.
);

  // Variable: addr
  //   Address bus.
  logic [31:0] addr;

  // Variable: data
  //   Data bus.
  logic [31:0] data;

  // Variable: valid
  //   Indicates a valid transfer.
  logic        valid;

  // Variable: ready
  //   Ready handshake from slave.
  logic        ready;

  // variable: cb
  //   Clocking block for cycle-accurate access.
  clocking cb @(posedge clk);
    // Note: Sample and drive signals via clocking block.
    default input #1step output #1step;
    input  addr, data, valid, ready;
    output addr, data, valid;
  endclocking : cb

  // variable: source_mp
  //   Master-side view of the bus.
  modport source_mp (
    import cb,
    output addr, data, valid,
    input  ready
  );

  // variable: sink_mp
  //   Slave-side view of the bus.
  modport sink_mp (
    import cb,
    input  addr, data, valid,
    output ready
  );

  // function: addr_alignment_chk
  //   Checker block for verifying address alignment rules.
  checker addr_alignment_chk (
    input logic clk,
    input logic rst_n,
    input logic [31:0] addr
);
// function: word_aligned_p
  //   Property ensuring the address is always word-aligned.
  property word_aligned_p;
    @(posedge clk) disable iff (!rst_n)
      (addr[1:0] == 2'b00);
  endproperty: word_aligned_p

  // function: assume_word_aligned_p
  //   Assume the property holds for formal verification.
  assume property (assume_word_aligned_p);

endchecker : addr_alignment_chk

  // function: valid_ready_handshake_p
  //   Once valid is asserted it must be followed by ready within 4 cycles.
  property valid_ready_handshake_p;
    // Note: Use a concurrent property with sequence implication.
    @(posedge clk) disable iff (!rst_n)
      valid |-> ##[1:4] ready;
  endproperty: valid_ready_handshake_p

  //  function: back_to_back_valid_s
  //   Sequence of two consecutive valid cycles.
  sequence back_to_back_valid_s;
    // Note: Two back-to-back cycles of valid.
    valid ##1 valid;
  endsequence: back_to_back_valid_s

  // Note: Assert the handshake property.
  assert property (valid_ready_handshake_p)
    else $error("Handshake failure");

  // Note: Cover the back-to-back valid sequence.
  cover property (back_to_back_valid_s);

  //covergroup: cg_bus
  //   Cover basic bus behavior.
  covergroup cg_bus @(posedge clk);

    // coverpoint: valid
    //   Cover when valid is asserted.
    coverpoint valid;

    // coverpoint: ready
    //   Cover when ready is asserted.
    coverpoint ready;

    // cross: valid, ready
    //   Cover all valid/ready combinations.
    cross valid, ready;
  endgroup : cg_bus

  // Variable: bus_cg
  //   Instantiate covergroup.
  cg_bus bus_cg = new();

endinterface : bus_if

//section: Module DUT

// module: dut
//   Simple DUT showing procedural, continuous, generate, and assertion constructs.
module dut #(
  parameter int WIDTH = 32 // Variable: WIDTH Configurable data width.
)(
  input  logic               clk, // Variable: clk Bus clock.
  input  logic               rst_n, // Variable: rst_n Active-low reset.
  input  logic [31:0]        addr, // Variable: addr Address bus.
  input  logic [WIDTH-1:0]   data_in, // Variable: data_in Data bus.
  output logic [WIDTH-1:0]   data_out, // Variable: data_out Data bus.
  output logic               ready // Variable: ready Ready handshake from slave.
);

  // package: svnd_example_pkg
  //   Use shared types and utilities.
  import svnd_example_pkg::*;

  // Variable: state
  //   Simple FSM state.
  state_e state;

  // Variable: next_state
  //   Next state logic.
  state_e next_state;

  // Variable: reg_data
  //   Internal registered data.
  logic [WIDTH-1:0] reg_data;

  // assign: ready
  // Continuous assignment to drive ready.
  assign ready = (state == DONE);

  // process: initial
  // Initial block for reset initialization.

  initial begin
    state    = IDLE;
    next_state = IDLE;
    reg_data = '0;
  end

  // process: final
  // Final block for end-of-simulation reporting.
  final begin
    $display("DUT final block reached at time %0t", $time);
  end

  // process: always_comb
  // Combinational next-state logic.
  always_comb begin
    next_state = state;
  end

  always_comb begin
    // process: case
    // Use unique case on state.
    unique case (state)
      IDLE: begin
        if (addr != 32'h0) begin
          next_state = BUSY;
        end
      end

      BUSY: begin
        if (addr == 32'h0) begin
          next_state = DONE;
        end
      end

      DONE: begin
        next_state = IDLE;
      end

      default: begin
        next_state = IDLE;
      end
    endcase
  end

  // process: always_ff
  // Sequential logic with async reset.
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      state    <= IDLE;
      reg_data <= '0;
    end
    else begin
      state <= next_state;

      // Note: Nonblocking assignment to reg_data.
      reg_data <= data_in;
    end
  end

  // process: always_latch
  // Simple latch example using always_latch.
  always_latch begin
    if (!rst_n)
      data_out <= '0;
    else if (state == DONE)
      data_out <= reg_data;
  end

  // process: always
  // Generic always block for miscellaneous logic.
  always @(addr or data_in) begin
    assert (addr[1:0] == 2'b00)
      else $warning("Unaligned address %h", addr);
  end

endmodule : dut

//section: Package svnd_uvm_pkg

// Package: svnd_uvm_pkg
//   UVM components using SystemVerilog OOP features.
package svnd_uvm_pkg;

  // package: uvm_pkg
  //   Standard UVM package.
  import uvm_pkg::*;

  // package: svnd_example_pkg
  //   Shared transaction types.
  import svnd_example_pkg::*;

//Section: Class svnd_transaction
  // Class: svnd_transaction
  //   UVM sequence item representing a bus transaction.
  class svnd_transaction extends uvm_sequence_item;

    // Variable: m_addr
    //   Transaction m_address.
    rand logic [31:0] m_addr;

    // Variable: m_data
    //   Transaction m_data.
    rand data_t       m_data;

    // Variable: m_op
    //   Transaction operation.
    rand op_e         m_op;

   // Variable: m_id
    //   Cyclic random transaction ID.
    randc logic [7:0] m_id;

    // Constraint: addr_align_c
    //   Keep addresses word aligned.
    constraint addr_align_c {
      addr[1:0] == 2'b00;
      }

    // Function: new
    //   Object constructor.
    function new(string name = "svnd_transaction");
      super.new(name);
    endfunction : new

    // Function: do_copy
    //   Standard UVM copy implementation.
    function void do_copy(uvm_object rhs);
      svnd_transaction rhs_txn;
      if (!$cast(rhs_txn, rhs)) return;
      addr = rhs_txn.addr;
      data = rhs_txn.data;
      op   = rhs_txn.op;
    endfunction : do_copy

    // Function: convert2string
    //   Human-readable representation.
    function string convert2string();
      return $sformatf("addr=%h data=%h op=%0d", addr, data, op);
    endfunction : convert2string

  endclass : svnd_transaction

  // Section: Class svnd_driver

  // Class: svnd_driver
  //   Simple UVM driver using a virtual interface.
  class svnd_driver extends uvm_driver #(svnd_transaction);

    // UVM_Macro: uvm_component_utils
    //   UVM factory registration macro.
    `uvm_component_utils(svnd_driver)

    // Variable: vif
    //   Virtual interface handle.
    virtual bus_if.master_mp_vif vif;

    // Function: new
    function new(string name, uvm_component parent);
      super.new(name, parent);
    endfunction : new

    // Function: run_phase
    //   Main driver loop.
    task run_phase(uvm_phase phase);
      svnd_transaction tr;

      forever begin

        // Note: Get next item from sequencer.
        seq_item_port.get_next_item(tr);

        // Note: Drive one transaction.
        drive_txn(tr);

        // Note: Indicate item is done.
        seq_item_port.item_done();

        // Note: Trigger transaction-done event.
        -> svnd_example_pkg::txn_done_ev;
      end

    endtask : run_phase

    // Function: drive_txn
    //   Drive a single transaction on the bus.
    task automatic drive_txn(svnd_transaction tr);
      // Note: Apply addr and data and toggle valid.
      vif.cb.addr  <= tr.addr;
      vif.cb.data  <= tr.data;
      vif.cb.valid <= 1'b1;

      // Note: Wait until ready is asserted.
      wait (vif.cb.ready == 1'b1);

      // Note: Deassert valid.
      vif.cb.valid <= 1'b0;
    endtask : drive_txn

  endclass : svnd_driver

//Section: Class svnd_env

  // Class: svnd_env
  //   UVM environment containing the driver.
  class svnd_env extends uvm_env;

    // Variable: m_driver
    //   Driver instance.
    svnd_driver m_driver;

    // UVM_Macro: uvm_component_utils
    //   UVM factory registration macro.
    `uvm_component_utils(svnd_env)

    // Function: new
    function new(string name, uvm_component parent);
      super.new(name, parent);
    endfunction : new

    // Function: build_phase
    //   Construct environment components.
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      driver = svnd_driver::type_id::create("driver", this);
    endfunction : build_phase

  endclass : svnd_env

endpackage : svnd_uvm_pkg

//Section: Module tb_top

// module: tb_top
//   Top-level testbench module instantiating DUT, interfaces, and starting UVM.
module tb_top;

  // Variable: clk
  //   System clock.
  logic clk;

  // Variable: rst_n
  //   Active-low reset.
  logic rst_n;

  //Variable: bus_if_i
  //   Instantiate bus interface.
  bus_if bus_if_i (
    .clk  (clk),
    .rst_n(rst_n)
  );

  // Variable: dut_i
  //   Instantiate DUT.
  dut #(.WIDTH(32)) dut_i (
    .clk     (clk),
    .rst_n   (rst_n),
    .addr    (bus_if_i.addr),
    .data_in (bus_if_i.data),
    .data_out(),
    .ready   (bus_if_i.ready)
  );

// Variable: align_chk_i
//   Bind the address alignment checker to the DUT instance.
bind dut addr_alignment_chk align_chk_i (
  .clk(clk),
  .rst_n(rst_n),
  .addr(addr)
);

  // program: test_prog
  // Simple test program driving transactions into the sequencer.
  program automatic test_prog(bus_if.master_mp m_if);

    // Note: Use initial block inside program.
    initial begin
      // Note: Test bench logic.
      $display("Test program started at %0t", $time);

      // Note: Trigger end-of-test manually.
      $display("Test program finished at %0t", $time);
    end
  endprogram : test_prog

  // Variable: test_prog_i
  //   Connect test program to interface.
  test_prog test_prog_i(bus_if_i.master_mp);

  // Note: Clock generation.
  initial begin
    clk = 1'b0;
    forever #5 clk = ~clk;
  end

  // Note: Reset generation.
  initial begin
    rst_n = 1'b0;
    #20 rst_n = 1'b1;
  end

  // Note: Start UVM test.
  initial begin
    // Note: Set virtual interface via config DB.
    uvm_config_db#(virtual bus_if.master_mp)::set(null, "*", "vif", bus_if_i.source_mp);
    run_test();
  end

endmodule : tb_top

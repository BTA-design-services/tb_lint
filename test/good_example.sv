/*******************************************************************************
 * File: good_example.sv
 *
 * Company: BTA Design Services
 *
 * Author: vbesyakov@btadesignservices.com
 *
 * Description: Example SystemVerilog file with correct NaturalDocs documentation
 *              This file demonstrates proper documentation for all constructs
 *              and passes all naturaldocs_lint.py checks.
 *
 * Created: October 2, 2025
 ******************************************************************************/

`ifndef GOOD_EXAMPLE_SV
`define GOOD_EXAMPLE_SV

//Package: bta_example_pkg
//Example package demonstrating correct NaturalDocs documentation.
//This package contains properly documented classes, functions, tasks,
//and constraints that comply with BTA coding standards.
package bta_example_pkg;

  // Import UVM
  import uvm_pkg::*;
  `include "uvm_macros.svh"

  //Group: Type Definitions

  //Typedef: state_t
  //State machine enumeration type for agent states
  typedef enum {
    IDLE_t,
    ACTIVE_t,
    WAIT_t,
    DONE_t
  } state_t;

  //Typedef: addr_t
  //Address type for memory operations
  typedef logic [31:0] addr_t;

  //Typedef: data_t
  //Data type for transactions
  typedef logic [63:0] data_t;

  //Group: Configuration Classes

  //Class: bta_config_c
  //Configuration class for the verification environment.
  //Contains all configuration parameters for the testbench components.
  class bta_config_c extends uvm_object;
    `uvm_object_utils(bta_config_c)

    //Group: Configuration Parameters

    //Variable: m_num_transactions
    //Number of transactions to generate
    rand int m_num_transactions;

    //Variable: m_timeout_cycles
    //Timeout value in clock cycles
    rand int m_timeout_cycles;

    //Variable: m_enable_coverage
    //Enable functional coverage collection
    bit m_enable_coverage;

    //Variable: m_verbosity
    //UVM verbosity level for reporting
    uvm_verbosity m_verbosity;

    //Group: Constraints

    //define: num_transactions_c
    //Constrains number of transactions to reasonable range
    constraint num_transactions_c {
      m_num_transactions inside {[1:1000]};
      m_num_transactions > 0;
    }

    //define: timeout_cycles_c
    //Constrains timeout to prevent simulation hangs
    constraint timeout_cycles_c {
      m_timeout_cycles inside {[100:10000]};
      m_timeout_cycles > m_num_transactions;
    }

    //Group: Methods

    //Function: new
    //Constructor for configuration object
    //
    //Parameters:
    //  name - Object name for UVM factory
    function new(string name = "bta_config_c");
      super.new(name);
      m_enable_coverage = 1;
      m_verbosity = UVM_MEDIUM;
    endfunction : new

    //Function: do_print
    //UVM print method override
    //
    //Parameters:
    //  printer - UVM printer object
    virtual function void do_print(uvm_printer printer);
      super.do_print(printer);
      printer.print_field_int("m_num_transactions", m_num_transactions, $bits(m_num_transactions));
      printer.print_field_int("m_timeout_cycles", m_timeout_cycles, $bits(m_timeout_cycles));
      printer.print_field_int("m_enable_coverage", m_enable_coverage, 1);
    endfunction : do_print

  endclass : bta_config_c

  //Group: Transaction Classes

  //Class: bta_transaction_c
  //Base transaction class for protocol transactions.
  //Contains address, data, and control fields.
  class bta_transaction_c extends uvm_sequence_item;
    `uvm_object_utils(bta_transaction_c)

    //Group: Transaction Fields

    //Variable: m_addr
    //Transaction address
    rand addr_t m_addr;

    //Variable: m_data
    //Transaction data payload
    rand data_t m_data;

    //Variable: m_write
    //Write enable (1=write, 0=read)
    rand bit m_write;

    //Variable: m_valid
    //Transaction valid signal
    bit m_valid;

    //Variable: m_timestamp
    //Transaction timestamp in simulation time
    time m_timestamp;

    //Group: Constraints

    //define: addr_range_c
    //Constrains address to valid memory range
    constraint addr_range_c {
      m_addr inside {[32'h1000:32'h1FFF]};
      m_addr[1:0] == 2'b00;  // Word aligned
    }

    //define: data_non_zero_c
    //Constrains data to non-zero for testing
    constraint data_non_zero_c {
      m_data != 0;
    }

    //Group: Methods

    //Function: new
    //Constructor for transaction object
    //
    //Parameters:
    //  name - Object name for UVM factory
    function new(string name = "bta_transaction_c");
      super.new(name);
      m_valid = 0;
      m_timestamp = 0;
    endfunction : new

    //Function: do_copy
    //UVM copy method override
    //
    //Parameters:
    //  rhs - Right-hand side object to copy from
    virtual function void do_copy(uvm_object rhs);
      bta_transaction_c rhs_trans;
      super.do_copy(rhs);
      if (!$cast(rhs_trans, rhs)) begin
        `uvm_fatal("CAST", "Failed to cast rhs object")
      end
      m_addr = rhs_trans.m_addr;
      m_data = rhs_trans.m_data;
      m_write = rhs_trans.m_write;
      m_valid = rhs_trans.m_valid;
      m_timestamp = rhs_trans.m_timestamp;
    endfunction : do_copy

    //Function: do_compare
    //UVM compare method override
    //
    //Parameters:
    //  rhs - Right-hand side object to compare with
    //  comparer - UVM comparer object
    //
    //Returns:
    //  1 if objects match, 0 otherwise
    virtual function bit do_compare(uvm_object rhs, uvm_comparer comparer);
      bta_transaction_c rhs_trans;
      if (!$cast(rhs_trans, rhs)) return 0;
      return (super.do_compare(rhs, comparer) &&
              (m_addr == rhs_trans.m_addr) &&
              (m_data == rhs_trans.m_data) &&
              (m_write == rhs_trans.m_write));
    endfunction : do_compare

    //Function: convert2string
    //Convert transaction to string for printing
    //
    //Returns:
    //  String representation of transaction
    virtual function string convert2string();
      return $sformatf("addr=0x%08h data=0x%016h write=%0b valid=%0b",
                       m_addr, m_data, m_write, m_valid);
    endfunction : convert2string

  endclass : bta_transaction_c

  //Group: Sequence Classes

  //Class: bta_sequence_c
  //Base sequence class for generating transactions.
  //Generates a configurable number of random transactions.
  class bta_sequence_c extends uvm_sequence #(bta_transaction_c);
    `uvm_object_utils(bta_sequence_c)

    //Group: Sequence Parameters

    //Variable: m_num_items
    //Number of transactions to generate
    rand int m_num_items;

    //Group: Constraints

    //define: num_items_range_c
    //Constrains sequence length to reasonable range
    constraint num_items_range_c {
      m_num_items inside {[1:100]};
    }

    //Group: Methods

    //Function: new
    //Constructor for sequence object
    //
    //Parameters:
    //  name - Object name for UVM factory
    function new(string name = "bta_sequence_c");
      super.new(name);
      m_num_items = 10;
    endfunction : new

    //Function: body
    //Main sequence body that generates transactions.
    //Creates and randomizes the specified number of transactions.
    virtual task body();
      bta_transaction_c trans;

      `uvm_info(get_type_name(),
                $sformatf("Starting sequence with %0d transactions", m_num_items),
                UVM_MEDIUM)

      for (int i = 0; i < m_num_items; i++) begin
        trans = bta_transaction_c::type_id::create($sformatf("trans_%0d", i));
        start_item(trans);
        if (!trans.randomize()) begin
          `uvm_error(get_type_name(), "Failed to randomize transaction")
        end
        finish_item(trans);
      end

      `uvm_info(get_type_name(), "Sequence completed", UVM_MEDIUM)
    endtask : body

  endclass : bta_sequence_c

  //Group: Driver Classes

  //Class: bta_driver_c
  //Driver component that converts transactions to pin wiggles.
  //Implements the UVM driver interface for the protocol.
  class bta_driver_c extends uvm_driver #(bta_transaction_c);
    `uvm_component_utils(bta_driver_c)

    //Group: Configuration

    //Variable: m_config
    //Configuration object reference
    bta_config_c m_config;

    //Group: Internal State

    //Variable: m_current_state
    //Current state of the driver FSM
    state_t m_current_state;

    //Variable: m_cycle_count
    //Cycle counter for timing
    int m_cycle_count;

    //Group: Methods

    //Function: new
    //Constructor for driver component
    //
    //Parameters:
    //  name - Component name
    //  parent - Parent component
    function new(string name = "bta_driver_c", uvm_component parent = null);
      super.new(name, parent);
      m_current_state = IDLE_t;
      m_cycle_count = 0;
    endfunction : new

    //Function: build_phase
    //UVM build phase - get configuration
    //
    //Parameters:
    //  phase - UVM phase object
    virtual function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db#(bta_config_c)::get(this, "", "config", m_config)) begin
        `uvm_info(get_type_name(), "Using default configuration", UVM_MEDIUM)
        m_config = bta_config_c::type_id::create("m_config");
      end
    endfunction : build_phase

    //Function: run_phase
    //UVM run phase - main driver execution
    //
    //Parameters:
    //  phase - UVM phase object
    virtual task run_phase(uvm_phase phase);
      bta_transaction_c trans;

      `uvm_info(get_type_name(), "Driver starting", UVM_MEDIUM)

      forever begin
        seq_item_port.get_next_item(trans);
        drive_transaction(trans);
        seq_item_port.item_done();
      end
    endtask : run_phase

    //Function: drive_transaction
    //Drive a single transaction on the interface
    //
    //Parameters:
    //  trans - Transaction to drive
    virtual task drive_transaction(bta_transaction_c trans);
      `uvm_info(get_type_name(),
                $sformatf("Driving transaction: %s", trans.convert2string()),
                UVM_HIGH)

      m_current_state = ACTIVE_t;

      // Simulate driving the transaction
      repeat (trans.m_write ? 1 : 2) @(posedge /* clk signal would go here */);

      m_cycle_count++;
      m_current_state = IDLE_t;
    endtask : drive_transaction

  endclass : bta_driver_c

  //Group: Monitor Classes

  //Class: bta_monitor_c
  //Monitor component that observes pin activity and creates transactions.
  //Implements protocol monitoring and coverage collection.
  class bta_monitor_c extends uvm_monitor;
    `uvm_component_utils(bta_monitor_c)

    //Group: Analysis Ports

    //Variable: m_analysis_port
    //Analysis port for broadcasting observed transactions
    uvm_analysis_port #(bta_transaction_c) m_analysis_port;

    //Group: Configuration

    //Variable: m_config
    //Configuration object reference
    bta_config_c m_config;

    //Group: Statistics

    //Variable: m_transaction_count
    //Total number of transactions observed
    int m_transaction_count;

    //Group: Methods

    //Function: new
    //Constructor for monitor component
    //
    //Parameters:
    //  name - Component name
    //  parent - Parent component
    function new(string name = "bta_monitor_c", uvm_component parent = null);
      super.new(name, parent);
      m_transaction_count = 0;
    endfunction : new

    //Function: build_phase
    //UVM build phase - create analysis port
    //
    //Parameters:
    //  phase - UVM phase object
    virtual function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      m_analysis_port = new("m_analysis_port", this);
      if (!uvm_config_db#(bta_config_c)::get(this, "", "config", m_config)) begin
        `uvm_info(get_type_name(), "Using default configuration", UVM_MEDIUM)
        m_config = bta_config_c::type_id::create("m_config");
      end
    endfunction : build_phase

    //Function: run_phase
    //UVM run phase - main monitor execution
    //
    //Parameters:
    //  phase - UVM phase object
    virtual task run_phase(uvm_phase phase);
      bta_transaction_c trans;

      `uvm_info(get_type_name(), "Monitor starting", UVM_MEDIUM)

      forever begin
        trans = bta_transaction_c::type_id::create("observed_trans");
        collect_transaction(trans);
        m_analysis_port.write(trans);
        m_transaction_count++;
      end
    endtask : run_phase

    //Function: collect_transaction
    //Collect a transaction from the interface
    //
    //Parameters:
    //  trans - Transaction object to fill with observed data
    virtual task collect_transaction(bta_transaction_c trans);
      // Simulate collecting transaction data
      @(posedge /* clk signal would go here */);
      trans.m_timestamp = $time;
      trans.m_valid = 1;
    endtask : collect_transaction

    //Function: report_phase
    //UVM report phase - print statistics
    //
    //Parameters:
    //  phase - UVM phase object
    virtual function void report_phase(uvm_phase phase);
      super.report_phase(phase);
      `uvm_info(get_type_name(),
                $sformatf("Monitor observed %0d transactions", m_transaction_count),
                UVM_LOW)
    endfunction : report_phase

  endclass : bta_monitor_c

endpackage : bta_example_pkg

`endif // GOOD_EXAMPLE_SV


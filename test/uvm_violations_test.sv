// File: uvm_violations_test.sv
// Company: BTA Design Services
// This file INTENTIONALLY violates UVM-related Verible lint rules
// WARNING: This is a BAD example - do NOT use as reference!
//
// Note: Simplified to avoid UVM macro expansion issues with static analysis

package uvm_violations_pkg;

  // Mock UVM base classes (simplified for linting)
  class uvm_object;
    function new(string name = "uvm_object");
    endfunction
    static function uvm_object type_id_create(string name);
      return null;
    endfunction
  endclass

  class uvm_component;
    function new(string name, uvm_component parent = null);
    endfunction
    static function uvm_component type_id_create(string name, uvm_component parent);
      return null;
    endfunction
  endclass

  class uvm_sequence_item extends uvm_object;
    function new(string name = "uvm_sequence_item");
      super.new(name);
    endfunction
  endclass

  // ==========================================================================
  // VIOLATION: create-object-name-match
  // The name in type_id::create() must match the variable name
  // ==========================================================================

  class my_transaction extends uvm_sequence_item;
    rand bit [7:0] data;
    rand bit [3:0] addr;

    function new(string name = "my_transaction");
      super.new(name);
    endfunction

    static function my_transaction type_id_create(string name);
      my_transaction obj = new(name);
      return obj;
    endfunction
  endclass

  // ==========================================================================
  // VIOLATION: create-object-name-match
  // Variable name is 'trans' but create uses "wrong_name"
  // ==========================================================================

  class my_sequence;

    function new(string name = "my_sequence");
    endfunction

    task body();
      my_transaction trans;
      // VIOLATION: "wrong_name" doesn't match variable name "trans"
      trans = my_transaction::type_id_create("wrong_name");
    endtask
  endclass

  // ==========================================================================
  // VIOLATION: create-object-name-match - multiple instances
  // ==========================================================================

  class my_driver extends uvm_component;

    function new(string name = "my_driver", uvm_component parent = null);
      super.new(name, parent);
    endfunction

    static function my_driver type_id_create(string name, uvm_component parent);
      my_driver obj = new(name, parent);
      return obj;
    endfunction

    task run_phase();
      my_transaction req;
      my_transaction rsp;

      // VIOLATION: "bad_response_name" doesn't match "rsp"
      rsp = my_transaction::type_id_create("bad_response_name");

      // VIOLATION: "another_wrong_name" doesn't match "req"
      req = my_transaction::type_id_create("another_wrong_name");
    endtask
  endclass

  // ==========================================================================
  // VIOLATION: create-object-name-match in build_phase
  // ==========================================================================

  class my_monitor extends uvm_component;

    function new(string name = "my_monitor", uvm_component parent = null);
      super.new(name, parent);
    endfunction

    static function my_monitor type_id_create(string name, uvm_component parent);
      my_monitor obj = new(name, parent);
      return obj;
    endfunction
  endclass

  class my_agent extends uvm_component;

    my_driver  drv;
    my_monitor mon;

    function new(string name = "my_agent", uvm_component parent = null);
      super.new(name, parent);
    endfunction

    static function my_agent type_id_create(string name, uvm_component parent);
      my_agent obj = new(name, parent);
      return obj;
    endfunction

    function void build_phase();
      // VIOLATION: "driver_instance" doesn't match "drv"
      drv = my_driver::type_id_create("driver_instance", this);

      // VIOLATION: "monitor_inst" doesn't match "mon"
      mon = my_monitor::type_id_create("monitor_inst", this);
    endfunction
  endclass

  // ==========================================================================
  // VIOLATION: create-object-name-match in test
  // ==========================================================================

  class my_env extends uvm_component;
    my_agent agent;

    function new(string name = "my_env", uvm_component parent = null);
      super.new(name, parent);
    endfunction

    static function my_env type_id_create(string name, uvm_component parent);
      my_env obj = new(name, parent);
      return obj;
    endfunction

    function void build_phase();
      // VIOLATION: "my_agent_inst" doesn't match "agent"
      agent = my_agent::type_id_create("my_agent_inst", this);
    endfunction
  endclass

  class my_test extends uvm_component;

    my_env       env;
    my_sequence  seq;

    function new(string name = "my_test", uvm_component parent = null);
      super.new(name, parent);
    endfunction

    static function my_test type_id_create(string name, uvm_component parent);
      my_test obj = new(name, parent);
      return obj;
    endfunction

    function void build_phase();
      // VIOLATION: "test_env" doesn't match "env"
      env = my_env::type_id_create("test_env", this);
    endfunction

    task run_phase();
      // VIOLATION: "main_sequence" doesn't match "seq"
      seq = my_sequence::new("main_sequence");
    endtask
  endclass

  // ==========================================================================
  // VIOLATION: explicit-parameter-storage-type
  // Parameters in UVM classes should have explicit types
  // ==========================================================================

  class param_test_class extends uvm_object;

    // VIOLATION: parameter without explicit type
    parameter NO_TYPE = 10;

    // VIOLATION: parameter name not uppercase
    parameter int bad_param_name = 20;

    function new(string name = "param_test_class");
      super.new(name);
    endfunction
  endclass

  // ==========================================================================
  // VIOLATION: explicit-function-task-parameter-type
  // Function/task parameters should have explicit types
  // ==========================================================================

  class function_param_test extends uvm_component;

    function new(string name = "function_param_test", uvm_component parent = null);
      super.new(name, parent);
    endfunction

    // VIOLATION: parameter 'data' has no explicit type
    function void process_data(data);
      $display("Data: %0d", data);
    endfunction

    // VIOLATION: parameter 'value' has no explicit type
    task send_transaction(value);
      #10;
      $display("Sent: %0d", value);
    endtask

    // VIOLATION: parameter 'addr' has no explicit type
    function bit check_address(addr);
      return (addr < 1024);
    endfunction
  endclass

  // ==========================================================================
  // Additional parameter violations
  // ==========================================================================

  class config_class extends uvm_object;

    // VIOLATION: Multiple parameters on one line
    parameter int PARAM1 = 1, PARAM2 = 2;

    // VIOLATION: Parameter without type
    parameter DEFAULT_VALUE = 100;

    function new(string name = "config_class");
      super.new(name);
    endfunction
  endclass

  // ==========================================================================
  // Example of CORRECT UVM patterns (for reference)
  // ==========================================================================

  class correct_example extends uvm_component;

    my_driver correct_drv;

    function new(string name = "correct_example", uvm_component parent = null);
      super.new(name, parent);
    endfunction

    static function correct_example type_id_create(string name, uvm_component parent);
      correct_example obj = new(name, parent);
      return obj;
    endfunction

    function void build_phase();
      // CORRECT: "correct_drv" matches variable name
      correct_drv = my_driver::type_id_create("correct_drv", this);
    endfunction

    // CORRECT: Explicit parameter types
    function void correct_function(int data, bit [7:0] addr);
      $display("Data: %0d, Addr: %0h", data, addr);
    endfunction
  endclass

endpackage

// Top-level module
module top;
  initial begin
    $display("UVM Violations Test");
  end
endmodule

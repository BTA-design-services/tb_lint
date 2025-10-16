//File: keyword_test.sv
//Test file for keyword validation

`ifndef KEYWORD_TEST_SV
`define KEYWORD_TEST_SV

//Package: test_pkg
package test_pkg;

  //Task: bad_task  // ❌ Invalid - should be Function
  task bad_task();
  endtask : bad_task

  //Member: m_data  // ❌ Invalid - should be Variable
  int m_data;

  //Component: test_class  // ❌ Invalid - should be Class
  class test_class;

    //Parameter: WIDTH  // ❌ Invalid - should be Constant
    parameter int WIDTH = 32;

    //Constraint: range_c  // ❌ Invalid - should be define
    constraint range_c {
      m_data inside {[0:100]};
    }

  endclass : test_class

  //Function: good_function  // ✅ Valid
  function int good_function();
    return 42;
  endfunction : good_function

  //Variable: m_count  // ✅ Valid
  int m_count;

endpackage : test_pkg

`endif // KEYWORD_TEST_SV


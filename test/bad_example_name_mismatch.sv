/*******************************************************************************
 * File: bad_example_name_mismatch.sv
 *
 * Company: BTA Design Services
 *
 * Author: vbesyakov@btadesignservices.com
 *
 * Description: Comprehensive test file for [ND_NAME_MISMATCH] violations.
 *              Every NaturalDocs-documented AST declaration type is exercised
 *              with an intentionally wrong documented name.
 *              Expected: one [ND_NAME_MISMATCH] per mismatch block.
 *
 * Created: March 25, 2026
 ******************************************************************************/

`ifndef BAD_EXAMPLE_NAME_MISMATCH_SV
`define BAD_EXAMPLE_NAME_MISMATCH_SV

// ============================================================================
// 1. Package mismatch  (kPackageDeclaration / package_docs.py)
// ============================================================================

//Package: wrong_pkg
//Intentional mismatch -- documented as wrong_pkg, actual is mismatch_test_pkg
package mismatch_test_pkg;

  import uvm_pkg::*;
  `include "uvm_macros.svh"

  // ==========================================================================
  // 2. Typedef enum mismatch  (kTypeDeclaration / typedef_docs.py)
  // ==========================================================================

  //Typedef: wrong_enum_t
  //Intentional mismatch
  typedef enum {A_t, B_t, C_t} actual_enum_t;

  // ==========================================================================
  // 3. Typedef simple mismatch  (kTypeDeclaration / typedef_docs.py, Type alias)
  // ==========================================================================

  //Type: wrong_data_t
  //Intentional mismatch with Type keyword
  typedef logic [31:0] actual_data_t;

  // ==========================================================================
  // 4. Typedef with Variable alias  (edge case)
  // ==========================================================================

  //Variable: wrong_addr_t
  //Intentional mismatch with Variable keyword on typedef
  typedef logic [15:0] actual_addr_t;

  // ==========================================================================
  // 5. Class mismatch  (kClassDeclaration / class_docs.py)
  // ==========================================================================

  //Class: wrong_class_c
  //Intentional mismatch
  class actual_class_c extends uvm_object;
    `uvm_object_utils(actual_class_c)

    //Group: Members

    // ========================================================================
    // 6. Variable (member) mismatch  (kDataDeclaration / variable_docs.py)
    // ========================================================================

    //Variable: m_wrong_var
    //Intentional mismatch
    int m_actual_var;

    // ========================================================================
    // 7. Parameter mismatch  (kParamDeclaration / parameter_docs.py)
    // ========================================================================

    //Variable: WRONG_PARAM
    //Intentional mismatch on parameter
    parameter int ACTUAL_PARAM = 42;

    // ========================================================================
    // 8. Localparam mismatch  (kParamDeclaration / parameter_docs.py)
    // ========================================================================

    //Variable: WRONG_LP
    //Intentional mismatch
    localparam int ACTUAL_LP = 99;

    // ========================================================================
    // 9. Constraint mismatch  (kConstraintDeclaration / constraint_docs.py)
    // ========================================================================

    //define: wrong_range_c
    //Intentional mismatch
    constraint actual_range_c {
      m_actual_var inside {[0:100]};
    }

    // ========================================================================
    // 10. Covergroup mismatch  (kCovergroupDeclaration / covergroup_docs.py)
    // ========================================================================

    //Variable: wrong_cg
    //Intentional mismatch
    covergroup actual_cg;
      option.per_instance = 1;
    endgroup : actual_cg

    // ========================================================================
    // 11. Function impl mismatch  (kFunctionDeclaration / function_docs.py)
    // ========================================================================

    //Function: wrong_build
    //Intentional mismatch
    function void actual_build();
    endfunction : actual_build

    // ========================================================================
    // 12. Constructor mismatch  (kClassConstructorPrototype / function_docs.py)
    // ========================================================================

    //Function: wrong_new
    //Intentional mismatch on constructor
    function new(string name = "actual_class_c");
      super.new(name);
    endfunction : new

    // ========================================================================
    // 13. Function prototype mismatch  (kFunctionPrototype / function_docs.py)
    // ========================================================================

    //Function: wrong_proto_fn
    //Intentional mismatch on extern prototype
    extern function void actual_proto_fn();

    // ========================================================================
    // 14. Task impl mismatch  (kTaskDeclaration / task_docs.py)
    // ========================================================================

    //Function: wrong_run
    //Intentional mismatch on task
    task actual_run();
    endtask : actual_run

    // ========================================================================
    // 15. Task prototype mismatch  (kTaskPrototype / task_docs.py)
    // ========================================================================

    //Function: wrong_task_proto
    //Intentional mismatch on extern task prototype
    extern task actual_task_proto();

    // ========================================================================
    // 16. Task with Method alias  (edge case)
    // ========================================================================

    //Method: wrong_method_task
    //Intentional mismatch with Method keyword on task
    task actual_method_task();
    endtask : actual_method_task

    // ========================================================================
    // 17. Task with Procedure alias  (edge case)
    // ========================================================================

    //Procedure: wrong_proc_task
    //Intentional mismatch with Procedure keyword on task
    task actual_proc_task();
    endtask : actual_proc_task

  endclass : actual_class_c

  // ==========================================================================
  // Function prototype implementation (required for extern)
  // ==========================================================================

  //Function: actual_proto_fn
  //Implementation of the extern prototype
  function void actual_class_c::actual_proto_fn();
  endfunction : actual_proto_fn

  // ==========================================================================
  // Task prototype implementation (required for extern)
  // ==========================================================================

  //Function: actual_task_proto
  //Implementation of the extern task prototype
  task actual_class_c::actual_task_proto();
  endtask : actual_task_proto

  // ==========================================================================
  // NEGATIVE CONTROL: correct name (should NOT trigger mismatch)
  // ==========================================================================

  //Class: correct_class_c
  //Name matches -- no mismatch expected
  class correct_class_c extends uvm_object;
    `uvm_object_utils(correct_class_c)

    //Function: new
    //Constructor
    function new(string name = "correct_class_c");
      super.new(name);
    endfunction : new

    //Function: do_work
    //Correctly documented function
    function void do_work();
      // NEGATIVE CONTROL: local variable -- variable_docs skips locals
      //Variable: wrong_local
      int actual_local;
      actual_local = 1;
    endfunction : do_work

  endclass : correct_class_c

endpackage : mismatch_test_pkg

// ============================================================================
// 18. Module mismatch  (kModuleDeclaration / module_docs.py)
// ============================================================================

//Module: wrong_module
//Intentional mismatch
module actual_module;
endmodule : actual_module

// ============================================================================
// 19. Interface mismatch  (kInterfaceDeclaration / interface_docs.py)
// ============================================================================

//Interface: wrong_iface
//Intentional mismatch
interface actual_iface;
endinterface : actual_iface

`endif // BAD_EXAMPLE_NAME_MISMATCH_SV

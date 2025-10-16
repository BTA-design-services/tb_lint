/*
File: wrong_keywords_example.sv
Company: BTA Design Services
Author: Example Author <example@btadesignservices.com>
Description: Examples of WRONG keyword usage for NaturalDocs linter testing
*/

`ifndef WRONG_KEYWORDS_EXAMPLE_SV
`define WRONG_KEYWORDS_EXAMPLE_SV

//===================================================================
// SECTION 1: Invalid Keywords (Not in NaturalDocs Spec)
//===================================================================

//NotAKeyword: bta_invalid_pkg
//This will be flagged as INVALID
package bta_invalid_pkg;

  //MyCustomKeyword: custom_type_t
  //ERROR: Not a valid NaturalDocs keyword
  typedef logic [15:0] custom_type_t;

  //Random: bta_invalid_class
  //ERROR: "Random" is not a NaturalDocs keyword
  class bta_invalid_class;

    //Something: m_data
    //ERROR: "Something" is not a NaturalDocs keyword
    rand bit [31:0] m_data;

    //Constructor: new
    //ERROR: "Constructor" is not a NaturalDocs keyword (use Function)
    function new(string name = "");
    endfunction : new

  endclass : bta_invalid_class

endpackage : bta_invalid_pkg

//===================================================================
// SECTION 2: Wrong Keywords for Declaration Type
//===================================================================

//Variable: bta_wrong_pkg
//ERROR: "Variable" is wrong for package (expected Package/Namespace)
package bta_wrong_pkg;

  //Function: addr_t
  //ERROR: "Function" is wrong for typedef (expected Typedef/Type)
  typedef logic [31:0] addr_t;

  //Typedef: state_t
  //CORRECT: This is the right keyword for enum typedef
  typedef enum {IDLE, ACTIVE, DONE} state_t;

  //Variable: bta_wrong_class
  //ERROR: "Variable" is wrong for class (expected Class/Struct)
  class bta_wrong_class;

    //Class: m_counter
    //ERROR: "Class" is wrong for variable (expected Variable/Member/Field)
    int m_counter;

    //Typedef: get_count
    //ERROR: "Typedef" is wrong for function (expected Function/Method)
    function int get_count();
      return m_counter;
    endfunction : get_count

    //Variable: increment
    //ERROR: "Variable" is wrong for task (expected Function/Method)
    task increment();
      m_counter++;
    endtask : increment

    //Function: valid_range_c
    //ERROR: "Function" is wrong for constraint (expected define:)
    constraint valid_range_c {
      m_counter inside {[0:100]};
    }

  endclass : bta_wrong_class

endpackage : bta_wrong_pkg

//===================================================================
// SECTION 3: Using "Task" Keyword (Not Valid)
//===================================================================

//Package: bta_task_keyword_pkg
package bta_task_keyword_pkg;

  //Class: bta_test_class
  class bta_test_class;

    //Task: my_task
    //ERROR: NaturalDocs doesn't have "Task" keyword - use "Function"
    task my_task();
      // Do something
    endtask : my_task

    //Task: another_task
    //ERROR: Again, should be "Function"
    task another_task(int value);
      // Do something else
    endtask : another_task

  endclass : bta_test_class

endpackage : bta_task_keyword_pkg

//===================================================================
// SECTION 4: Mixed Correct and Wrong
//===================================================================

//Package: bta_mixed_pkg
//CORRECT: Package is the right keyword
package bta_mixed_pkg;

  //Type: byte_t
  //CORRECT: "Type" is an alias for Typedef
  typedef logic [7:0] byte_t;

  //Module: bta_mixed_class
  //ERROR: "Module" is not a valid NaturalDocs keyword for classes
  class bta_mixed_class;

    //Field: m_id
    //CORRECT: "Field" is valid for variables
    int m_id;

    //Procedure: set_id
    //CORRECT: "Procedure" is valid for functions
    function void set_id(int id);
      m_id = id;
    endfunction : set_id

    //Operation: reset
    //ERROR: "Operation" is not a valid NaturalDocs keyword
    task reset();
      m_id = 0;
    endtask : reset

    //Constraint: id_range_c
    //ERROR: Should use "define:" not "Constraint:"
    constraint id_range_c {
      m_id inside {[1:100]};
    }

    //define: valid_id_c
    //CORRECT: Constraints must use "define:" (lowercase)
    constraint valid_id_c {
      m_id != 0;
    }

  endclass : bta_mixed_class

endpackage : bta_mixed_pkg

//===================================================================
// SECTION 5: Case Sensitivity Issues
//===================================================================

//package: bta_case_pkg
//ERROR: Lowercase "package" is not recognized
package bta_case_pkg;

  //class: bta_case_class
  //ERROR: Lowercase "class" is not recognized
  class bta_case_class;

    //function: my_func
    //ERROR: Lowercase "function" is not recognized
    function void my_func();
    endfunction : my_func

  endclass : bta_case_class

endpackage : bta_case_pkg

`endif // WRONG_KEYWORDS_EXAMPLE_SV


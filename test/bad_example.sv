// This is a BAD example file that violates ALL BTA coding standards
// Purpose: Testing linter and demonstrating what NOT to do
// Author: Test Generator

// ❌ VIOLATION: No proper file header (missing Company, proper format)
// ❌ VIOLATION: No include guards (`ifndef FILENAME_SV)

// ❌ VIOLATION: Wrong interface naming (should have _if suffix)
// ❌ VIOLATION: Missing interface documentation
interface MyInterface;
  logic clk;
  logic [31:0] data;
  logic valid;
endinterface

// ❌ VIOLATION: Wrong package naming (should be *_pkg)
package TestPackage;	// ❌ VIOLATION: Using tabs instead of spaces
// ❌ VIOLATION: Missing package documentation (Package: keyword)

import uvm_pkg::*;

// ❌ VIOLATION: Wrong typedef naming (should have _t suffix)
// ❌ VIOLATION: Missing typedef documentation
typedef enum {IDLE, ACTIVE, DONE} StateEnum;

// ❌ VIOLATION: Wrong class naming (should have bta_ prefix)
// ❌ VIOLATION: Missing class documentation
// ❌ VIOLATION: Using tabs for indentation
class BadDriver extends uvm_driver;
	// ❌ VIOLATION: Missing UVM factory registration macro

	// ❌ VIOLATION: Wrong member variable naming (should have m_ prefix)
	// ❌ VIOLATION: Missing variable documentation
	int dataWidth;		// Using tabs
	string configName;
	virtual MyInterface vif;  // ❌ VIOLATION: vif should be named *_vif

	// ❌ VIOLATION: Parameters should be UPPER_CASE
	parameter int MaxSize = 1024;
	localparam string default_name = "driver";	// ❌ Should be UPPER_CASE

	// ❌ VIOLATION: Wrong constraint naming (should have _c suffix)
	// ❌ VIOLATION: Wrong constraint documentation (should use define: keyword)
	// Constraint: This is wrong format
	constraint valid_data_constraint {
		dataWidth inside {8, 16, 32, 64};
		dataWidth > 0;
	}

	// ❌ VIOLATION: Missing Groups for organization
	// ❌ VIOLATION: Missing function documentation
	// ❌ VIOLATION: Function should have explicit lifetime
	// ❌ VIOLATION: Missing arguments/returns documentation
	function void SetConfig(string name, int width);
		configName = name;
		dataWidth = width;
		$display("Config set");  // ❌ Should use `uvm_info instead
	endfunction

	// ❌ VIOLATION: Missing task documentation
	// ❌ VIOLATION: Task should have explicit lifetime
	task run_phase(uvm_phase phase);
		forever begin
			// ❌ VIOLATION: Line too long - this line intentionally exceeds 100 characters to demonstrate violation of maximum line length coding standard
			@(posedge vif.clk);
			vif.data <= $random;
		end
	endtask

	// ❌ VIOLATION: Using $random instead of proper randomization
	// ❌ VIOLATION: Function created without factory
	function new(string name = "BadDriver");
		// ❌ VIOLATION: Missing super.new() call
		this.configName = name;
	endfunction  // ❌ VIOLATION: Unnamed ending (should be endfunction : new)

endclass  // ❌ VIOLATION: Unnamed ending (should be endclass : BadDriver)

// ❌ VIOLATION: Wrong class naming
// ❌ VIOLATION: Missing class documentation
class ConfigObject extends uvm_object;
	// ❌ VIOLATION: Missing factory macro

	rand bit [7:0] addr;
	rand bit [31:0] data;

	// ❌ VIOLATION: always blocks cannot be in classes (removed for valid syntax)

endclass

// ❌ VIOLATION: Wrong class naming (should be bta_*_config)
// ❌ VIOLATION: Missing comprehensive documentation
class MyConfig;
	int timeout;
	string name;

	// ❌ VIOLATION: Missing constraint prefix
	constraint timing { timeout inside {[10:100]}; }
endclass  // ❌ VIOLATION: Unnamed ending

// ❌ VIOLATION: Wrong sequence naming
class TestSequence extends uvm_sequence;
	// ❌ VIOLATION: Missing factory macro

	// ❌ VIOLATION: No documentation
	// ❌ VIOLATION: Wrong variable naming
	int numItems;

	function new(string name = "TestSequence");
		super.new(name);
	endfunction

	task body();
		repeat (numItems) begin
			// ❌ VIOLATION: Not using factory pattern properly
			ConfigObject cfg = new();
			// ❌ No randomization
		end
	endtask  // ❌ VIOLATION: Unnamed ending
endclass  // ❌ VIOLATION: Unnamed ending

// ❌ VIOLATION: Missing file-level documentation
// ❌ VIOLATION: No Groups used
// ❌ VIOLATION: No cross-references to related classes

`define my_macro 100  // ❌ VIOLATION: Macro should be UPPER_CASE
`define ANOTHER_MACRO(x) (x + 1)  // ❌ VIOLATION: Macro name styling (removed backslash continuation for valid syntax)

// ❌ VIOLATION: This function uses system tasks that should be avoided
function void bad_system_calls();
	string s;
	s = $psprintf("Bad: %d", 10);  // ❌ Use $sformatf instead
	int r = $random;  // ❌ Use std::randomize instead
endfunction

// ❌ VIOLATION: No proper endpackage documentation
endpackage  // ❌ VIOLATION: Unnamed ending (should be endpackage : TestPackage)

// ❌ VIOLATION: Module should not use defparam (deprecated)
module test_module;
	parameter WIDTH = 32;

	// ❌ VIOLATION: Missing generate label
	generate
		for (genvar i = 0; i < WIDTH; i++) begin
			// ❌ VIOLATION: Unlabeled generate block
			assign data[i] = in[i];
		end
	endgenerate

	// ❌ VIOLATION: Using always @* instead of always_comb
	logic result;
	always @* begin
		result = a & b;  // ❌ Should use always_comb
	end

	// ❌ VIOLATION: Case without default
	always_ff @(posedge clk) begin
		case (state)
			2'b00: next_state = 2'b01;
			2'b01: next_state = 2'b10;
			2'b10: next_state = 2'b00;
			// ❌ Missing default case
		endcase
	end

	// ❌ VIOLATION: Using blocking assignment in sequential logic
	always_ff @(posedge clk) begin
		counter = counter + 1;  // ❌ Should use non-blocking (<=)
	end

	// ❌ VIOLATION: Consecutive null statements
	assign x = 1;;

	// ❌ VIOLATION: Trailing spaces at end of line

endmodule

// ❌ VIOLATION: No closing comment for package
// ❌ VIOLATION: Missing include guard closing (`endif // FILENAME_SV)

/*
SUMMARY OF ALL VIOLATIONS IN THIS FILE:
========================================

NAMING VIOLATIONS (Coding Standards):
1. ❌ Package: "TestPackage" (should be "test_package_pkg")
2. ❌ Typedef: "StateEnum" (should be "state_enum_t")
3. ❌ Interface: "MyInterface" (should be "my_interface_if")
4. ❌ Class: "BadDriver" (should be "bta_bad_driver")
5. ❌ Class: "ConfigObject" (should be "bta_config_object")
6. ❌ Class: "MyConfig" (should be "bta_my_config")
7. ❌ Class: "TestSequence" (should be "bta_test_sequence")
8. ❌ Member variables: "dataWidth", "configName" (should be "m_data_width", "m_config_name")
9. ❌ Virtual interface: "vif" (should be "*_vif" with descriptive name)
10. ❌ Constraints: "valid_data_constraint", "timing" (should be "valid_data_c", "timing_c")
11. ❌ Parameters: "MaxSize", "default_name" (should be "MAX_SIZE", "DEFAULT_NAME")
12. ❌ Macro: "my_macro" (should be "MY_MACRO")

STYLE VIOLATIONS (Coding Standards):
13. ❌ Using tabs instead of 2 spaces
14. ❌ Lines exceeding 100 characters
15. ❌ Trailing spaces
16. ❌ Using always @* instead of always_comb
17. ❌ Consecutive null statements (;;)
18. ❌ No include guards
19. ❌ No proper file header

DOCUMENTATION VIOLATIONS (NaturalDocs Patterns):
20. ❌ Missing file header documentation
21. ❌ Missing Package: documentation
22. ❌ Missing Class: documentation
23. ❌ Missing Function: documentation
24. ❌ Missing Task: documentation
25. ❌ Missing Variable: documentation
26. ❌ Missing define: for constraints (using wrong "Constraint:" keyword)
27. ❌ Missing Interface: documentation
28. ❌ Missing Typedef: documentation (should use Type:)
29. ❌ No Groups used for organization
30. ❌ No cross-references using angle brackets
31. ❌ No code examples in documentation

UVM/SYSTEMVERILOG BEST PRACTICES VIOLATIONS:
32. ❌ Missing factory registration macros
33. ❌ Using $display instead of `uvm_info
34. ❌ Using $random instead of randomize()
35. ❌ Using $psprintf instead of $sformatf
36. ❌ Missing explicit function/task lifetime
37. ❌ Blocking assignment in sequential logic (always_ff)
38. ❌ Non-blocking assignment in combinational logic
39. ❌ Case statement without default
40. ❌ Missing generate block labels
41. ❌ Using deprecated defparam
42. ❌ Line continuation with backslash
43. ❌ Not using factory pattern (new() instead of create())
44. ❌ Missing parameter types
45. ❌ Missing super.new() in constructor

VERIBLE LINT RULE VIOLATIONS:
46. ❌ line-length (100 chars)
47. ❌ no-tabs
48. ❌ no-trailing-spaces
49. ❌ constraint-name-style (*_c suffix)
50. ❌ enum-name-style (*_t suffix)
51. ❌ interface-name-style (*_if suffix)
52. ❌ macro-name-style (UPPER_CASE)
53. ❌ always-comb
54. ❌ always-comb-blocking
55. ❌ always-ff-non-blocking
56. ❌ case-missing-default
57. ❌ generate-label
58. ❌ explicit-function-lifetime
59. ❌ explicit-task-lifetime
60. ❌ invalid-system-task-function
61. ❌ forbid-consecutive-null-statements
62. ❌ forbid-line-continuations

This file demonstrates 60+ distinct violations!
Use this to test your linter configuration.
*/


// ❌ VIOLATION: No proper file header (missing Company, proper format, Author with @btadesignservices.com)
// ❌ VIOLATION: No include guards (`ifndef BAD_EXAMPLE_VALID_SYNTAX_SV)

// ❌ VIOLATION: Wrong interface naming (should have _if suffix)
// ❌ VIOLATION: Missing interface documentation (should use Interface: keyword)
interface MyInterface(input logic clk);
  logic [31:0] data;
  logic valid;
endinterface

// ❌ VIOLATION: Wrong package naming (should be *_pkg suffix)
package TestPackage;

// ❌ VIOLATION: Missing package documentation (should use Package: keyword)
// ❌ VIOLATION: No UVM import documentation (should use Program: keyword)

import uvm_pkg::*;

// ❌ VIOLATION: Wrong typedef naming (should have _t suffix)
// ❌ VIOLATION: Missing typedef documentation (should use Type: keyword)
typedef enum {IDLE, ACTIVE, DONE} StateEnum;

// ❌ VIOLATION: Wrong class naming (should have bta_ prefix)
// ❌ VIOLATION: Missing class documentation (should use Class: keyword)
// ❌ VIOLATION: Tabs used for indentation (should be 2 spaces)
class BadDriver extends uvm_driver;
	// ❌ VIOLATION: Missing UVM factory registration macro
	// ❌ VIOLATION: Missing Group: for Variables organization

	// ❌ VIOLATION: Wrong member variable naming (should have m_ prefix)
	// ❌ VIOLATION: Missing variable documentation (should use Variable: keyword)
	int dataWidth;
	string configName;
	int timeout;

	// ❌ VIOLATION: Parameters should be UPPER_CASE
	// ❌ VIOLATION: Missing explicit parameter type
	parameter MaxSize = 1024;
	localparam default_name = "driver";

	// ❌ VIOLATION: Wrong constraint naming (should have _c suffix)
	// ❌ VIOLATION: Wrong constraint documentation (should use define: keyword not Constraint:)
	constraint valid_data_constraint {
		dataWidth inside {8, 16, 32, 64};
		dataWidth > 0;
	}

	// ❌ VIOLATION: Missing Group: for Methods organization
	// ❌ VIOLATION: Missing function documentation (should use Function: keyword)
	// ❌ VIOLATION: Function should have explicit lifetime (static or automatic)
	// ❌ VIOLATION: Missing Arguments: and Returns: documentation
	function void SetConfig(string name, int width);
		configName = name;
		dataWidth = width;
	endfunction

	// ❌ VIOLATION: Constructor without proper documentation
	function new(string name = "BadDriver");
		super.new(name);
		this.configName = name;
	endfunction  // ❌ VIOLATION: Unnamed ending (should be endfunction : new)

endclass  // ❌ VIOLATION: Unnamed ending (should be endclass : BadDriver)

// ❌ VIOLATION: Wrong class naming
// ❌ VIOLATION: Missing class documentation
class ConfigObject extends uvm_object;
	// ❌ VIOLATION: Missing factory macro
	// ❌ VIOLATION: Variables without proper prefix and documentation

	rand bit [7:0] addr;
	rand bit [31:0] data_value;

	// ❌ VIOLATION: Missing constraint suffix _c
	// ❌ VIOLATION: Missing constraint documentation with define:
	constraint addr_range {
		addr inside {[0:127]};
	}

	// ❌ VIOLATION: Line too long - this line intentionally exceeds the maximum allowed line length of 100 characters to demonstrate a line-length violation error

	function new(string name = "ConfigObject");
		super.new(name);
	endfunction  // ❌ VIOLATION: Unnamed ending

endclass  // ❌ VIOLATION: Unnamed ending

// ❌ VIOLATION: Wrong class naming (should be bta_*_config)
class MyConfig extends uvm_object;
	int my_timeout;	// ❌ VIOLATION: Using tab
	string testName;

	// ❌ VIOLATION: Missing constraint suffix _c
	constraint timing {
		my_timeout inside {[10:100]};
	}

	function new(string name = "MyConfig");
		super.new(name);
	endfunction  // ❌ VIOLATION: Unnamed ending
endclass  // ❌ VIOLATION: Unnamed ending

// ❌ VIOLATION: Wrong sequence naming (should have bta_ prefix)
class TestSequence extends uvm_sequence;
	// ❌ VIOLATION: Missing factory macro
	// ❌ VIOLATION: No documentation
	// ❌ VIOLATION: Wrong variable naming (no m_ prefix)

	int numItems;

	function new(string name = "TestSequence");
		super.new(name);
	endfunction

	task body();
		// Task implementation
	endtask  // ❌ VIOLATION: Unnamed ending
endclass  // ❌ VIOLATION: Unnamed ending

// ❌ VIOLATION: Macro should be UPPER_CASE
`define my_macro 100

// ❌ VIOLATION: Using line continuation with backslash (forbidden)
`define ANOTHER_MACRO(x) \
  (x + 1)

// ❌ VIOLATION: This function uses forbidden system tasks
function automatic string bad_system_calls();
	string s;
	s = $psprintf("Bad: %d", 10);  // ❌ Use $sformatf instead
	return s;
endfunction

endpackage  // ❌ VIOLATION: Unnamed ending and missing proper closing comment

// ❌ VIOLATION: Module in a package (moved outside for valid syntax)
module test_module(
  input logic clk,
  input logic rst,
  output logic result
);
	logic a, b;
	logic [7:0] counter;
	logic [1:0] state, next_state;
	logic [31:0] data [3:0];
	logic [7:0] in;

	// ❌ VIOLATION: Using always @* instead of always_comb
	always @* begin
		result = a & b;
	end

	// ❌ VIOLATION: Case without default
	always_ff @(posedge clk) begin
		case (state)
			2'b00: next_state = 2'b01;
			2'b01: next_state = 2'b10;
			2'b10: next_state = 2'b00;
		endcase
	end

	// ❌ VIOLATION: Using blocking assignment in sequential logic (should be non-blocking <=)
	always_ff @(posedge clk) begin
		if (!rst)
			counter = 8'h00;
		else
			counter = counter + 8'h01;
	end

	// ❌ VIOLATION: Missing generate label
	generate
		for (genvar i = 0; i < 4; i++) begin
			assign data[i] = in + i;
		end
	endgenerate

	// ❌ VIOLATION: Consecutive null statements
	assign a = 1'b1;;

	// ❌ VIOLATION: No trailing spaces check - line has spaces at end

endmodule  // ❌ VIOLATION: Unnamed ending (should be endmodule : test_module)

// ❌ VIOLATION: Missing include guard closing (`endif // BAD_EXAMPLE_VALID_SYNTAX_SV)

/*
SUMMARY OF ALL VIOLATIONS IN THIS FILE (Syntactically Valid):
==============================================================

NAMING VIOLATIONS (BTA Coding Standards):
1.  ❌ Package: "TestPackage" → should be "test_package_pkg"
2.  ❌ Typedef: "StateEnum" → should be "state_enum_t"
3.  ❌ Interface: "MyInterface" → should be "my_interface_if"
4.  ❌ Class: "BadDriver" → should be "bta_bad_driver"
5.  ❌ Class: "ConfigObject" → should be "bta_config_object"
6.  ❌ Class: "MyConfig" → should be "bta_my_config"
7.  ❌ Class: "TestSequence" → should be "bta_test_sequence"
8.  ❌ Members: "dataWidth", "configName", "timeout" → should be "m_*"
9.  ❌ Constraints: "valid_data_constraint", "addr_range", "timing" → should be "*_c"
10. ❌ Parameters: "MaxSize", "default_name" → should be "MAX_SIZE", "DEFAULT_NAME"
11. ❌ Macro: "my_macro" → should be "MY_MACRO"

STYLE VIOLATIONS (Coding Standards):
12. ❌ Using tabs instead of 2 spaces
13. ❌ Lines exceeding 100 characters
14. ❌ Trailing spaces
15. ❌ Using always @* instead of always_comb
16. ❌ Consecutive null statements (;;)
17. ❌ No include guards
18. ❌ No proper file header with Company, Author @btadesignservices.com

DOCUMENTATION VIOLATIONS (NaturalDocs):
19. ❌ Missing file header documentation
20. ❌ Missing Package: keyword for package documentation
21. ❌ Missing Class: keyword for class documentation
22. ❌ Missing Function: keyword for function documentation
23. ❌ Missing Task: keyword for task documentation
24. ❌ Missing Variable: keyword for variable documentation
25. ❌ Using wrong "Constraint:" keyword instead of "define:"
26. ❌ Missing Interface: keyword for interface documentation
27. ❌ Missing Type: keyword for typedef documentation
28. ❌ No Group: keywords for organization
29. ❌ Missing Arguments: and Returns: sections for functions
30. ❌ Missing Program: keyword for package subsections

UVM/SYSTEMVERILOG VIOLATIONS:
31. ❌ Missing factory registration macros (`uvm_object_utils, etc.)
32. ❌ Missing explicit function/task lifetime (automatic/static)
33. ❌ Blocking assignment in sequential logic (always_ff)
34. ❌ Case statement without default
35. ❌ Missing generate block labels
36. ❌ Using forbidden $psprintf (use $sformatf)
37. ❌ Line continuation with backslash (forbidden)
38. ❌ Missing explicit parameter storage types
39. ❌ Unnamed endings (endclass, endfunction, endtask, endpackage, endmodule)

VERIBLE LINT VIOLATIONS:
39. ❌ line-length (>100 chars)
40. ❌ no-tabs
41. ❌ no-trailing-spaces
42. ❌ constraint-name-style (*_c pattern)
43. ❌ enum-name-style (*_t pattern)
44. ❌ interface-name-style (*_if pattern)
45. ❌ macro-name-style (UPPER_CASE)
46. ❌ always-comb (use always_comb not always @*)
47. ❌ always-ff-non-blocking (use <= in always_ff)
48. ❌ case-missing-default
49. ❌ generate-label
50. ❌ explicit-function-lifetime
51. ❌ invalid-system-task-function ($psprintf)
52. ❌ forbid-consecutive-null-statements (;;)
53. ❌ forbid-line-continuations (\)
54. ❌ mismatched-labels (unnamed endings)

This file has 54+ violations with valid SystemVerilog syntax!
Perfect for testing your linter configuration.
*/


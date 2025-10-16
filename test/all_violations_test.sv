// File: all_violations_test.sv
// Company: BTA Design Services
// This file INTENTIONALLY violates Verible lint rules for testing

// VIOLATION: endif-comment mismatch
`ifdef TEST_DEFINE
  localparam int P = 1;
`endif // WRONG_NAME

// VIOLATION: module-filename - module name doesn't match filename
module wrong_module_name (
  input wire clk,
  input wire rst_n,
  input wire [7:0] data_in,
  output logic [7:0] data_out
);

  // VIOLATION: line-length - intentionally long line exceeding 100 characters to demonstrate the line length violation check for testing purposes

  // VIOLATION: trailing-spaces (next line has trailing spaces)
  localparam int PARAM1 = 10;

  // VIOLATION: tabs (next line starts with tab)
	localparam int PARAM2 = 20;

  // VIOLATION: forbid-consecutive-null-statements
  logic signal_a;;

  // VIOLATION: explicit-parameter-storage-type
  parameter NO_TYPE = 5;

  // VIOLATION: parameter-name-style (lowercase)
  parameter int bad_param = 15;

  // VIOLATION: enum-name-style - missing _t suffix
  typedef enum logic [1:0] {
    IDLE = 0,
    RUN = 1,
    DONE = 2
  } bad_enum;

  // VIOLATION: macro-name-style - lowercase
  `define bad_macro 99

  // VIOLATION: struct-union-name-style - missing _t suffix
  typedef struct packed {
    logic [7:0] field1;
    logic [7:0] field2;
  } bad_struct;

  // VIOLATION: typedef-enums - inline enum without typedef
  enum {ENUM_A, ENUM_B} my_enum_var;

  // VIOLATION: case-missing-default
  logic [1:0] sel;
  logic [7:0] result;
  always_comb begin
    case(sel)
      2'b00: result = 8'h10;
      2'b01: result = 8'h20;
    endcase
  end

  // VIOLATION: always-comb - should use always_comb not always @*
  logic combo_sig;
  always @* begin
    combo_sig = signal_a;
  end

  // VIOLATION: always-comb-blocking - non-blocking in always_comb
  logic combo2;
  always_comb begin
    combo2 <= data_in[0];
  end

  // VIOLATION: always-ff-non-blocking - blocking assignment
  logic ff_out;
  always_ff @(posedge clk) begin
    ff_out = data_in[1];
  end

  // VIOLATION: explicit-begin for if
  always_comb
    if (signal_a)
      combo_sig = 1'b1;

  // VIOLATION: explicit-begin for else
  always_comb begin
    if (rst_n)
      combo_sig = 1'b0;
    else
      combo_sig = 1'b1;
  end

  // VIOLATION: explicit-begin for for-loop
  initial
    for (int i = 0; i < 10; i++)
      $display("Count: %0d", i);

  // VIOLATION: explicit-begin for while
  initial begin
    int cnt = 0;
    while (cnt < 5)
      cnt++;
  end

  // VIOLATION: explicit-begin for initial
  initial
    data_out = 8'h00;

  // VIOLATION: invalid-system-task-function - $random forbidden
  initial begin
    int rnd = $random;
  end

  // VIOLATION: forbid-line-continuations
  string str_val = "This is a long string that \
continues on next line with backslash";

  // VIOLATION: forbid-negative-array-dim
  wire [-1:0] neg_array;

  // VIOLATION: packed-dimensions-range-ordering
  wire [0:7] wrong_order;

  // VIOLATION: unpacked-dimensions-range-ordering
  wire [7:0] mem [0:15];

  // VIOLATION: undersized-binary-literal
  wire [7:0] undersized = 4'b1010;

  // VIOLATION: truncated-numeric-literal
  wire [3:0] truncated = 8'd200;

  // VIOLATION: suggest-parentheses - ambiguous precedence
  assign data_out = data_in & 8'h0F | 8'h80;

  // VIOLATION: suspicious-semicolon
  always_comb begin
    if (signal_a);
    combo_sig = 1'b0;
  end

  // VIOLATION: redundant-semicolons
  wire extra_semi;;;

  // VIOLATION: generate-label - unlabeled
  generate
    for (genvar i = 0; i < 4; i++) begin
      wire [7:0] arr_wire;
    end
  endgenerate

  // VIOLATION: generate-label-prefix - wrong prefix
  generate
    for (genvar j = 0; j < 4; j++) begin: bad_gen_name
      wire [7:0] arr2;
    end
  endgenerate

  // VIOLATION: legacy-genvar-declaration
  genvar old_genvar;
  generate
    for (old_genvar = 0; old_genvar < 2; old_genvar++) begin: gen_old
      wire sig;
    end
  endgenerate

  // VIOLATION: instance-shadowing
  begin: outer
    wire shadowed;
    begin: inner
      wire shadowed;  // shadows outer.shadowed
    end
  end

  // VIOLATION: mismatched-labels
  function void my_func();
  endfunction: wrong_name

  // VIOLATION: void-cast - unused return value
  function int get_value();
    return 42;
  endfunction

  initial begin
    get_value();  // should use void'(get_value())
  end

  // VIOLATION: disable-statement
  initial begin
    begin: block1
      #10;
    end
    disable block1;
  end

  // VIOLATION: positive-meaning-parameter-name
  parameter bit DISABLE_CHECK = 1;

  // VIOLATION: numeric-format-string-style
  initial $display("Value: %h", 8'hFF);

endmodule

// VIOLATION: one-module-per-file
module second_module;
endmodule

// VIOLATION: interface-name-style - missing _if
interface bad_if_name;
endinterface

// VIOLATION: package-filename - name doesn't match file
package bad_pkg_name;
endpackage

// VIOLATION: dff-name-style
module dff_test(
  input  wire clk,
  input  wire bad_in,    // should be _d or _next
  output logic bad_out   // should be _q or _reg
);
  always_ff @(posedge clk) begin
    bad_out <= bad_in;
  end
endmodule

// VIOLATION: proper-parameter-declaration
module param_test;
  parameter int p1 = 1, p2 = 2;
endmodule

// UVM violations (in class context)
class test_class;

  // VIOLATION: constraint-name-style - missing _c
  rand int value;
  constraint bad_name {
    value < 100;
  }

  // VIOLATION: explicit-function-lifetime
  function void no_lifetime();
  endfunction

  // VIOLATION: explicit-task-lifetime
  task no_task_lifetime();
  endtask

  // VIOLATION: explicit-function-task-parameter-type
  function void no_type(x);
  endfunction

endclass

// No newline at end (posix-eof violation)
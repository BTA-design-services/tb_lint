#!/bin/bash
# Test runner: Run all linters on all .sv files in test directory
# Create temporary file list
find test -name "*.sv" -type f > /tmp/all_sv_files.txt
python3 unified_linter.py -f /tmp/all_sv_files.txt --color
rm -f /tmp/all_sv_files.txt


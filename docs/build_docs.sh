#!/bin/bash
# Script to build Sphinx documentation for tb_lint
# This script handles the complete documentation build process

set -e  # Exit on error

echo "=================================="
echo "TB_LINT Documentation Builder"
echo "=================================="
echo ""

# Navigate to docs directory
cd "$(dirname "$0")"

# Step 1: Clean previous build
echo "Step 1: Cleaning previous build..."
rm -rf build/
echo "  ✓ Build directory cleaned"
echo ""

# Step 2: Regenerate API documentation
echo "Step 2: Regenerating API documentation..."
cd ..
python3 -m sphinx.ext.apidoc -f -o docs/source . --force
echo "  ✓ API documentation regenerated"
echo ""

# Step 3: Build HTML documentation
echo "Step 3: Building HTML documentation..."
cd docs
python3 -m sphinx -b html source build/html 2>&1 | tee build.log
echo ""

# Check if build succeeded
if [ -f "build/html/index.html" ]; then
    echo "=================================="
    echo "✓ Documentation build succeeded!"
    echo "=================================="
    echo ""
    echo "Output location: $(pwd)/build/html/"
    echo "Open: file://$(pwd)/build/html/index.html"
    echo ""
    
    # Count warnings and errors
    WARNINGS=$(grep -c "WARNING:" build.log || true)
    ERRORS=$(grep -c "ERROR:" build.log || true)
    echo "Build statistics:"
    echo "  - Warnings: $WARNINGS"
    echo "  - Errors: $ERRORS"
    echo ""
    
    if [ $ERRORS -gt 0 ]; then
        echo "Note: There are $ERRORS formatting errors in docstrings."
        echo "These don't prevent documentation generation but should be fixed."
    fi
else
    echo "=================================="
    echo "✗ Documentation build failed!"
    echo "=================================="
    echo "Check build.log for details"
    exit 1
fi


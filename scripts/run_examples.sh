#!/bin/bash
# PyOpenMagnetics - Run All Examples
# This script runs all example files to verify they work correctly

set -e  # Exit on first error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EXAMPLES_DIR="$PROJECT_ROOT/examples"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
SKIPPED=0

# Output directory for results
OUTPUT_DIR="$PROJECT_ROOT/examples/_output"
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  PyOpenMagnetics Example Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Change to project root for imports to work
cd "$PROJECT_ROOT"

# Use virtual environment Python if it exists (required for PyOpenMagnetics C++ bindings)
if [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
    PYTHON="$PROJECT_ROOT/.venv/bin/python"
else
    PYTHON="python3"
fi

# Add project root to PYTHONPATH so examples can import api module
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Function to run a single example
run_example() {
    local file="$1"
    local relative_path="${file#$PROJECT_ROOT/}"

    # Skip __init__.py and test files
    if [[ "$file" == *"__init__.py"* ]] || [[ "$file" == *"test_"* ]]; then
        return 0
    fi

    # Skip files in to_be upgrade folder
    if [[ "$file" == *"to_be upgrade"* ]]; then
        echo -e "  ${YELLOW}SKIP${NC} $relative_path (legacy)"
        SKIPPED=$((SKIPPED + 1))
        return 0
    fi

    echo -n "  Running $relative_path... "

    # Create output filename from example path
    local output_file="$OUTPUT_DIR/$(echo "$relative_path" | tr '/' '_').log"

    # Run with timeout (180 seconds max for complex designs), -u for unbuffered output
    if timeout 180 $PYTHON -u "$file" > "$output_file" 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        echo "    Output (see $output_file):"
        head -20 "$output_file" | sed 's/^/    /'
        FAILED=$((FAILED + 1))
    fi
}

# Consumer Electronics Examples
echo -e "${BLUE}Consumer Electronics${NC}"
for file in "$EXAMPLES_DIR"/consumer/*.py; do
    [ -f "$file" ] && run_example "$file"
done
echo ""

# Automotive Examples
echo -e "${BLUE}Automotive${NC}"
for file in "$EXAMPLES_DIR"/automotive/*.py; do
    [ -f "$file" ] && run_example "$file"
done
echo ""

# Industrial Examples
echo -e "${BLUE}Industrial${NC}"
for file in "$EXAMPLES_DIR"/industrial/*.py; do
    [ -f "$file" ] && run_example "$file"
done
echo ""

# Telecom Examples
echo -e "${BLUE}Telecom${NC}"
for file in "$EXAMPLES_DIR"/telecom/*.py; do
    [ -f "$file" ] && run_example "$file"
done
echo ""

# Advanced Examples
echo -e "${BLUE}Advanced${NC}"
for file in "$EXAMPLES_DIR"/advanced/*.py; do
    [ -f "$file" ] && run_example "$file"
done
echo ""

# Root-level Examples
echo -e "${BLUE}Root Examples${NC}"
for file in "$EXAMPLES_DIR"/*.py; do
    [ -f "$file" ] && run_example "$file"
done
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "  ${GREEN}Passed:${NC}  $PASSED"
echo -e "  ${RED}Failed:${NC}  $FAILED"
echo -e "  ${YELLOW}Skipped:${NC} $SKIPPED"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Some examples failed!${NC}"
    exit 1
else
    echo -e "${GREEN}All examples passed!${NC}"
    exit 0
fi

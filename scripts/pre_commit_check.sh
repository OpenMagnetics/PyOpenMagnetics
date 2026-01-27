#!/bin/bash
# PyOpenMagnetics - Pre-Commit Check Script
# Run this before committing to ensure code quality
#
# Usage:
#   ./scripts/pre_commit_check.sh          # Run all checks
#   ./scripts/pre_commit_check.sh --quick  # Run only fast checks
#   ./scripts/pre_commit_check.sh --full   # Run all checks including examples

set -e  # Exit on first error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
QUICK_MODE=false
FULL_MODE=false
for arg in "$@"; do
    case $arg in
        --quick)
            QUICK_MODE=true
            ;;
        --full)
            FULL_MODE=true
            ;;
    esac
done

cd "$PROJECT_ROOT"

# Use virtual environment Python if it exists (required for PyOpenMagnetics C++ bindings)
if [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
    PYTHON="$PROJECT_ROOT/.venv/bin/python"
else
    PYTHON="python3"
fi

# Add project root to PYTHONPATH so imports work
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Output directory for results
OUTPUT_DIR="$PROJECT_ROOT/examples/_output/checks"
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  PyOpenMagnetics Pre-Commit Checks${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Track overall status
CHECKS_PASSED=0
CHECKS_FAILED=0

# Helper function
run_check() {
    local name="$1"
    local command="$2"
    local output_file="$OUTPUT_DIR/$(echo "$name" | tr ' /' '_').log"

    echo -n "  $name... "

    if eval "$command" > "$output_file" 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        echo "    Output (see $output_file):"
        head -30 "$output_file" | sed 's/^/    /'
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
        return 1
    fi
}

# =============================================================================
# 1. Python Syntax Check
# =============================================================================
echo -e "${BLUE}1. Syntax Checks${NC}"

# Check all Python files for syntax errors
check_python_syntax() {
    local errors=0
    while IFS= read -r -d '' file; do
        if ! $PYTHON -m py_compile "$file" 2>/dev/null; then
            echo "Syntax error in: $file"
            errors=$((errors + 1))
        fi
    done < <(find "$PROJECT_ROOT/api" "$PROJECT_ROOT/examples" -name "*.py" -print0 2>/dev/null)
    return $errors
}
run_check "Python syntax (api/)" "check_python_syntax"
echo ""

# =============================================================================
# 2. Import Checks
# =============================================================================
echo -e "${BLUE}2. Import Checks${NC}"

run_check "Import api module" "$PYTHON -c 'import api'"
run_check "Import api.design" "$PYTHON -c 'from api.design import Design'"
run_check "Import api.waveforms" "$PYTHON -c 'from api.waveforms import boost_inductor_waveforms'"
run_check "Import api.optimization" "$PYTHON -c 'from api.optimization import NSGAOptimizer'"
run_check "Import api.expert.knowledge" "$PYTHON -c 'from api.expert.knowledge import POWDER_CORE_MATERIALS'"
echo ""

# =============================================================================
# 3. Unit Tests
# =============================================================================
echo -e "${BLUE}3. Unit Tests${NC}"

if [ "$QUICK_MODE" = true ]; then
    run_check "Quick pytest (fast tests only)" "$PYTHON -m pytest tests/ -v --tb=short -x -q --ignore=tests/test_examples_integration.py 2>&1 | tail -20"
else
    run_check "Pytest (all unit tests)" "$PYTHON -m pytest tests/ -v --tb=short -x 2>&1 | tail -30"
fi
echo ""

# =============================================================================
# 4. Example Validation (full mode only)
# =============================================================================
if [ "$FULL_MODE" = true ]; then
    echo -e "${BLUE}4. Example Validation${NC}"
    run_check "Run all examples" "$SCRIPT_DIR/run_examples.sh"
    echo ""
fi

# =============================================================================
# 5. Type Hints Check (optional - if mypy installed)
# =============================================================================
if command -v mypy &> /dev/null && [ "$QUICK_MODE" != true ]; then
    echo -e "${BLUE}5. Type Checking (mypy)${NC}"
    run_check "mypy api/" "mypy api/ --ignore-missing-imports --no-error-summary 2>&1 | tail -20"
    echo ""
fi

# =============================================================================
# 6. Documentation Check
# =============================================================================
echo -e "${BLUE}6. Documentation${NC}"

run_check "README.md exists" "test -f README.md"
run_check "PRD.md exists" "test -f PRD.md"
run_check "CLAUDE.md exists" "test -f CLAUDE.md"
echo ""

# =============================================================================
# Summary
# =============================================================================
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "  ${GREEN}Passed:${NC} $CHECKS_PASSED"
echo -e "  ${RED}Failed:${NC} $CHECKS_FAILED"
echo ""

if [ $CHECKS_FAILED -gt 0 ]; then
    echo -e "${RED}Pre-commit checks failed!${NC}"
    echo -e "${YELLOW}Please fix the issues above before committing.${NC}"
    exit 1
else
    echo -e "${GREEN}All pre-commit checks passed!${NC}"
    echo ""
    echo -e "${YELLOW}IMPORTANT: Do NOT push to origin yet!${NC}"
    echo -e "${YELLOW}Features need to be split between FREE and PRO versions.${NC}"
    echo ""
    echo "See PRD.md for the FREE vs PRO feature matrix."
    exit 0
fi

#!/bin/bash
#
# Launch PyOpenMagnetics Streamlit GUI
#
# Usage: ./scripts/run_gui.sh [port]
#
# Requirements:
#   pip install streamlit
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

PORT=${1:-8501}

echo "=============================================="
echo " PyOpenMagnetics Design Tool - Streamlit GUI"
echo "=============================================="
echo ""
echo "Starting server on http://localhost:$PORT"
echo "Press Ctrl+C to stop"
echo ""

cd "$PROJECT_ROOT"

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "ERROR: streamlit not found. Install with:"
    echo "  pip install streamlit"
    exit 1
fi

# Check if GUI pages exist
if [ ! -d "api/gui/pages" ]; then
    echo "WARNING: api/gui/pages directory not found"
    echo "The GUI may have limited functionality"
fi

# Run streamlit
exec streamlit run api/gui/app.py --server.port "$PORT"

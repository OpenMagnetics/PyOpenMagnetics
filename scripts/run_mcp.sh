#!/bin/bash
#
# Launch PyOpenMagnetics MCP Server
#
# Usage: ./scripts/run_mcp.sh
#
# The MCP server provides AI assistant integration for magnetic design.
# It exposes tools: design_magnetic, query_database
#
# To use with Claude Desktop, add to ~/.config/claude/claude_desktop_config.json:
# {
#   "mcpServers": {
#     "pyopenmagnetics": {
#       "command": "/path/to/PyMKF/scripts/run_mcp.sh"
#     }
#   }
# }
#
# Requirements:
#   pip install mcp
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if mcp is installed
python3 -c "import mcp" 2>/dev/null || {
    echo "ERROR: mcp package not found. Install with:" >&2
    echo "  pip install mcp" >&2
    exit 1
}

# Run MCP server
exec python3 -m api.mcp.server

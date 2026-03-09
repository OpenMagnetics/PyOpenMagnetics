#!/bin/bash
# PyOpenMagnetics - Push Blocker
# This script prevents accidental pushes to origin until FREE/PRO split is complete
#
# Installation:
#   cp scripts/block_push.sh .git/hooks/pre-push
#   chmod +x .git/hooks/pre-push

RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${RED}========================================${NC}"
echo -e "${RED}  PUSH BLOCKED${NC}"
echo -e "${RED}========================================${NC}"
echo ""
echo -e "${YELLOW}PyOpenMagnetics push to origin is currently blocked.${NC}"
echo ""
echo "Reason: Features need to be split between FREE and PRO versions"
echo "        before public release."
echo ""
echo -e "${BLUE}FREE Features:${NC}"
echo "  - Basic topologies (buck, boost, flyback)"
echo "  - Design adviser"
echo "  - Core/material database"
echo "  - Python API"
echo "  - Basic examples"
echo ""
echo -e "${BLUE}PRO Features (to be separated):${NC}"
echo "  - Multi-objective optimization (NSGA-II)"
echo "  - MCP server for AI"
echo "  - Streamlit GUI"
echo "  - FEMMT bridge"
echo "  - Expert knowledge base"
echo "  - Advanced topologies (LLC, DAB)"
echo "  - Full powder core materials (25+)"
echo ""
echo "See PRD.md for the complete feature matrix."
echo ""
echo -e "${YELLOW}To force push (NOT RECOMMENDED):${NC}"
echo "  git push --no-verify"
echo ""
echo -e "${YELLOW}To remove this block after FREE/PRO split:${NC}"
echo "  rm .git/hooks/pre-push"
echo ""

exit 1

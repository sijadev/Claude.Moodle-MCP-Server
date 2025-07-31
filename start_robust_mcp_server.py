#!/usr/bin/env python3
"""
Startup script for the robust MCP server
This ensures proper Python path setup
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import and run the server
from src.core.robust_mcp_server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
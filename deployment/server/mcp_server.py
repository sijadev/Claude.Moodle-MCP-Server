"""
Compatibility module for direct import of mcp_server.
Re-exports everything from src.core.mcp_server for backward compatibility.
"""

import os
import sys

# Add the src directory to the Python path for imports to work
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    from src.core.mcp_server import *
except ImportError:
    # Fallback for different environment setups
    try:
        from core.mcp_server import *
    except ImportError:
        # Another fallback
        sys.path.insert(0, os.path.join(current_dir, "src", "core"))
        from mcp_server import *

#!/usr/bin/env python3
"""
MCP Server startup script with proper import handling
"""

import sys
import os

# Add the project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

# Now we can import and run the enhanced MCP server
if __name__ == "__main__":
    try:
        # Import the enhanced MCP server
        import asyncio
        from src.core.enhanced_mcp_server import main
        
        # Run the server
        asyncio.run(main())
    except ImportError as e:
        print(f"Import error: {e}", file=sys.stderr)
        print("Checking if all required files exist...", file=sys.stderr)
        
        required_files = [
            "src/core/enhanced_mcp_server.py",
            "config/dual_token_config.py", 
            "src/core/constants.py",
            "src/clients/moodle_client.py"
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"Found: {file_path}", file=sys.stderr)
            else:
                print(f"Missing: {file_path}", file=sys.stderr)
                
        sys.exit(1)
    except Exception as e:
        print(f"Error starting MCP server: {e}", file=sys.stderr)
        sys.exit(1)
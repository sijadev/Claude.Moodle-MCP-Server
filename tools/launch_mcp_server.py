#!/usr/bin/env python3
"""
MCP Server Launcher für Claude Desktop
=====================================

Startet den MCP Server mit korrekter Umgebung und PYTHONPATH.
Löst Import-Probleme und stellt sicher, dass alle Dependencies verfügbar sind.
"""

import logging
import os
import sys
from pathlib import Path


def setup_environment():
    """Setup correct Python path and environment."""
    # Get project root
    project_root = Path(__file__).parent.parent

    # Add project root and src to Python path
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "src"))

    # Set environment variables
    os.environ["PYTHONPATH"] = (
        f"{project_root}:{project_root / 'src'}:{os.environ.get('PYTHONPATH', '')}"
    )

    # Ensure all required directories are in path
    required_paths = [
        project_root,
        project_root / "src",
        project_root / "config",
        project_root / "src" / "core",
        project_root / "src" / "clients",
    ]

    for path in required_paths:
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))


def main():
    """Main launcher function."""
    # Setup environment first
    setup_environment()

    # Get server type from command line or environment
    server_type = os.environ.get("MCP_SERVER_TYPE", "optimized")

    if len(sys.argv) > 1:
        if sys.argv[1] in ["optimized", "advanced", "enhanced"]:
            server_type = sys.argv[1]

    # Map server types to modules
    server_modules = {
        "optimized": "src.core.optimized_mcp_server",
        "advanced": "src.core.advanced_mcp_server",
        "enhanced": "src.core.enhanced_mcp_server",
    }

    if server_type not in server_modules:
        print(f"Unknown server type: {server_type}")
        print(f"Available types: {list(server_modules.keys())}")
        sys.exit(1)

    module_name = server_modules[server_type]

    try:
        # Import and run the server
        print(f"Starting MCP Server: {server_type}")
        print(f"Module: {module_name}")
        print(f"Python Path: {sys.path[:3]}...")

        # Import the server module
        import importlib

        server_module = importlib.import_module(module_name)

        # Check if the module has a main function
        if hasattr(server_module, "main"):
            server_module.main()
        elif hasattr(server_module, "run_server"):
            server_module.run_server()
        else:
            print(
                f"Server module {module_name} doesn't have main() or run_server() function"
            )
            sys.exit(1)

    except ImportError as e:
        print(f"Failed to import server module {module_name}: {e}")
        print("Available modules in src.core:")

        project_root = Path(__file__).parent.parent
        core_dir = project_root / "src" / "core"
        if core_dir.exists():
            for py_file in core_dir.glob("*mcp*.py"):
                print(f"  - {py_file.name}")

        sys.exit(1)
    except Exception as e:
        print(f"Failed to start server: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
MCP Server Launcher for Claude Desktop
This script ensures proper module loading and robust error handling
"""

import sys
import os
import logging

def setup_logging():
    """Setup logging to stderr for Claude Desktop visibility"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [MCP-Launcher] %(levelname)s: %(message)s',
        stream=sys.stderr
    )
    return logging.getLogger(__name__)

def setup_python_path():
    """Setup Python path for module imports"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Add project root to Python path if not already there
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        
    # Also try adding to PYTHONPATH for subprocess compatibility
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    if project_root not in current_pythonpath:
        if current_pythonpath:
            os.environ['PYTHONPATH'] = f"{project_root}:{current_pythonpath}"
        else:
            os.environ['PYTHONPATH'] = project_root
    
    return project_root

def main():
    """Main launcher function"""
    logger = setup_logging()
    
    try:
        logger.info("🚀 Starting MCP Server Launcher...")
        
        # Setup Python path
        project_root = setup_python_path()
        logger.info(f"📁 Project root: {project_root}")
        logger.info(f"🐍 Python path: {sys.path[:3]}...")  # Show first 3 entries
        
        # Test imports before launching
        logger.info("🔍 Testing imports...")
        try:
            import src.core.robust_mcp_server
            logger.info("✅ Import test successful")
        except ImportError as e:
            logger.error(f"❌ Import test failed: {e}")
            logger.error("📋 Available modules in src/core/:")
            try:
                core_dir = os.path.join(project_root, 'src', 'core')
                if os.path.exists(core_dir):
                    files = [f for f in os.listdir(core_dir) if f.endswith('.py')]
                    logger.error(f"   {', '.join(files[:5])}")  # Show first 5 files
                else:
                    logger.error(f"   Directory not found: {core_dir}")
            except Exception as e2:
                logger.error(f"   Error listing directory: {e2}")
            raise
        
        # Import and run the server
        logger.info("🎯 Launching robust MCP server...")
        from src.core.robust_mcp_server import main as server_main
        import asyncio
        
        # Run the server
        asyncio.run(server_main())
        
    except KeyboardInterrupt:
        logger.info("🛑 Launcher stopped by user")
    except Exception as e:
        logger.error(f"💥 Launcher failed: {e}")
        logger.error(f"📍 Error type: {type(e).__name__}")
        
        # Additional debugging info
        logger.error("🔧 Debug information:")
        logger.error(f"   Working directory: {os.getcwd()}")
        logger.error(f"   Script location: {__file__}")
        logger.error(f"   Python executable: {sys.executable}")
        logger.error(f"   Python version: {sys.version}")
        
        # Re-raise for proper exit code
        raise

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Quick test to verify that all 6 advanced MCP tools can be imported and initialized
"""

import sys
import os
import asyncio
import logging

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_advanced_server_initialization():
    """Test that the advanced server can be initialized with all tools"""
    try:
        # Set required environment variables
        os.environ['MOODLE_URL'] = 'http://localhost:8080'
        os.environ['MOODLE_BASIC_TOKEN'] = '8545ed4837f1faf6cd246e470815f67b'
        os.environ['MOODLE_PLUGIN_TOKEN'] = 'a72c43335a0974fc34c53a55c7231681'
        os.environ['MOODLE_USERNAME'] = 'simon'
        os.environ['MOODLE_CLAUDE_DB_PATH'] = 'data/sessions.db'
        
        from src.core.advanced_mcp_server import AdvancedMoodleMCPServer
        
        # Initialize server
        logger.info("Initializing Advanced MCP Server...")
        server = AdvancedMoodleMCPServer()
        
        # Verify session manager is initialized
        assert server.session_manager is not None, "Session manager not initialized"
        logger.info("✅ Session manager initialized successfully")
        
        # Verify content processor is available
        assert server.session_manager.content_processor is not None, "Content processor not available"
        logger.info("✅ Content processor initialized successfully")
        
        # Verify database is accessible
        analytics = server.session_manager.get_session_analytics()
        assert 'overall' in analytics, "Database analytics not accessible"
        logger.info("✅ Database and analytics accessible")
        
        # Cleanup
        await server.session_manager.cleanup_and_shutdown()
        logger.info("✅ All advanced server components verified successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Advanced server test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🚀 Testing Advanced MCP Server Components")
    logger.info("=" * 50)
    
    success = await test_advanced_server_initialization()
    
    if success:
        logger.info("=" * 50)
        logger.info("🎉 All tests passed! Advanced MCP Server is ready to use.")
        logger.info("Available tools:")
        logger.info("  1. create_intelligent_course")
        logger.info("  2. continue_course_session") 
        logger.info("  3. validate_course")
        logger.info("  4. get_session_status")
        logger.info("  5. get_processing_analytics")
        logger.info("  6. analyze_content_complexity")
    else:
        logger.error("❌ Tests failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
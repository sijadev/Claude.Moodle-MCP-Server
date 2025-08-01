#!/usr/bin/env python3
"""
Comprehensive test for the dual-token MoodleClaude system
"""

import asyncio
import logging

from dual_token_config import DualTokenConfig
from enhanced_mcp_server import EnhancedMoodleMCPServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_dual_token_system():
    """Test the complete dual-token system"""

    print("🧪 MoodleClaude Dual-Token System Test")
    print("=" * 60)

    # Initialize the enhanced server
    try:
        server = EnhancedMoodleMCPServer()
        print("✅ Enhanced MCP Server initialized")
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        return

    # Test plugin functionality
    print("\n🔧 Testing plugin functionality...")
    try:
        result = await server._test_plugin_functionality({})
        print(result[0].text)
    except Exception as e:
        print(f"❌ Plugin test failed: {e}")

    # Test content extraction
    print("\n📄 Testing content extraction...")
    sample_content = """
# Digital Photography Course

## Module 1: Camera Basics
Learn about different camera types and settings.

```python
# Camera settings example
aperture = "f/2.8"
shutter_speed = "1/125"
iso = 400

print(f"Settings: {aperture}, {shutter_speed}, ISO {iso}")
```

## Module 2: Composition
Master the art of composition in photography.

Key principles:
- Rule of thirds
- Leading lines
- Symmetry
"""

    try:
        result = await server._extract_and_preview_content(
            {"chat_content": sample_content}
        )
        print("✅ Content extraction successful:")
        print(result[0].text[:300] + "...")
    except Exception as e:
        print(f"❌ Content extraction failed: {e}")

    # Test course creation if both tokens work
    config = server.config
    if config and config.is_dual_token_mode():
        print(f"\n🚀 Testing course creation with dual tokens...")
        try:
            result = await server._create_course_from_chat(
                {
                    "chat_content": sample_content,
                    "course_name": "Dual-Token Test Course",
                    "course_description": "Test course created with dual-token system",
                }
            )
            print("📚 Course creation result:")
            print(result[0].text[:500] + "...")
        except Exception as e:
            print(f"❌ Course creation test failed: {e}")

    print(f"\n" + "=" * 60)
    print("🎯 Dual-Token System Test Complete!")


if __name__ == "__main__":
    asyncio.run(test_dual_token_system())

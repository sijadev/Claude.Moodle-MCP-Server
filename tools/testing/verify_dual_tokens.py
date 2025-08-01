#!/usr/bin/env python3
"""
Token verification script for dual-token setup
Tests both basic and plugin tokens independently
"""

import asyncio
import logging
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.dual_token_config import DualTokenConfig
from src.clients.moodle_client import MoodleClient
from src.clients.moodle_client_enhanced import EnhancedMoodleClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def verify_tokens():
    """Verify both basic and plugin tokens work correctly"""

    print("🔍 MoodleClaude Dual-Token Verification")
    print("=" * 60)

    # Load configuration
    try:
        config = DualTokenConfig.from_env()
        print(f"📋 Configuration loaded:")
        summary = config.get_config_summary()
        for key, value in summary.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Current .env format:")
        print("   MOODLE_URL=http://localhost:8080")
        print("   MOODLE_TOKEN=your_current_token")
        print("\n🔧 For dual-token setup, use:")
        print("   MOODLE_BASIC_TOKEN=token_for_basic_operations")
        print("   MOODLE_PLUGIN_TOKEN=token_for_plugin_operations")
        return

    # Test 1: Basic token
    print(f"\n1️⃣ Testing Basic Token...")
    print(f"   Token: ...{config.get_basic_token()[-8:]}")

    try:
        async with MoodleClient(
            config.moodle_url, config.get_basic_token()
        ) as basic_client:
            courses = await basic_client.get_courses()
            print(f"   ✅ Basic operations work - found {len(courses)} courses")

            # Try creating a test course
            test_course_id = await basic_client.create_course(
                name="Token Test Course (Basic)",
                description="Test course for basic token verification",
            )
            print(f"   ✅ Course creation works - ID: {test_course_id}")

    except Exception as e:
        print(f"   ❌ Basic token failed: {e}")
        print("   💡 Check if token is valid and has basic web service access")

    # Test 2: Plugin token
    print(f"\n2️⃣ Testing Plugin Token...")
    plugin_token = config.get_plugin_token()
    print(f"   Token: ...{plugin_token[-8:]}")

    if config.is_dual_token_mode():
        print("   🔄 Dual-token mode detected")
    else:
        print("   🔄 Single-token mode (using same token for plugin operations)")

    try:
        async with EnhancedMoodleClient(
            config.moodle_url, plugin_token
        ) as plugin_client:
            # Check plugin availability
            plugin_available = await plugin_client._check_plugin_availability()

            if plugin_available:
                print("   ✅ Plugin functions detected!")

                # Test enhanced functionality
                test_course_id = await plugin_client.create_course(
                    name="Token Test Course (Plugin)",
                    description="Test course for plugin token verification",
                )
                print(f"   ✅ Enhanced course creation works - ID: {test_course_id}")

                # Test section update
                section_success = await plugin_client.update_section_content(
                    course_id=test_course_id,
                    section_number=1,
                    name="Test Section",
                    summary="<h3>Plugin Test</h3><p>This section was updated using the plugin token!</p>",
                )

                if section_success:
                    print("   ✅ Section content update works!")
                else:
                    print("   ⚠️ Section update limited (expected without plugin)")

                # Test activity creation
                page_result = await plugin_client.create_page_activity(
                    course_id=test_course_id,
                    section_id=1,
                    name="Test Page Activity",
                    content="<h2>Plugin Token Test</h2><p>This page was created using enhanced functionality!</p>",
                )

                if page_result["success"]:
                    print(
                        f"   ✅ Page activity creation works! (ID: {page_result['activity_id']})"
                    )
                    print(
                        f"   🔗 Visit: {config.moodle_url}/course/view.php?id={test_course_id}"
                    )
                else:
                    print(
                        f"   ❌ Page activity creation failed: {page_result['message']}"
                    )

            else:
                print("   ❌ Plugin functions not available")
                print(
                    "   💡 Check if MoodleClaude service is enabled and token is correct"
                )

    except Exception as e:
        print(f"   ❌ Plugin token failed: {e}")
        print("   💡 Check if token has access to MoodleClaude service")

    # Summary
    print(f"\n" + "=" * 60)
    print("🎯 Token Verification Summary")

    if config.is_dual_token_mode():
        print("\n✅ **Dual-Token Mode Active:**")
        print("   - Basic operations use MOODLE_BASIC_TOKEN")
        print("   - Plugin operations use MOODLE_PLUGIN_TOKEN")
        print("   - Optimal separation of concerns")
    else:
        print("\n🔄 **Single-Token Mode Active:**")
        print("   - Both operations use MOODLE_TOKEN")
        print("   - Token must have access to both services")

    print(f"\n💡 **Next Steps:**")
    print("   1. If both tokens work: You're ready!")
    print("   2. If basic works but plugin doesn't:")
    print("      - Enable 'MoodleClaude Content Creation Service' in Moodle admin")
    print("      - Create token specifically for that service")
    print("   3. If neither works: Check token validity and permissions")


if __name__ == "__main__":
    asyncio.run(verify_tokens())

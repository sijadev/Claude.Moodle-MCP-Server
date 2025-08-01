#!/usr/bin/env python3
"""
Diagnostic script to troubleshoot MoodleClaude service access
"""

import asyncio
import logging

from dual_token_config import DualTokenConfig
from moodle_client import MoodleClient
from moodle_client_enhanced import EnhancedMoodleClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def diagnose_service_access():
    """Diagnose service access issues"""

    print("🔍 MoodleClaude Service Access Diagnosis")
    print("=" * 60)

    config = DualTokenConfig.from_env()

    # Test basic token access to site info
    print("\n1️⃣ Testing basic token access to site info...")
    try:
        async with MoodleClient(config.moodle_url, config.get_basic_token()) as client:
            site_info = await client._call_api("core_webservice_get_site_info", {})
            user_id = site_info.get("userid", "unknown")
            username = site_info.get("username", "unknown")
            print(f"✅ Basic token works - User: {username} (ID: {user_id})")

            # Check available functions
            functions = [f.get("name", "") for f in site_info.get("functions", [])]
            total_functions = len(functions)
            moodleclaude_functions = [
                f for f in functions if "moodleclaude" in f.lower()
            ]

            print(f"📊 Available functions with basic token: {total_functions}")
            print(f"🎯 MoodleClaude functions: {len(moodleclaude_functions)}")

            if moodleclaude_functions:
                print("✅ MoodleClaude functions accessible with basic token!")
                for func in moodleclaude_functions:
                    print(f"   - {func}")
            else:
                print("❌ No MoodleClaude functions accessible with basic token")

    except Exception as e:
        print(f"❌ Basic token site info failed: {e}")

    # Test plugin token access to site info
    print("\n2️⃣ Testing plugin token access to site info...")
    try:
        async with EnhancedMoodleClient(
            config.moodle_url, config.get_plugin_token()
        ) as client:
            site_info = await client._call_api("core_webservice_get_site_info", {})
            user_id = site_info.get("userid", "unknown")
            username = site_info.get("username", "unknown")
            print(f"✅ Plugin token works - User: {username} (ID: {user_id})")

            # Check available functions
            functions = [f.get("name", "") for f in site_info.get("functions", [])]
            total_functions = len(functions)
            moodleclaude_functions = [
                f for f in functions if "moodleclaude" in f.lower()
            ]

            print(f"📊 Available functions with plugin token: {total_functions}")
            print(f"🎯 MoodleClaude functions: {len(moodleclaude_functions)}")

            if moodleclaude_functions:
                print("✅ MoodleClaude functions accessible with plugin token!")
                for func in moodleclaude_functions:
                    print(f"   - {func}")

                # Test actual function call
                print("\n3️⃣ Testing actual MoodleClaude function call...")
                try:
                    # Test the simplest function first
                    result = await client._call_api(
                        "local_moodleclaude_update_section_content",
                        {
                            "courseid": 1,  # Test course
                            "section": 1,
                            "name": "Diagnostic Test Section",
                            "summary": "This is a test from the diagnostic script",
                        },
                    )
                    print(f"✅ Function call successful: {result}")
                except Exception as func_error:
                    print(f"❌ Function call failed: {func_error}")

            else:
                print("❌ No MoodleClaude functions accessible with plugin token")

    except Exception as e:
        print(f"❌ Plugin token site info failed: {e}")
        print("💡 This suggests the plugin token doesn't have proper service access")

    # Compare tokens
    print(f"\n4️⃣ Token comparison...")
    basic_token = config.get_basic_token()
    plugin_token = config.get_plugin_token()

    print(f"Basic token:  ...{basic_token[-12:]}")
    print(f"Plugin token: ...{plugin_token[-12:]}")

    if basic_token == plugin_token:
        print("⚠️ Tokens are identical - this might be the issue!")
        print(
            "💡 You may need to create a separate token specifically for the MoodleClaude service"
        )
    else:
        print("✅ Tokens are different - dual-token setup is correct")

    print(f"\n" + "=" * 60)
    print("🎯 Diagnosis Complete")

    print(f"\n💡 **Next Steps:**")
    print("1. If basic token has MoodleClaude functions: Use single-token mode")
    print("2. If plugin token fails site info: Check service authorization")
    print("3. If tokens are identical: Create separate plugin token")
    print("4. If functions not available: Check service is enabled and user authorized")


if __name__ == "__main__":
    asyncio.run(diagnose_service_access())

#!/usr/bin/env python3
"""
Test exact parameter validation for create_course_structure
"""

import asyncio
import json
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, PROJECT_ROOT)

from config.dual_token_config import DualTokenConfig
from src.clients.moodle_client_enhanced import EnhancedMoodleClient


async def test_exact_validation():
    """Test exact parameter format that Moodle expects"""

    print("🔍 Testing Exact Parameter Validation")
    print("=" * 60)

    config = DualTokenConfig.from_env()
    course_id = 6  # From previous test

    plugin_client = EnhancedMoodleClient(
        base_url=config.moodle_url, token=config.get_plugin_token()
    )

    async with plugin_client as client:
        # Test different parameter formats to see what Moodle expects

        print(f"\n1️⃣ Testing with explicit courseid parameter...")
        try:
            # Try exactly as the PHP function expects
            test_data = {"courseid": course_id, "sections": []}
            print(f"Sending: {json.dumps(test_data, indent=2)}")
            result = await client._call_api(
                "local_moodleclaude_create_course_structure", test_data
            )
            print(f"Result: {result}")
        except Exception as e:
            print(f"❌ Failed: {e}")

        print(f"\n2️⃣ Testing parameter names case sensitivity...")
        try:
            # Try with different case
            test_data = {"courseId": course_id, "sections": []}  # Different case
            print(f"Sending: {json.dumps(test_data, indent=2)}")
            result = await client._call_api(
                "local_moodleclaude_create_course_structure", test_data
            )
            print(f"Result: {result}")
        except Exception as e:
            print(f"❌ Failed: {e}")

        print(f"\n3️⃣ Testing sections parameter format...")
        try:
            # Maybe the issue is with the sections array format
            test_data = {
                "courseid": course_id,
                "sections": [{"name": "Test", "summary": "Test", "activities": []}],
            }
            print(f"Sending: {json.dumps(test_data, indent=2)}")
            result = await client._call_api(
                "local_moodleclaude_create_course_structure", test_data
            )
            print(f"Result: {result}")
        except Exception as e:
            print(f"❌ Failed: {e}")

        print(f"\n4️⃣ Testing if it's about the course permissions...")
        try:
            # Try with a valid course that we know simon has access to
            site_info = await client._call_api("core_webservice_get_site_info", {})
            print(f"User ID: {site_info.get('userid')}")
            print(f"Site name: {site_info.get('sitename')}")

            # Check if we can access the course at all
            courses = await client._call_api("core_course_get_courses", {})
            print(f"Available courses: {[c.get('id') for c in courses]}")

            # Try update_section_content on the same course (this works)
            section_result = await client._call_api(
                "local_moodleclaude_update_section_content",
                {
                    "courseid": course_id,
                    "section": 1,
                    "name": "Validation Test",
                    "summary": "Testing parameter validation",
                },
            )
            print(f"Section update (works): {section_result}")

        except Exception as e:
            print(f"❌ Permission test failed: {e}")

        print(f"\n5️⃣ Testing raw API call format...")
        try:
            # Try the exact format Moodle expects for multi-structure parameters
            import aiohttp

            # Get the raw API URL and token
            url = f"{config.moodle_url}/webservice/rest/server.php"
            token = config.get_plugin_token()

            # Raw API call
            data = {
                "wstoken": token,
                "wsfunction": "local_moodleclaude_create_course_structure",
                "moodlewsrestformat": "json",
                "courseid": course_id,
                "sections[0][name]": "Test Section",
                "sections[0][summary]": "Test Summary",
                "sections[0][activities]": [],
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data) as response:
                    result = await response.json()
                    print(f"Raw API result: {result}")

        except Exception as e:
            print(f"❌ Raw API test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_exact_validation())

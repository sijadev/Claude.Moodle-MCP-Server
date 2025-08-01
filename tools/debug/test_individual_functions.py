#!/usr/bin/env python3
"""
Test individual plugin functions to isolate the parameter validation issue
"""

import asyncio
import json
import logging
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, PROJECT_ROOT)

from config.dual_token_config import DualTokenConfig
from src.clients.moodle_client import MoodleClient
from src.clients.moodle_client_enhanced import EnhancedMoodleClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_individual_functions():
    """Test each plugin function individually to isolate the issue"""

    print("🔍 Testing Individual Plugin Functions")
    print("=" * 60)

    # Load configuration
    config = DualTokenConfig.from_env()
    print(f"📋 Configuration: {config.get_config_summary()}")

    # Create test course
    basic_client = MoodleClient(
        base_url=config.moodle_url, token=config.get_basic_token()
    )

    async with basic_client as basic:
        course_id = await basic.create_course(
            name="Individual Function Test Course",
            description="Course for testing individual plugin functions",
            category_id=1,
        )

    print(f"✅ Test course created with ID: {course_id}")

    # Test plugin client
    plugin_client = EnhancedMoodleClient(
        base_url=config.moodle_url, token=config.get_plugin_token()
    )

    async with plugin_client as client:
        print(f"\n🧪 Testing individual plugin functions...")

        # Test 1: update_section_content (should work)
        print(f"\n1️⃣ Testing update_section_content...")
        try:
            # This should work since it's simpler
            result = await client._call_api(
                "local_moodleclaude_update_section_content",
                {
                    "courseid": course_id,
                    "section": 1,  # Section 1 should exist by default
                    "name": "Test Section Name",
                    "summary": "Test section summary",
                },
            )
            print(f"✅ update_section_content: {result}")
        except Exception as e:
            print(f"❌ update_section_content failed: {e}")

        # Test 2: create_page_activity
        print(f"\n2️⃣ Testing create_page_activity...")
        try:
            result = await client._call_api(
                "local_moodleclaude_create_page_activity",
                {
                    "courseid": course_id,
                    "section": 1,
                    "name": "Test Page",
                    "content": "Simple test content",
                },
            )
            print(f"✅ create_page_activity: {result}")
        except Exception as e:
            print(f"❌ create_page_activity failed: {e}")

        # Test 3: create_label_activity
        print(f"\n3️⃣ Testing create_label_activity...")
        try:
            result = await client._call_api(
                "local_moodleclaude_create_label_activity",
                {
                    "courseid": course_id,
                    "section": 1,
                    "content": "Simple label content",
                },
            )
            print(f"✅ create_label_activity: {result}")
        except Exception as e:
            print(f"❌ create_label_activity failed: {e}")

        # Test 4: create_file_resource
        print(f"\n4️⃣ Testing create_file_resource...")
        try:
            result = await client._call_api(
                "local_moodleclaude_create_file_resource",
                {
                    "courseid": course_id,
                    "section": 1,
                    "name": "Test File",
                    "filename": "test.txt",
                    "content": "Simple file content",
                },
            )
            print(f"✅ create_file_resource: {result}")
        except Exception as e:
            print(f"❌ create_file_resource failed: {e}")

        # Test 5: Test create_course_structure with MINIMAL data
        print(f"\n5️⃣ Testing create_course_structure with absolutely minimal data...")
        try:
            # Try with the absolute minimum possible - empty activities
            minimal_data = {"courseid": course_id, "sections": []}
            result = await client._call_api(
                "local_moodleclaude_create_course_structure", minimal_data
            )
            print(f"✅ create_course_structure (empty): {result}")
        except Exception as e:
            print(f"❌ create_course_structure (empty) failed: {e}")

        # Test 6: Test create_course_structure with one empty section
        print(f"\n6️⃣ Testing create_course_structure with one empty section...")
        try:
            single_section_data = {
                "courseid": course_id,
                "sections": [
                    {
                        "name": "Test Section",
                        "summary": "Test summary",
                        "activities": [],
                    }
                ],
            }
            result = await client._call_api(
                "local_moodleclaude_create_course_structure", single_section_data
            )
            print(f"✅ create_course_structure (one empty section): {result}")
        except Exception as e:
            print(f"❌ create_course_structure (one empty section) failed: {e}")

        # Test 7: Test parameter validation by trying with wrong types
        print(f"\n7️⃣ Testing parameter type validation...")
        try:
            wrong_type_data = {
                "courseid": str(course_id),  # Should be int
                "sections": [],
            }
            result = await client._call_api(
                "local_moodleclaude_create_course_structure", wrong_type_data
            )
            print(f"✅ create_course_structure (wrong courseid type): {result}")
        except Exception as e:
            print(f"❌ create_course_structure (wrong courseid type) failed: {e}")

        # Test 8: Test with invalid course ID
        print(f"\n8️⃣ Testing with invalid course ID...")
        try:
            invalid_course_data = {
                "courseid": 99999,  # Non-existent course
                "sections": [],
            }
            result = await client._call_api(
                "local_moodleclaude_create_course_structure", invalid_course_data
            )
            print(f"✅ create_course_structure (invalid course): {result}")
        except Exception as e:
            print(f"❌ create_course_structure (invalid course) failed: {e}")

        # Test 9: Direct API call to check if it's our wrapper
        print(f"\n9️⃣ Testing direct API access...")
        try:
            # Get available functions to see if our function is there
            site_info = await client._call_api("core_webservice_get_site_info", {})
            functions = [f["name"] for f in site_info.get("functions", [])]

            moodleclaude_functions = [f for f in functions if "local_moodleclaude" in f]
            print(f"Available MoodleClaude functions: {moodleclaude_functions}")

            if "local_moodleclaude_create_course_structure" in functions:
                print("✅ Function is available in API")
            else:
                print("❌ Function not found in API - this is the problem!")

        except Exception as e:
            print(f"❌ Direct API access failed: {e}")

    print("\n" + "=" * 60)
    print("🎯 Individual Function Test Complete")


if __name__ == "__main__":
    asyncio.run(test_individual_functions())

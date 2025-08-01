#!/usr/bin/env python3
"""
Debug plugin parameters to identify validation issues
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
from src.clients.moodle_client_enhanced import EnhancedMoodleClient
from src.core.content_formatter import ContentFormatter
from src.core.content_parser import ChatContentParser

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def debug_plugin_parameters():
    """Debug the exact parameters being sent to the plugin"""

    print("🔍 Debugging Plugin Parameter Validation")
    print("=" * 60)

    # Load configuration
    config = DualTokenConfig.from_env()
    print(f"📋 Configuration: {config.get_config_summary()}")

    # Create test data similar to what causes the error
    test_sections_data = [
        {
            "name": "Test Section",
            "summary": "Test section description",
            "activities": [
                {
                    "type": "page",
                    "name": "Test Page",
                    "content": "<h1>Test Content</h1><p>This is test content.</p>",
                    "filename": "",
                },
                {
                    "type": "file",
                    "name": "Test File",
                    "content": 'print("Hello World")',
                    "filename": "test.py",
                },
            ],
        }
    ]

    print("📊 Test Data Structure:")
    print(json.dumps(test_sections_data, indent=2))

    # Try to call the plugin with minimal data first
    plugin_client = EnhancedMoodleClient(
        base_url=config.moodle_url, token=config.get_plugin_token()
    )

    async with plugin_client as client:
        print("\n🧪 Testing Plugin Availability...")
        plugin_available = await client._check_plugin_availability()
        print(f"Plugin Available: {plugin_available}")

        if not plugin_available:
            print("❌ Plugin not available - cannot test parameters")
            return

        # Get a test course ID (create a simple course first)
        print("\n📋 Creating test course...")
        try:
            # Use the basic client to create a course
            from src.clients.moodle_client import MoodleClient

            basic_client = MoodleClient(
                base_url=config.moodle_url, token=config.get_basic_token()
            )

            async with basic_client as basic:
                course_id = await basic.create_course(
                    name="Debug Test Course",
                    description="Course for debugging plugin parameters",
                    category_id=1,
                )

            print(f"✅ Test course created with ID: {course_id}")

        except Exception as e:
            print(f"❌ Failed to create test course: {e}")
            return

        # Test parameter validation step by step
        print(f"\n🔬 Testing Plugin Parameters with Course ID {course_id}...")

        # Test 1: Empty sections array
        print("\n1️⃣ Testing with empty sections array...")
        try:
            result = await client.create_course_structure(course_id, [])
            print(f"✅ Empty sections: {result}")
        except Exception as e:
            print(f"❌ Empty sections failed: {e}")

        # Test 2: Single section with no activities
        print("\n2️⃣ Testing single section with no activities...")
        try:
            minimal_data = [
                {"name": "Test Section", "summary": "Test summary", "activities": []}
            ]
            result = await client.create_course_structure(course_id, minimal_data)
            print(f"✅ Minimal section: {result}")
        except Exception as e:
            print(f"❌ Minimal section failed: {e}")

        # Test 3: Single section with one simple page activity
        print("\n3️⃣ Testing single page activity...")
        try:
            simple_page_data = [
                {
                    "name": "Test Section",
                    "summary": "Test summary",
                    "activities": [
                        {
                            "type": "page",
                            "name": "Simple Test Page",
                            "content": "Simple test content",
                            "filename": "",
                        }
                    ],
                }
            ]
            result = await client.create_course_structure(course_id, simple_page_data)
            print(f"✅ Simple page: {result}")
        except Exception as e:
            print(f"❌ Simple page failed: {e}")

        # Test 4: Single section with one file activity
        print("\n4️⃣ Testing single file activity...")
        try:
            simple_file_data = [
                {
                    "name": "Test Section",
                    "summary": "Test summary",
                    "activities": [
                        {
                            "type": "file",
                            "name": "Simple Test File",
                            "content": 'print("test")',
                            "filename": "test.py",
                        }
                    ],
                }
            ]
            result = await client.create_course_structure(course_id, simple_file_data)
            print(f"✅ Simple file: {result}")
        except Exception as e:
            print(f"❌ Simple file failed: {e}")

        # Test 5: Complex content (like what causes the error)
        print("\n5️⃣ Testing complex formatted content...")
        try:
            # Test with content similar to what the content formatter produces
            formatter = ContentFormatter()
            complex_content = formatter.format_code_for_moodle(
                code='print("Hello World")\nprint("This is a test")',
                language="python",
                title="Test Code",
                description="Test description",
            )

            complex_data = [
                {
                    "name": "Complex Section",
                    "summary": "Section with complex formatted content",
                    "activities": [
                        {
                            "type": "page",
                            "name": "Complex Page",
                            "content": complex_content,
                            "filename": "",
                        }
                    ],
                }
            ]

            print(f"Complex content length: {len(complex_content)} characters")
            print(f"Complex content preview: {complex_content[:200]}...")

            result = await client.create_course_structure(course_id, complex_data)
            print(f"✅ Complex content: {result}")
        except Exception as e:
            print(f"❌ Complex content failed: {e}")

        # Test 6: Validate parameter types and values
        print("\n6️⃣ Parameter validation check...")

        # Check each parameter individually
        test_params = {"courseid": course_id, "sections": test_sections_data}

        print("Parameter types:")
        print(
            f"  courseid: {type(test_params['courseid'])} = {test_params['courseid']}"
        )
        print(
            f"  sections: {type(test_params['sections'])} with {len(test_params['sections'])} items"
        )

        for i, section in enumerate(test_params["sections"]):
            print(f"    Section {i}:")
            print(f"      name: {type(section['name'])} = '{section['name']}'")
            print(f"      summary: {type(section['summary'])} = '{section['summary']}'")
            print(
                f"      activities: {type(section['activities'])} with {len(section['activities'])} items"
            )

            for j, activity in enumerate(section["activities"]):
                print(f"        Activity {j}:")
                print(
                    f"          type: {type(activity['type'])} = '{activity['type']}'"
                )
                print(
                    f"          name: {type(activity['name'])} = '{activity['name']}'"
                )
                print(
                    f"          content: {type(activity['content'])} ({len(activity['content'])} chars)"
                )
                print(
                    f"          filename: {type(activity['filename'])} = '{activity['filename']}'"
                )

    print("\n" + "=" * 60)
    print("🎯 Debugging Complete")


if __name__ == "__main__":
    asyncio.run(debug_plugin_parameters())

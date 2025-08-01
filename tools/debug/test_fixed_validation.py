#!/usr/bin/env python3
"""
Test fixed parameter validation
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
from src.clients.moodle_client import MoodleClient
from src.clients.moodle_client_enhanced import EnhancedMoodleClient


async def test_fixed_validation():
    """Test if the parameter flattening fixes the validation issue"""

    print("🔍 Testing Fixed Parameter Validation")
    print("=" * 60)

    config = DualTokenConfig.from_env()
    course_id = 6  # From previous test

    # Test with basic client first (has the parameter flattening fix)
    basic_client = MoodleClient(
        base_url=config.moodle_url, token=config.get_plugin_token()
    )

    async with basic_client as client:
        print(f"\n1️⃣ Testing basic client parameter flattening...")

        # Test the flattening function directly
        test_params = {
            "courseid": course_id,
            "sections": [
                {
                    "name": "Test Section",
                    "summary": "Test summary",
                    "activities": [
                        {
                            "type": "page",
                            "name": "Test Page",
                            "content": "Test content",
                            "filename": "",
                        }
                    ],
                }
            ],
        }

        flattened = client._flatten_params(test_params)
        print(f"Flattened parameters:")
        for k, v in flattened.items():
            print(f"  {k}: {v}")

        print(f"\n2️⃣ Testing create_course_structure with flattened parameters...")
        try:
            result = await client._call_api(
                "local_moodleclaude_create_course_structure", test_params
            )
            print(f"✅ Success: {result}")
        except Exception as e:
            print(f"❌ Failed: {e}")

        print(f"\n3️⃣ Testing create_file_resource fix...")
        try:
            result = await client._call_api(
                "local_moodleclaude_create_file_resource",
                {
                    "courseid": course_id,
                    "section": 1,
                    "name": "Test File Fixed",
                    "filename": "test_fixed.py",
                    "content": 'print("File creation fixed!")',
                },
            )
            print(f"✅ File resource: {result}")
        except Exception as e:
            print(f"❌ File resource failed: {e}")

    # Now test with enhanced client
    plugin_client = EnhancedMoodleClient(
        base_url=config.moodle_url, token=config.get_plugin_token()
    )

    async with plugin_client as client:
        print(f"\n4️⃣ Testing enhanced client course structure creation...")

        sections_data = [
            {
                "name": "Python Basics",
                "summary": "Introduction to Python programming",
                "activities": [
                    {
                        "type": "page",
                        "name": "Hello World",
                        "content": '<h2>Hello World Example</h2><p>This is a simple Python example.</p><pre><code>print("Hello, World!")</code></pre>',
                        "filename": "",
                    },
                    {
                        "type": "file",
                        "name": "Hello World Script",
                        "content": 'print("Hello, World!")\nprint("Welcome to Python!")',
                        "filename": "hello_world.py",
                    },
                ],
            },
            {
                "name": "Variables and Data Types",
                "summary": "Learning about Python variables",
                "activities": [
                    {
                        "type": "page",
                        "name": "Variable Examples",
                        "content": "<h2>Python Variables</h2><p>Examples of different variable types.</p>",
                        "filename": "",
                    }
                ],
            },
        ]

        try:
            result = await client.create_course_structure(course_id, sections_data)
            print(f"✅ Enhanced course structure: {result}")

            if result.get("success"):
                print(f"🎉 SUCCESS! Course content should now be populated!")

        except Exception as e:
            print(f"❌ Enhanced client failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_fixed_validation())

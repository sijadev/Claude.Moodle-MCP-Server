#!/usr/bin/env python3
"""
Test different parameter formats for wsmanagesections
"""

import asyncio
import os

from dotenv import load_dotenv
from moodle_client import MoodleClient


async def test_wsmanage_parameters():
    load_dotenv()

    moodle_url = os.getenv("MOODLE_URL")
    moodle_token = os.getenv("MOODLE_TOKEN")

    print(f"🧪 Testing WSManageSections Parameter Formats")
    print("=" * 60)

    async with MoodleClient(moodle_url, moodle_token) as client:
        # Use existing course
        course_id = 6  # From previous test

        # Test different parameter formats for create_sections
        test_formats = [
            # Format 1: Simple parameters
            {
                "name": "Format 1 - Simple",
                "params": {
                    "courseid": course_id,
                    "sectionname": "New Section Simple",
                    "summary": "Simple format test",
                },
            },
            # Format 2: Array format
            {
                "name": "Format 2 - Array",
                "params": {
                    "courseid": course_id,
                    "sections[0][name]": "New Section Array",
                    "sections[0][summary]": "Array format test",
                },
            },
            # Format 3: Position-based
            {
                "name": "Format 3 - Position",
                "params": {
                    "courseid": course_id,
                    "position": 2,
                    "name": "New Section Position",
                    "summary": "Position format test",
                },
            },
            # Format 4: Full specification
            {
                "name": "Format 4 - Full",
                "params": {
                    "courseid": course_id,
                    "sectionnumber": 2,
                    "sectionname": "New Section Full",
                    "summary": "Full format test",
                    "summaryformat": 1,
                    "visible": 1,
                },
            },
            # Format 5: Moodle web service style
            {
                "name": "Format 5 - WS Style",
                "params": {
                    "course": course_id,
                    "sections": [
                        {
                            "name": "New Section WS",
                            "summary": "WS style test",
                            "summaryformat": 1,
                        }
                    ],
                },
            },
        ]

        for test_format in test_formats:
            print(f"\n🔍 Testing: {test_format['name']}")
            print(f"   Parameters: {test_format['params']}")

            try:
                result = await client._call_api(
                    "local_wsmanagesections_create_sections", test_format["params"]
                )
                print(f"✅ SUCCESS! Result: {result}")

                # If successful, verify the section was created
                sections = await client._call_api(
                    "local_wsmanagesections_get_sections", {"courseid": course_id}
                )
                print(f"   Total sections now: {len(sections)}")

                break  # Stop on first success

            except Exception as e:
                print(f"❌ Failed: {e}")

        # Also test minimal parameters
        print(f"\n🔍 Testing: Minimal Parameters")
        try:
            minimal_params = {"courseid": course_id}
            result = await client._call_api(
                "local_wsmanagesections_create_sections", minimal_params
            )
            print(f"✅ Minimal params successful: {result}")
        except Exception as e:
            print(f"❌ Minimal params failed: {e}")

        # Test empty parameters to see error message
        print(f"\n🔍 Testing: Empty Parameters (to see expected format)")
        try:
            result = await client._call_api(
                "local_wsmanagesections_create_sections", {}
            )
            print(f"✅ Empty params successful: {result}")
        except Exception as e:
            print(f"❌ Empty params failed: {e}")
            print(f"   This error might tell us what parameters are expected")


if __name__ == "__main__":
    asyncio.run(test_wsmanage_parameters())

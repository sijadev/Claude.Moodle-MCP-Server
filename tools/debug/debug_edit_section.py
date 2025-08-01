#!/usr/bin/env python3
"""
Debug core_course_edit_section API call
"""

import asyncio
import logging

from moodle_client import MoodleClient

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def debug_edit_section():
    """Debug the core_course_edit_section API call"""
    config = Config()

    if not config.moodle_url or not config.moodle_token:
        print("❌ Missing Moodle credentials - skipping test")
        return

    async with MoodleClient(config.moodle_url, config.moodle_token) as client:
        print("🧪 Debugging core_course_edit_section API...")

        course_id = 13

        print(f"📚 Getting section info for course {course_id}...")

        # Get sections using WSManageSections
        sections = await client._call_api(
            "local_wsmanagesections_get_sections", {"courseid": course_id}
        )

        # Find section 1
        target_section = None
        for section in sections:
            if section.get("sectionnum") == 1:
                target_section = section
                break

        if not target_section:
            print("❌ Could not find section 1")
            return

        section_db_id = target_section["id"]
        print(f"📊 Found section 1 with database ID: {section_db_id}")
        print(f"   Current name: '{target_section.get('name', 'NULL')}'")
        print(f"   Current summary length: {len(target_section.get('summary', ''))}")

        # Try different parameter formats for core_course_edit_section
        test_name = "Test Section Name"
        test_summary = "<p>Test section summary content</p>"

        print(
            f"\n🔄 Testing core_course_edit_section with different parameter formats..."
        )

        # Format 1: Direct parameters
        print("1️⃣ Format 1: Direct parameters")
        try:
            result = await client._call_api(
                "core_course_edit_section",
                {
                    "id": section_db_id,
                    "name": test_name,
                    "summary": test_summary,
                    "summaryformat": 1,
                },
            )
            print(f"   Success: {result}")
        except Exception as e:
            print(f"   Error: {e}")

        # Format 2: With course ID
        print("2️⃣ Format 2: With course ID")
        try:
            result = await client._call_api(
                "core_course_edit_section",
                {
                    "id": section_db_id,
                    "courseid": course_id,
                    "name": test_name,
                    "summary": test_summary,
                    "summaryformat": 1,
                },
            )
            print(f"   Success: {result}")
        except Exception as e:
            print(f"   Error: {e}")

        # Format 3: Using section number instead of ID
        print("3️⃣ Format 3: Using section number")
        try:
            result = await client._call_api(
                "core_course_edit_section",
                {
                    "section": 1,
                    "courseid": course_id,
                    "name": test_name,
                    "summary": test_summary,
                    "summaryformat": 1,
                },
            )
            print(f"   Success: {result}")
        except Exception as e:
            print(f"   Error: {e}")


async def main():
    """Main debug function"""
    print("🧪 core_course_edit_section Debug")
    print("=" * 50)

    await debug_edit_section()

    print("\n" + "=" * 50)
    print("🎯 core_course_edit_section Debug Complete")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Test script to verify section name and content updates work
"""

import asyncio
import logging

from moodle_client import MoodleClient

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_section_update():
    """Test section name and content updates"""
    config = Config()

    if not config.moodle_url or not config.moodle_token:
        print("❌ Missing Moodle credentials - skipping test")
        return

    async with MoodleClient(config.moodle_url, config.moodle_token) as client:
        print("🧪 Testing Section Update...")

        # Use the photography course we created
        course_id = 13

        print(f"📚 Testing section update for course {course_id}...")

        # Test updating section 1 with a meaningful name and content
        section_number = 1
        new_name = "Modul 1: Kamera-Grundlagen"
        new_description = """
        <h3>Die Kamera verstehen</h3>
        <ul>
        <li>Verschiedene Kameratypen (DSLR, Spiegellos, Smartphone)</li>
        <li>Wichtige Bedienelemente</li>
        <li>Grundeinstellungen</li>
        </ul>
        """

        print(f"🔄 Updating section {section_number} with name '{new_name}'...")

        success = await client.update_section_content(
            course_id=course_id,
            section_number=section_number,
            name=new_name,
            summary=new_description,
        )

        if success:
            print("✅ Section update reported success!")
        else:
            print("❌ Section update reported failure!")

        # Verify the update by getting sections again
        print("🔍 Verifying update...")
        sections = await client._call_api(
            "core_course_get_contents", {"courseid": course_id}
        )

        updated_section = None
        for section in sections:
            if section.get("section") == section_number:
                updated_section = section
                break

        if updated_section:
            actual_name = updated_section.get("name", "NULL")
            actual_summary = updated_section.get("summary", "")

            print(f"📊 Section {section_number} after update:")
            print(f"   Name: '{actual_name}'")
            print(f"   Summary length: {len(actual_summary)} characters")
            print(f"   Summary preview: {actual_summary[:100]}...")

            if actual_name == new_name:
                print("✅ Section name updated successfully!")
            else:
                print(f"❌ Section name mismatch:")
                print(f"   Expected: '{new_name}'")
                print(f"   Actual: '{actual_name}'")

            if len(actual_summary) > 0:
                print("✅ Section content added successfully!")
            else:
                print("❌ Section content is still empty!")
        else:
            print(f"❌ Could not find section {section_number} after update")


async def main():
    """Main test function"""
    print("🧪 Section Update Test")
    print("=" * 50)

    await test_section_update()

    print("\n" + "=" * 50)
    print("🎯 Section Update Test Complete")


if __name__ == "__main__":
    asyncio.run(main())

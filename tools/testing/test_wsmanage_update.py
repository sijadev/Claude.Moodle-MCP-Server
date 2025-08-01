#!/usr/bin/env python3
"""
Test WSManageSections update_sections function
"""

import asyncio
import logging

from moodle_client import MoodleClient

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_wsmanage_update():
    """Test the local_wsmanagesections_update_sections function"""
    config = Config()

    if not config.moodle_url or not config.moodle_token:
        print("❌ Missing Moodle credentials - skipping test")
        return

    async with MoodleClient(config.moodle_url, config.moodle_token) as client:
        print("🧪 Testing local_wsmanagesections_update_sections...")

        course_id = 13

        # Get current section info
        sections = await client._call_api(
            "local_wsmanagesections_get_sections", {"courseid": course_id}
        )
        target_section = None
        for section in sections:
            if section.get("sectionnum") == 1:
                target_section = section
                break

        if not target_section:
            print("❌ Could not find section 1")
            return

        section_db_id = target_section["id"]
        print(f"📊 Section 1 before update:")
        print(f"   Database ID: {section_db_id}")
        print(f"   Name: '{target_section.get('name', 'NULL')}'")
        print(f"   Summary: '{target_section.get('summary', '')}'")

        # Test update_sections function with different parameter formats
        test_name = "📸 Modul 1: Kamera-Grundlagen"
        test_summary = """<div class="photography-module">
<h3>Die Kamera verstehen</h3>
<ul>
<li>Verschiedene Kameratypen (DSLR, Spiegellos, Smartphone)</li>
<li>Wichtige Bedienelemente</li>
<li>Grundeinstellungen</li>
</ul>
</div>"""

        print(f"\n🔄 Testing update with name: '{test_name}'")

        # Try different parameter formats
        formats_to_try = [
            {
                "name": "Format 1: sectionnumber + courseid",
                "params": {
                    "courseid": course_id,
                    "sectionnumber": 1,
                    "name": test_name,
                    "summary": test_summary,
                    "summaryformat": 1,
                },
            },
            {
                "name": "Format 2: sections array",
                "params": {
                    "sections": [
                        {
                            "courseid": course_id,
                            "sectionnumber": 1,
                            "name": test_name,
                            "summary": test_summary,
                            "summaryformat": 1,
                        }
                    ]
                },
            },
            {
                "name": "Format 3: sections[0] format",
                "params": {
                    "sections[0][courseid]": course_id,
                    "sections[0][sectionnumber]": 1,
                    "sections[0][name]": test_name,
                    "sections[0][summary]": test_summary,
                    "sections[0][summaryformat]": 1,
                },
            },
        ]

        for format_test in formats_to_try:
            print(f"\n📝 {format_test['name']}:")
            try:
                result = await client._call_api(
                    "local_wsmanagesections_update_sections", format_test["params"]
                )
                print(f"   ✅ Success: {result}")

                # Verify the update
                updated_sections = await client._call_api(
                    "local_wsmanagesections_get_sections", {"courseid": course_id}
                )
                updated_section = None
                for section in updated_sections:
                    if section.get("sectionnum") == 1:
                        updated_section = section
                        break

                if updated_section:
                    print(f"   📊 After update:")
                    print(f"      Name: '{updated_section.get('name', 'NULL')}'")
                    print(
                        f"      Summary length: {len(updated_section.get('summary', ''))}"
                    )

                    if updated_section.get("name") == test_name:
                        print("   🎉 SUCCESS! Section name updated correctly!")
                        return True
                    else:
                        print(
                            f"   ⚠️ Name not updated. Expected: '{test_name}', Got: '{updated_section.get('name')}'"
                        )

                break  # If one format works, we're done

            except Exception as e:
                print(f"   ❌ Error: {e}")

        return False


async def main():
    """Main test function"""
    print("🧪 WSManageSections Update Test")
    print("=" * 50)

    success = await test_wsmanage_update()

    if success:
        print("\n🎉 Section update working!")
    else:
        print("\n❌ Section update still not working")

    print("\n" + "=" * 50)
    print("🎯 WSManageSections Update Test Complete")


if __name__ == "__main__":
    asyncio.run(main())

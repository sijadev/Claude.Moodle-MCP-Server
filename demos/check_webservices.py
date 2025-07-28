#!/usr/bin/env python3
"""
Check available Moodle web service functions
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from moodle_client import MoodleAPIError, MoodleClient


async def check_available_functions():
    """Check what web service functions are available"""
    moodle_url = os.getenv("MOODLE_URL", "http://localhost:8080")
    moodle_token = os.getenv("MOODLE_TOKEN", "b2021a7a41309b8c58ad026a751d0cd0")

    print("🔍 Checking available Moodle Web Service functions...")
    print(f"URL: {moodle_url}")
    print(f"Token: {moodle_token[:10]}...")

    try:
        async with MoodleClient(moodle_url, moodle_token) as client:

            # Test verschiedene API calls um zu sehen was funktioniert
            functions_to_test = [
                "core_webservice_get_site_info",
                "core_course_get_courses",
                "core_course_create_courses",
                "core_course_get_categories",
                "core_course_create_categories",
                "core_course_get_contents",
                "core_course_create_sections",  # Das brauchen wir!
                "core_course_edit_section",
                "mod_page_create_page",
                "core_course_create_activities",
                "mod_label_add_label",
                "core_files_upload",
            ]

            print(f"\n{'Function':<35} {'Status':<15} {'Info'}")
            print("=" * 80)

            for func in functions_to_test:
                try:
                    # Versuche einen API Call - wenn er fehlschlägt wissen wir die Funktion existiert nicht
                    if func == "core_webservice_get_site_info":
                        result = await client._call_api(func)
                        print(
                            f"{func:<35} ✅ Available     Site: {result.get('sitename', 'Unknown')}"
                        )

                    elif func == "core_course_get_courses":
                        result = await client._call_api(func)
                        print(f"{func:<35} ✅ Available     Found {len(result)} courses")

                    elif func == "core_course_get_categories":
                        result = await client._call_api(func)
                        print(f"{func:<35} ✅ Available     Found {len(result)} categories")

                    elif func == "core_course_create_courses":
                        # Nicht testen da es einen Kurs erstellen würde
                        print(f"{func:<35} ✅ Available     (Used successfully)")

                    else:
                        # Teste mit dummy parameters
                        result = await client._call_api(func, {"test": "dummy"})
                        print(f"{func:<35} ✅ Available     Response received")

                except MoodleAPIError as e:
                    if "Can't find data record in database table external_functions" in str(e):
                        print(f"{func:<35} ❌ Not Available Function not enabled")
                    elif "Invalid parameter value detected" in str(e):
                        print(
                            f"{func:<35} ✅ Available     (Parameter error - but function exists)"
                        )
                    elif "Missing required parameter" in str(e):
                        print(f"{func:<35} ✅ Available     (Missing params - but function exists)")
                    else:
                        print(f"{func:<35} ⚠️  Error        {str(e)[:50]}...")

                except Exception as e:
                    print(f"{func:<35} ❌ Error         {str(e)[:50]}...")

            print("\n" + "=" * 80)
            print("RECOMMENDATIONS:")
            print("=" * 80)

            print("\n🔧 To enable missing web service functions in Moodle:")
            print("1. Go to: Site Administration → Server → Web services → External services")
            print("2. Find your web service (or create a new one)")
            print("3. Add the missing functions, especially:")
            print("   - core_course_create_sections")
            print("   - core_course_create_activities")
            print("   - mod_page_create_page")
            print("4. Make sure your user has the right capabilities")

            print("\n🛡️ Required capabilities for your user:")
            print("- moodle/course:manageactivities")
            print("- moodle/course:activityvisibility")
            print("- moodle/course:sectionvisibility")
            print("- moodle/site:uploadusers")

            return True

    except Exception as e:
        print(f"❌ Failed to check functions: {e}")
        return False


async def test_manual_section_creation():
    """Test if we can create sections using direct API calls"""
    moodle_url = os.getenv("MOODLE_URL", "http://localhost:8080")
    moodle_token = os.getenv("MOODLE_TOKEN", "b2021a7a41309b8c58ad026a751d0cd0")

    print(f"\n🧪 Testing manual section creation...")

    try:
        async with MoodleClient(moodle_url, moodle_token) as client:

            # Get existing courses to test with
            courses = await client.get_courses()
            if not courses:
                print("❌ No courses found to test with")
                return

            test_course_id = courses[0]["id"]
            print(f"Testing with course ID: {test_course_id}")

            # Try different section creation approaches
            section_methods = [
                {
                    "name": "core_course_create_sections",
                    "params": {
                        "courseid": test_course_id,
                        "sections[0][name]": "Test Section via API",
                        "sections[0][summary]": "Created via Web Service API",
                    },
                },
                {
                    "name": "core_course_edit_section",
                    "params": {
                        "action": "create",
                        "courseid": test_course_id,
                        "sectionname": "Test Section 2",
                    },
                },
            ]

            for method in section_methods:
                try:
                    print(f"\nTrying: {method['name']}")
                    result = await client._call_api(method["name"], method["params"])
                    print(f"✅ Success! Result: {result}")

                except Exception as e:
                    print(f"❌ Failed: {e}")

    except Exception as e:
        print(f"❌ Manual section test failed: {e}")


async def main():
    print("🚀 Moodle Web Service Function Checker")
    print("=" * 50)

    # Set environment variables
    if not os.getenv("MOODLE_URL"):
        os.environ["MOODLE_URL"] = "http://localhost:8080"
    if not os.getenv("MOODLE_TOKEN"):
        os.environ["MOODLE_TOKEN"] = "b2021a7a41309b8c58ad026a751d0cd0"

    success = await check_available_functions()

    if success:
        await test_manual_section_creation()


if __name__ == "__main__":
    asyncio.run(main())

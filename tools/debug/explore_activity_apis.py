#!/usr/bin/env python3
"""
Explore available activity creation APIs in Moodle
"""

import asyncio
import logging

from moodle_client import MoodleClient

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def explore_activity_apis():
    """Explore what activity creation APIs are available"""
    config = Config()

    if not config.moodle_url or not config.moodle_token:
        print("❌ Missing Moodle credentials - skipping test")
        return

    async with MoodleClient(config.moodle_url, config.moodle_token) as client:
        print("🧪 Exploring Available Activity APIs...")

        # Get site info to see available functions
        try:
            site_info = await client._call_api("core_webservice_get_site_info", {})
            if "functions" in site_info:
                functions = site_info["functions"]
                print(f"📊 Total available functions: {len(functions)}")

                # Look for activity/module creation functions
                activity_functions = []
                for func in functions:
                    func_name = func.get("name", "").lower()
                    if any(
                        keyword in func_name
                        for keyword in [
                            "create",
                            "add",
                            "mod_",
                            "activity",
                            "resource",
                            "page",
                            "label",
                            "file",
                        ]
                    ):
                        activity_functions.append(func)

                print(
                    f"\n🎯 Potential activity creation functions ({len(activity_functions)}):"
                )
                for func in activity_functions:
                    print(f"   - {func.get('name')}")

                # Test some promising functions
                promising_functions = [
                    "mod_page_add_instance",
                    "mod_label_add_instance",
                    "mod_resource_add_instance",
                    "core_course_add_mod",
                    "core_course_create_activities",
                ]

                print(f"\n🔬 Testing promising functions...")
                course_id = 14  # Use our test course

                for func_name in promising_functions:
                    if any(f.get("name") == func_name for f in functions):
                        print(f"\n📝 Testing {func_name}:")
                        try:
                            # Try creating a simple page activity
                            if "page" in func_name:
                                result = await client._call_api(
                                    func_name,
                                    {
                                        "course": course_id,
                                        "name": "Test Page Activity",
                                        "intro": "<p>This is a test page created via API</p>",
                                        "content": "<h3>Test Content</h3><p>This is test content for the page.</p>",
                                        "section": 1,
                                    },
                                )
                                print(f"   ✅ Success: {result}")
                            elif "label" in func_name:
                                result = await client._call_api(
                                    func_name,
                                    {
                                        "course": course_id,
                                        "name": "Test Label",
                                        "intro": "<p>This is a test label created via API</p>",
                                        "section": 1,
                                    },
                                )
                                print(f"   ✅ Success: {result}")
                            elif "resource" in func_name:
                                result = await client._call_api(
                                    func_name,
                                    {
                                        "course": course_id,
                                        "name": "Test Resource",
                                        "intro": "<p>This is a test resource created via API</p>",
                                        "section": 1,
                                    },
                                )
                                print(f"   ✅ Success: {result}")
                            else:
                                print(f"   ⏭️ Skipping (no test parameters defined)")
                        except Exception as e:
                            print(f"   ❌ Error: {e}")
                    else:
                        print(f"   ⚠️ {func_name} not available")

        except Exception as e:
            print(f"❌ Could not get site info: {e}")


async def test_alternative_approaches():
    """Test alternative approaches for content storage"""
    config = Config()

    if not config.moodle_url or not config.moodle_token:
        return

    async with MoodleClient(config.moodle_url, config.moodle_token) as client:
        print(f"\n🔬 Testing Alternative Content Storage Approaches...")

        course_id = 14

        # Approach 1: Try to create a forum post with content
        print("1️⃣ Testing forum post creation:")
        try:
            # First see if we can get forums in the course
            forums = await client._call_api(
                "mod_forum_get_forums_by_courses", {"courseids[0]": course_id}
            )
            print(f"   Found {len(forums)} forums")

            if forums:
                forum_id = forums[0]["id"]
                # Try to create a discussion
                result = await client._call_api(
                    "mod_forum_add_discussion",
                    {
                        "forumid": forum_id,
                        "subject": "Modul 1: Kamera-Grundlagen",
                        "message": "<h3>Die Kamera verstehen</h3><ul><li>Verschiedene Kameratypen</li><li>Wichtige Bedienelemente</li></ul>",
                    },
                )
                print(f"   ✅ Forum discussion created: {result}")
        except Exception as e:
            print(f"   ❌ Forum approach failed: {e}")

        # Approach 2: Try to update course summary with all content
        print("\n2️⃣ Testing course summary update with all content:")
        try:
            all_content = """
            <h2>📸 Digitale Fotografie für Einsteiger - Kursinhalte</h2>
            <div style="background-color: #f0f8ff; padding: 15px; margin: 10px 0; border-left: 4px solid #0066cc;">
            <h3>🎯 Kursübersicht</h3>
            <p>Dieser Kurs wurde automatisch aus einem Chat-Gespräch erstellt und enthält die folgenden Module:</p>
            </div>

            <div style="background-color: #f9f9f9; padding: 15px; margin: 10px 0; border: 1px solid #ddd;">
            <h3>📷 Modul 1: Kamera-Grundlagen</h3>
            <h4>Die Kamera verstehen</h4>
            <ul>
            <li>Verschiedene Kameratypen (DSLR, Spiegellos, Smartphone)</li>
            <li>Wichtige Bedienelemente</li>
            <li>Grundeinstellungen</li>
            </ul>

            <h4>Objektive und Brennweiten</h4>
            <ul>
            <li>Weitwinkel vs. Teleobjektiv</li>
            <li>Festbrennweite vs. Zoom</li>
            <li>Blende und Schärfentiefe</li>
            </ul>
            </div>

            <div style="background-color: #fff8dc; padding: 15px; margin: 10px 0; border: 1px solid #ddd;">
            <h3>💡 Modul 2: Belichtung meistern</h3>
            <h4>Das Belichtungsdreieck</h4>
            <ul>
            <li>Blende (Aperture)</li>
            <li>Verschlusszeit (Shutter Speed)</li>
            <li>ISO-Wert</li>
            </ul>
            </div>

            <p style="margin-top: 20px; font-style: italic; color: #666;">
            💡 Hinweis: Dieser Kurs wurde automatisch aus einem Claude-Chat erstellt. Die Inhalte sind in den jeweiligen Kursabschnitten verfügbar.
            </p>
            """

            result = await client._call_api(
                "core_course_update_courses",
                {
                    "courses[0][id]": course_id,
                    "courses[0][summary]": all_content,
                    "courses[0][summaryformat]": 1,
                },
            )
            print(f"   ✅ Course summary updated successfully")

        except Exception as e:
            print(f"   ❌ Course summary update failed: {e}")


async def main():
    """Main exploration function"""
    print("🧪 Activity API Exploration")
    print("=" * 60)

    await explore_activity_apis()
    await test_alternative_approaches()

    print("\n" + "=" * 60)
    print("🎯 Activity API Exploration Complete")


if __name__ == "__main__":
    asyncio.run(main())

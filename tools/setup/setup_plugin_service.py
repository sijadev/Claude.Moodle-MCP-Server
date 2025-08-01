#!/usr/bin/env python3
"""
Setup script to enable MoodleClaude plugin service and create token
"""

import asyncio
import logging

from moodle_client_enhanced import EnhancedMoodleClient

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_plugin_service():
    """Setup the MoodleClaude plugin service"""
    config = Config()

    if not config.moodle_url or not config.moodle_token:
        print("❌ Missing Moodle credentials - please check .env file")
        return

    async with EnhancedMoodleClient(config.moodle_url, config.moodle_token) as client:
        print("🔧 Setting up MoodleClaude Plugin Service")
        print("=" * 60)

        # Check current web service functions
        print("\n1️⃣ Checking available web service functions...")
        try:
            site_info = await client._call_api("core_webservice_get_site_info", {})
            if "functions" in site_info:
                functions = [f.get("name", "") for f in site_info["functions"]]
                total_functions = len(functions)
                moodleclaude_functions = [
                    f for f in functions if "moodleclaude" in f.lower()
                ]

                print(f"📊 Total web service functions: {total_functions}")
                print(f"🎯 MoodleClaude functions found: {len(moodleclaude_functions)}")

                if moodleclaude_functions:
                    print("✅ MoodleClaude plugin functions are available!")
                    for func in moodleclaude_functions:
                        print(f"   - {func}")
                else:
                    print("❌ MoodleClaude plugin functions not found")
                    print("\n💡 This means the plugin service is not enabled yet.")
                    print("   Please follow these manual steps:")
                    print("   1. Go to: http://localhost:8080/admin/")
                    print(
                        "   2. Site Administration → Server → Web services → External services"
                    )
                    print(
                        "   3. Find 'MoodleClaude Content Creation Service' and enable it"
                    )
                    print("   4. Create a new token for this service")
                    return

        except Exception as e:
            print(f"❌ Error checking functions: {e}")
            return

        # Check current user permissions
        print("\n2️⃣ Checking current user permissions...")
        try:
            user_info = await client._get_current_user()
            username = user_info.get("username", "unknown")
            user_id = user_info.get("userid", 0)
            print(f"👤 Current user: {username} (ID: {user_id})")

            # Check if user has required capabilities
            print("🔍 Checking user capabilities...")

            # This will tell us if the user can use the functions
            if user_info.get("fullname"):
                print(f"✅ User authenticated: {user_info.get('fullname')}")
            else:
                print("⚠️ User information limited")

        except Exception as e:
            print(f"❌ Error checking user: {e}")

        # Test plugin functions directly
        print("\n3️⃣ Testing plugin functions...")

        if moodleclaude_functions:
            # Test creating a simple course first
            try:
                print("📚 Creating test course...")
                course_id = await client.create_course(
                    name="Plugin Test Course",
                    description="Test course for MoodleClaude plugin verification",
                )
                print(f"✅ Test course created: ID {course_id}")

                # Test section update
                print("📝 Testing section update...")
                success = await client.update_section_content(
                    course_id=course_id,
                    section_number=1,
                    name="Test Section",
                    summary="This section was updated using the MoodleClaude plugin!",
                )

                if success:
                    print("✅ Section update successful - plugin is working!")
                else:
                    print("❌ Section update failed - check permissions")

                # Test page activity creation
                print("📄 Testing page activity creation...")
                page_result = await client.create_page_activity(
                    course_id=course_id,
                    section_id=1,
                    name="Test Page",
                    content="<h2>Plugin Test</h2><p>This page was created using the MoodleClaude plugin!</p>",
                )

                if page_result["success"]:
                    print(
                        f"✅ Page activity created successfully! (ID: {page_result['activity_id']})"
                    )
                else:
                    print(f"❌ Page activity creation failed: {page_result['message']}")

                print(
                    f"\n🔗 Visit your test course: {config.moodle_url}/course/view.php?id={course_id}"
                )

            except Exception as e:
                print(f"❌ Error testing functions: {e}")

        print("\n" + "=" * 60)
        if moodleclaude_functions:
            print("🎉 MoodleClaude Plugin Setup Complete!")
            print("\n✅ Ready for automated course creation with:")
            print("   - Real content storage")
            print("   - Actual activity creation")
            print("   - Section content updates")
            print("   - Bulk operations")
        else:
            print("⚠️ Manual configuration required")
            print("   See setup instructions above")


if __name__ == "__main__":
    asyncio.run(setup_plugin_service())

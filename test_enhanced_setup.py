#!/usr/bin/env python3
"""
Test Enhanced MoodleClaude Setup
===============================

Comprehensive test of the enhanced web service setup.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

async def test_enhanced_setup():
    """Test the enhanced MoodleClaude setup."""
    print("🧪 Testing Enhanced MoodleClaude Setup")
    print("=" * 50)
    
    # Import MoodleClaude client
    try:
        from src.moodle.client import MoodleClient
        from src.moodle.models import CourseCreationRequest
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    # Load enhanced configuration
    moodle_url = os.getenv("MOODLE_URL", "http://localhost:8080")
    enhanced_token = os.getenv("MOODLE_TOKEN_ENHANCED")
    
    if not enhanced_token:
        print("❌ MOODLE_TOKEN_ENHANCED not set in environment")
        return False
    
    print(f"✅ Moodle URL: {moodle_url}")
    print(f"✅ Enhanced Token: {enhanced_token[:8]}...")

    # Create client with enhanced token
    try:
        client = MoodleClient(moodle_url, enhanced_token)
        print("✅ MoodleClient created with enhanced token")
    except Exception as e:
        print(f"❌ Failed to create MoodleClient: {e}")
        return False

    # Test 1: Get site info
    print("\n🔍 Test 1: Site Information")
    try:
        site_info = await client.call_webservice("core_webservice_get_site_info")
        print(f"✅ Site: {site_info.get('sitename', 'Unknown')}")
        print(f"✅ User: {site_info.get('username', 'Unknown')}")
        print(f"✅ Functions: {len(site_info.get('functions', []))}")
    except Exception as e:
        print(f"❌ Site info failed: {e}")
        return False

    # Test 2: List courses
    print("\n📚 Test 2: Course Listing")
    try:
        courses = await client.call_webservice("core_course_get_courses")
        print(f"✅ Found {len(courses)} courses")
        for course in courses[:3]:  # Show first 3
            print(f"   • {course.get('shortname', 'N/A')}: {course.get('fullname', 'N/A')}")
    except Exception as e:
        print(f"❌ Course listing failed: {e}")
        return False

    # Test 3: Create test course
    print("\n🆕 Test 3: Course Creation")
    try:
        course_data = {
            "courses": [{
                "fullname": "Enhanced Test Course - " + str(asyncio.get_event_loop().time()),
                "shortname": f"ENHANCED_TEST_{int(asyncio.get_event_loop().time())}",
                "categoryid": 1,
                "summary": "Test course created with Enhanced MoodleClaude",
                "summaryformat": 1
            }]
        }
        
        result = await client.call_webservice("core_course_create_courses", **course_data)
        if result and len(result) > 0:
            course_id = result[0].get('id')
            print(f"✅ Created course with ID: {course_id}")
        else:
            print("❌ Course creation returned empty result")
            return False
    except Exception as e:
        print(f"❌ Course creation failed: {e}")
        return False

    # Test 4: Test available functions
    print("\n⚙️  Test 4: Function Availability")
    test_functions = [
        "core_course_get_contents",
        "core_user_get_users", 
        "core_files_upload",
        "mod_assign_get_assignments",
        "core_completion_get_course_completion_status"
    ]
    
    available_functions = [f.get('name') for f in site_info.get('functions', [])]
    
    for func in test_functions:
        if func in available_functions:
            print(f"✅ {func}")
        else:
            print(f"❌ {func} (not available)")

    print("\n🎉 Enhanced Setup Test Completed Successfully!")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   • Site Info: ✅")
    print(f"   • Course Listing: ✅") 
    print(f"   • Course Creation: ✅")
    print(f"   • Functions Available: {len(available_functions)}")
    print(f"   • Enhanced Token: Working")
    
    return True

async def main():
    """Main test function."""
    try:
        success = await test_enhanced_setup()
        if success:
            print("\n🚀 All tests passed! Enhanced setup is working perfectly! ✨")
            return 0
        else:
            print("\n❌ Some tests failed. Check the output above.")
            return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
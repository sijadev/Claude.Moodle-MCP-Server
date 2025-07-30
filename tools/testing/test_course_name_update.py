#!/usr/bin/env python3
"""
Test script to verify course name update functionality
"""

import asyncio
import logging
from moodle_client import MoodleClient
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_course_name_update():
    """Test that course names are properly updated when reusing courses"""
    config = Config()
    
    if not config.moodle_url or not config.moodle_token:
        print("❌ Missing Moodle credentials - skipping test")
        return
    
    async with MoodleClient(config.moodle_url, config.moodle_token) as client:
        print("🧪 Testing Course Name Update Functionality...")
        
        # Get available courses before the test
        courses_before = await client.get_courses()
        print(f"📚 Available courses before test: {len(courses_before)}")
        
        # Find a test course
        test_course = None
        for course in courses_before:
            if course.get('id', 0) > 1:  # Skip site course
                test_course = course
                break
                
        if not test_course:
            print("❌ No suitable test course found")
            return
            
        original_name = test_course.get('fullname', 'Unknown')
        course_id = test_course['id']
        print(f"📝 Using course ID {course_id}: '{original_name}'")
        
        # Test the update course details function directly
        new_name = "Test Course Name Update - Photography Basics"
        new_description = "This is a test course description for photography basics."
        
        print(f"🔄 Updating course {course_id} name to '{new_name}'...")
        success = await client._update_course_details(course_id, new_name, new_description)
        
        if success:
            print("✅ Course details update reported success")
            
            # Verify the update by fetching courses again
            courses_after = await client.get_courses()
            updated_course = next((c for c in courses_after if c.get('id') == course_id), None)
            
            if updated_course:
                actual_name = updated_course.get('fullname', 'Unknown')
                print(f"📝 Course name in database: '{actual_name}'")
                
                if actual_name == new_name:
                    print("✅ Course name successfully updated in database!")
                else:
                    print(f"⚠️ Course name update may have failed:")
                    print(f"   Expected: '{new_name}'")
                    print(f"   Actual: '{actual_name}'")
            else:
                print("❌ Could not find updated course in results")
        else:
            print("❌ Course details update reported failure")

async def main():
    """Main test function"""
    print("🧪 Course Name Update Test")
    print("=" * 50)
    
    await test_course_name_update()
    
    print("\n" + "=" * 50)
    print("🎯 Course Name Update Test Complete")

if __name__ == "__main__":
    asyncio.run(main())
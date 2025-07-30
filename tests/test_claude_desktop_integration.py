#!/usr/bin/env python3
"""
Test script to debug Claude Desktop integration issues
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from content_parser import ChatContentParser
from content_formatter import ContentFormatter
from moodle_client import MoodleClient

async def test_claude_desktop_integration():
    """Test the same flow that Claude Desktop would use"""
    print("🔧 Testing Claude Desktop Integration")
    print("=" * 60)
    
    # Load configuration
    load_dotenv()
    config = Config()
    
    if not config.moodle_url or not config.moodle_token:
        print("❌ Error: MOODLE_URL and MOODLE_TOKEN environment variables are required")
        return
    
    print(f"🌐 Moodle URL: {config.moodle_url}")
    print(f"🔑 Token configured: {'✅' if config.moodle_token else '❌'}")
    
    # Test sample chat content (similar to what Claude Desktop might send)
    sample_chat = """
    User: Can you explain Python functions and show me some examples?
    
    Assistant: I'd be happy to explain Python functions! Here's what you need to know:
    
    ## What are Python Functions?
    
    Functions are reusable blocks of code that perform specific tasks. They help organize your code and avoid repetition.
    
    ### Basic Function Example
    
    ```python
    def greet(name):
        return f"Hello, {name}!"
    
    # Call the function
    message = greet("World")
    print(message)  # Output: Hello, World!
    ```
    
    ### Function with Multiple Parameters
    
    ```python
    def calculate_area(length, width):
        area = length * width
        return area
    
    # Example usage
    room_area = calculate_area(10, 12)
    print(f"Room area: {room_area} square feet")
    ```
    
    ### Function Benefits
    
    Functions provide several advantages:
    - **Reusability**: Write once, use many times
    - **Organization**: Break complex problems into smaller parts
    - **Testing**: Easier to test individual components
    - **Maintainability**: Changes only need to be made in one place
    """
    
    try:
        print("\n📝 Testing Content Parsing...")
        
        # Initialize parser
        parser = ChatContentParser()
        
        # Parse the chat content
        parsed_content = parser.parse_chat(sample_chat)
        print(f"✅ Parsed content: {len(parsed_content.items)} items found")
        
        # Show what was parsed
        for item in parsed_content.items:
            print(f"   - {item.type}: {item.title}")
        
        print("\n🏗️  Testing Course Creation...")
        
        # Test course creation using the same method as MCP server
        async with MoodleClient(config.moodle_url, config.moodle_token) as client:
            
            # Check existing courses first
            courses = await client.get_courses()
            print(f"📚 Found {len(courses)} existing courses")
            
            course_name = f"Claude Desktop Test Course - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            course_description = "Test course created through Claude Desktop integration testing"
            
            print(f"🎓 Creating course: {course_name}")
            
            # Create course (this uses the same method as MCP server)
            course_id = await client.create_course(
                name=course_name,
                description=course_description,
                category_id=1,
            )
            
            print(f"✅ Course created with ID: {course_id}")
            
            # Test creating a simple section/activity
            print(f"📖 Testing section creation...")
            
            # Try to create a section (if the method exists)
            try:
                section_id = await client.create_section(
                    course_id=course_id,
                    name="Test Section",
                    description="This is a test section created by Claude Desktop integration"
                )
                print(f"✅ Section created with ID: {section_id}")
            except Exception as e:
                print(f"⚠️  Section creation failed: {e}")
            
            # Test page activity creation
            print(f"📄 Testing page activity creation...")
            
            try:
                page_id = await client.create_page_activity(
                    course_id=course_id,
                    section_id=1,  # Use section 1 (General)
                    name="Python Functions Guide",
                    content="""<h2>Python Functions</h2>
                    <p>Functions are essential building blocks in Python programming.</p>
                    <pre><code>def greet(name):
    return f"Hello, {name}!"</code></pre>"""
                )
                print(f"✅ Page activity created with ID: {page_id}")
            except Exception as e:
                print(f"⚠️  Page activity creation failed: {e}")
            
            # Get the final course URL
            course_url = f"{config.moodle_url}/course/view.php?id={course_id}"
            
            print(f"\n🎉 Integration Test Results:")
            print(f"   ✅ Course ID: {course_id}")
            print(f"   ✅ Course Name: {course_name}")
            print(f"   ✅ Course URL: {course_url}")
            print(f"   📱 Direct Link: {course_url}")
            
            # Check if user is enrolled
            print(f"\n👤 Checking user enrollment...")
            try:
                user_courses = await client._call_api('core_enrol_get_users_courses', {'userid': 2})
                enrolled_course_ids = [c.get('id') for c in user_courses]
                
                if course_id in enrolled_course_ids:
                    print(f"   ✅ User is enrolled in the course")
                else:
                    print(f"   ⚠️  User is NOT enrolled in the course")
                    print(f"   💡 This might be why the course doesn't appear in 'My Courses'")
                    
            except Exception as e:
                print(f"   ❌ Could not check enrollment: {e}")
            
            print(f"\n🔍 Debugging Tips:")
            print(f"   1. Check if the course appears at: {course_url}")
            print(f"   2. Go to 'My Courses' page to see if it's listed")
            print(f"   3. If not visible, run: python fix_course_visibility.py")
            print(f"   4. Check Moodle admin settings for course visibility")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_claude_desktop_integration())
#!/usr/bin/env python3
"""
Simulate the exact Claude Desktop workflow for course creation
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from content_parser import ChatContentParser
from content_formatter import ContentFormatter  
from moodle_client import MoodleClient
from models import CourseStructure

async def simulate_claude_desktop_workflow():
    """Simulate exactly what happens when Claude Desktop creates a course"""
    print("🤖 Simulating Claude Desktop Course Creation Workflow")
    print("=" * 60)
    
    load_dotenv()
    
    # Sample chat content that Claude Desktop might send
    sample_chat_content = """
    User: Can you teach me about Python functions? I want to learn the basics and see some practical examples.
    
    Assistant: I'd be happy to teach you about Python functions! Let me break this down into clear sections.
    
    ## Introduction to Python Functions
    
    Functions are reusable blocks of code that perform specific tasks. They're essential for writing clean, organized code.
    
    ### Basic Function Syntax
    
    Here's the basic structure of a Python function:
    
    ```python
    def function_name(parameters):
        \"\"\"Optional docstring\"\"\"
        # Function body
        return result  # Optional
    ```
    
    ### Simple Function Example
    
    Let's start with a basic greeting function:
    
    ```python
    def greet(name):
        \"\"\"Greet a person by name\"\"\"
        return f"Hello, {name}! Welcome to Python programming!"
    
    # Call the function
    message = greet("Alice")
    print(message)  # Output: Hello, Alice! Welcome to Python programming!
    ```
    
    ### Function with Multiple Parameters
    
    Functions can accept multiple parameters:
    
    ```python
    def calculate_rectangle_area(length, width):
        \"\"\"Calculate the area of a rectangle\"\"\"
        area = length * width
        return area
    
    # Example usage
    room_area = calculate_rectangle_area(12, 10)
    print(f"Room area: {room_area} square feet")
    ```
    
    ### Function Benefits
    
    Using functions provides several advantages:
    - **Reusability**: Write once, use many times
    - **Organization**: Break complex problems into smaller parts  
    - **Testing**: Easier to test individual components
    - **Maintainability**: Changes only need to be made in one place
    
    Functions are fundamental to Python programming and you'll use them constantly!
    """
    
    course_name = f"Python Functions Tutorial - Claude Desktop Test {datetime.now().strftime('%H%M%S')}"
    course_description = "A comprehensive tutorial on Python functions created via Claude Desktop integration"
    
    print(f"📝 Simulating MCP tool call:")
    print(f"   Tool: create_course_from_chat")
    print(f"   Chat content: {len(sample_chat_content)} characters")
    print(f"   Course name: {course_name}")
    print(f"   Course description: {course_description}")
    
    try:
        # Step 1: Parse content (like MCP server would)
        print(f"\n🔍 Step 1: Parsing chat content...")
        parser = ChatContentParser()
        parsed_content = parser.parse_chat(sample_chat_content)
        
        print(f"   ✅ Parsed {len(parsed_content.items)} content items:")
        for i, item in enumerate(parsed_content.items, 1):
            print(f"      {i}. {item.type}: {item.title}")
            if hasattr(item, 'language') and item.language:
                print(f"         Language: {item.language}")
                print(f"         Content: {len(item.content)} characters")
        
        # Step 2: Organize into course structure
        print(f"\n🏗️  Step 2: Creating course structure...")
        course_structure = organize_content(parsed_content)
        
        print(f"   ✅ Course structure with {len(course_structure.sections)} sections:")
        for i, section in enumerate(course_structure.sections, 1):
            print(f"      {i}. {section.name} ({len(section.items)} items)")
        
        # Step 3: Create course in Moodle (actual API call)
        print(f"\n🎓 Step 3: Creating course in Moodle...")
        
        async with MoodleClient(os.getenv('MOODLE_URL'), os.getenv('MOODLE_TOKEN')) as client:
            # Get current user (this should work for both Claude Desktop and Claude Code)
            current_user = await client._get_current_user()
            print(f"   👤 Current user: {current_user.get('username')} (ID: {current_user.get('userid')})")
            
            # Create the course
            course_id = await client.create_course(
                name=course_name,
                description=course_description,
                category_id=1,
            )
            
            print(f"   ✅ Course created with ID: {course_id}")
            
            # Step 4: Add content to course  
            print(f"\n📚 Step 4: Adding content to course...")
            created_activities = []
            formatter = ContentFormatter()
            
            for section_idx, section in enumerate(course_structure.sections):
                print(f"   📖 Processing section: {section.name}")
                
                try:
                    section_id = await client.create_section(
                        course_id=course_id,
                        name=section.name,
                        description=section.description or "",
                    )
                    print(f"      ✅ Section created: {section_id}")
                except Exception as e:
                    print(f"      ⚠️  Section creation failed: {e}")
                    section_id = section_idx + 1
                
                for item in section.items:
                    print(f"      📄 Creating activity: {item.title}")
                    
                    try:
                        if item.type == "code":
                            formatted_content = formatter.format_code_for_moodle(
                                code=item.content,
                                language=getattr(item, 'language', 'text'),
                                title=item.title,
                                description=getattr(item, 'description', ''),
                            )
                        elif item.type == "topic":
                            formatted_content = formatter.format_topic_for_moodle(
                                content=item.content,
                                title=item.title,
                                description=getattr(item, 'description', ''),
                            )
                        else:
                            formatted_content = item.content
                        
                        activity_id = await client.create_page_activity(
                            course_id=course_id,
                            section_id=section_id,
                            name=item.title,
                            content=formatted_content,
                        )
                        
                        print(f"         ✅ Activity created: {activity_id}")
                        created_activities.append(activity_id)
                        
                    except Exception as e:
                        print(f"         ⚠️  Activity creation failed: {e}")
            
            # Step 5: Verify enrollment
            print(f"\n👤 Step 5: Verifying user enrollment...")
            
            user_courses = await client._call_api('core_enrol_get_users_courses', {
                'userid': current_user.get('userid')
            })
            
            enrolled_course_ids = [c.get('id') for c in user_courses]
            is_enrolled = course_id in enrolled_course_ids
            
            print(f"   User enrolled in new course: {'✅ YES' if is_enrolled else '❌ NO'}")
            print(f"   Total user courses: {len(user_courses)}")
            
            # Step 6: Generate response (like MCP server would)
            course_url = f"{client.base_url}/course/view.php?id={course_id}"
            
            response = f"""
✅ Course Created Successfully via Claude Desktop Simulation!

📚 Course Details:
• Course ID: {course_id}
• Course Name: {course_name}
• Course URL: {course_url}
• Sections: {len(course_structure.sections)}
• Activities: {len(created_activities)}

📊 Content Analysis:
• Code Items: {len([item for section in course_structure.sections for item in section.items if item.type == 'code'])}
• Topic Items: {len([item for section in course_structure.sections for item in section.items if item.type == 'topic'])}
• Total Items: {len(parsed_content.items)}

👤 User Status:
• User: {current_user.get('username')} (ID: {current_user.get('userid')})
• Enrolled: {'✅ YES' if is_enrolled else '❌ NO'}
• Total Courses: {len(user_courses)}

🔗 Access Your Course:
1. Visit: {course_url}
2. Or go to "My Courses" in Moodle dashboard

⏰ Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            print(f"\n📋 MCP Server Response:")
            print(response)
            
            print(f"\n🎯 Claude Desktop Workflow Test Results:")
            print(f"   ✅ Content parsing: {len(parsed_content.items)} items found")
            print(f"   ✅ Course creation: ID {course_id}")
            print(f"   ✅ Section creation: {len(course_structure.sections)} sections")
            print(f"   ✅ Activity creation: {len(created_activities)} activities")
            print(f"   {'✅' if is_enrolled else '❌'} User enrollment: {'Working' if is_enrolled else 'Failed'}")
            print(f"   🔗 Course URL: {course_url}")
            
            if is_enrolled:
                print(f"\n🎉 SUCCESS: Claude Desktop integration working perfectly!")
                print(f"   The course should appear in 'My Courses' page")
                print(f"   User can access course directly or via dashboard")
            else:
                print(f"\n⚠️  ISSUE: Enrollment may need manual activation")
                print(f"   Course is created but may not appear in 'My Courses'")
                print(f"   Direct URL access should still work")
    
    except Exception as e:
        print(f"❌ Workflow simulation failed: {e}")
        import traceback
        traceback.print_exc()

def organize_content(parsed_content):
    """Organize parsed content into course structure (same logic as MCP server)"""
    from models import CourseStructure
    
    if not parsed_content.items:
        section = CourseStructure.Section(
            name="General Information",
            description="Course information and resources",
            items=[]
        )
        return CourseStructure(sections=[section])
    
    # Group items by topic or create sections based on content type
    sections = []
    current_section_items = []
    current_section_name = "Python Functions Tutorial"
    
    for item in parsed_content.items:
        current_section_items.append(item)
    
    if current_section_items:
        section = CourseStructure.Section(
            name=current_section_name,
            description="Comprehensive tutorial on Python functions with examples",
            items=current_section_items
        )
        sections.append(section)
    
    return CourseStructure(sections=sections)

if __name__ == "__main__":
    asyncio.run(simulate_claude_desktop_workflow())
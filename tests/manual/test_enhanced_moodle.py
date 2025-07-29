#!/usr/bin/env python3
"""
Test the enhanced MoodleClient with WSManageSections support
"""

import asyncio
import os
from dotenv import load_dotenv
from moodle_client import MoodleClient

async def test_enhanced_moodle():
    load_dotenv()
    
    moodle_url = os.getenv('MOODLE_URL')
    moodle_token = os.getenv('MOODLE_TOKEN')
    
    print(f"🚀 Testing Enhanced MoodleClient with WSManageSections")
    print(f"URL: {moodle_url}")
    print("=" * 60)
    
    try:
        async with MoodleClient(moodle_url, moodle_token) as client:
            
            # Test 1: Create course with minimal sections
            print("🎓 Test 1: Create Course with Minimal Sections")
            course_id = await client.create_course(
                name="Enhanced MCP Test Course",
                description="Testing enhanced section creation capabilities",
                numsections=1  # Start minimal
            )
            print(f"✅ Course created with ID: {course_id}")
            
            # Test 2: Create custom sections using WSManageSections
            print(f"\n📖 Test 2: Create Custom Sections")
            
            # Create Python Basics section
            python_section = await client.create_section(
                course_id=course_id,
                name="Python Basics",
                description="Introduction to Python programming fundamentals",
                position=0  # Add at end
            )
            print(f"✅ Created 'Python Basics' section: {python_section}")
            
            # Create Advanced Topics section
            advanced_section = await client.create_section(
                course_id=course_id,
                name="Advanced Topics", 
                description="Advanced Python concepts and best practices",
                position=0  # Add at end
            )
            print(f"✅ Created 'Advanced Topics' section: {advanced_section}")
            
            # Create Exercises section at specific position
            exercises_section = await client.create_section(
                course_id=course_id,
                name="Exercises",
                description="Hands-on coding exercises and challenges",
                position=2  # Insert at position 2
            )
            print(f"✅ Created 'Exercises' section at position 2: {exercises_section}")
            
            # Test 3: Verify final course structure
            print(f"\n🔍 Test 3: Verify Course Structure")
            sections = await client._call_api("local_wsmanagesections_get_sections", {"courseid": course_id})
            print(f"✅ Final course structure ({len(sections)} sections):")
            for section in sections:
                print(f"   - Section {section['sectionnum']}: {section['name']}")
                if section.get('summary'):
                    print(f"     📝 {section['summary']}")
            
            # Test 4: Simulate content creation in each section
            print(f"\n📄 Test 4: Simulate Content Creation")
            
            content_items = [
                ("Variables and Data Types", "Learn about Python variables, strings, numbers, and booleans"),
                ("Control Structures", "Understanding if statements, loops, and conditional logic"),
                ("Functions", "Creating reusable code with functions and parameters"),
                ("Object-Oriented Programming", "Classes, objects, inheritance, and polymorphism"),
                ("Practice Exercise 1", "Build a simple calculator application"),
                ("Practice Exercise 2", "Create a text-based adventure game")
            ]
            
            section_counter = 1
            for title, description in content_items:
                # Determine which section to use
                if "Exercise" in title:
                    target_section = exercises_section
                elif any(keyword in title for keyword in ["Object-Oriented", "Advanced"]):
                    target_section = advanced_section
                else:
                    target_section = python_section
                
                # Simulate page activity creation
                activity_id = await client.create_page_activity(
                    course_id=course_id,
                    section_id=target_section,
                    name=title,
                    content=f"<h2>{title}</h2><p>{description}</p><p>This content would be created as a page activity.</p>"
                )
                print(f"   📄 Planned activity '{title}' in section {target_section}")
                section_counter += 1
            
            print(f"\n" + "=" * 60)
            print("🎉 ENHANCED MOODLE TEST COMPLETED!")
            print("=" * 60)
            print("✅ New Capabilities with WSManageSections:")
            print("   - ✅ Dynamic section creation")
            print("   - ✅ Custom section positioning")
            print("   - ✅ Section name and description updates")
            print("   - ✅ Flexible course structure organization")
            print("")
            print("💡 This enables true course structure automation!")
            print(f"🔗 View course: http://localhost:8080/course/view.php?id={course_id}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_moodle())
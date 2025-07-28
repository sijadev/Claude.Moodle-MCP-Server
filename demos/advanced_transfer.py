#!/usr/bin/env python3
"""
Advanced Moodle transfer with sections - tries different approaches to create sections
Enhanced with EnhancedMoodleAPI capabilities for better section management
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
from enhanced_moodle_claude import EnhancedMoodleAPI, SectionConfig


async def create_course_with_sections():
    """Create a course and try to add sections using different methods"""
    moodle_url = os.getenv("MOODLE_URL", "http://localhost:8080")
    moodle_token = os.getenv("MOODLE_TOKEN", "b2021a7a41309b8c58ad026a751d0cd0")

    course_name = "Python Kurs - Mit Sektionen"
    course_description = "Ein Python-Kurs mit verschiedenen Sektionen für strukturierten Aufbau."

    try:
        async with MoodleClient(moodle_url, moodle_token) as client:
            print(f"🎓 Creating course: '{course_name}'")

            # Create course
            course_id = await client.create_course(
                name=course_name, description=course_description, category_id=1
            )

            print(f"✅ Course created with ID: {course_id}")

            # Try different approaches to create sections
            sections_to_create = [
                {
                    "name": "1. Python Grundlagen",
                    "description": "Einführung in Python-Syntax und Grundkonzepte",
                },
                {"name": "2. Datentypen", "description": "Strings, Listen, Dictionaries und mehr"},
                {
                    "name": "3. Kontrollstrukturen",
                    "description": "If-Statements, Schleifen und Funktionen",
                },
                {
                    "name": "4. Praktische Übungen",
                    "description": "Hands-on Coding mit realen Beispielen",
                },
            ]

            created_sections = []

            for i, section_info in enumerate(sections_to_create):
                print(f"\n📖 Attempting to create section: '{section_info['name']}'")

                try:
                    # Method 1: Try the modified create_section method
                    section_id = await client.create_section(
                        course_id=course_id,
                        name=section_info["name"],
                        description=section_info["description"],
                    )

                    print(f"✅ Section created with ID: {section_id}")
                    created_sections.append(
                        {
                            "id": section_id,
                            "name": section_info["name"],
                            "description": section_info["description"],
                        }
                    )

                    # Try to add some content to each section
                    await add_content_to_section(client, course_id, section_id, section_info, i)

                except Exception as e:
                    print(f"⚠️  Section creation method failed: {e}")
                    # Try alternative method
                    await try_alternative_section_creation(client, course_id, section_info, i)

            # Final summary
            print(f"\n" + "=" * 60)
            print(f"🎉 COURSE CREATION SUMMARY")
            print(f"=" * 60)
            print(f"✅ Course: '{course_name}' (ID: {course_id})")
            print(f"✅ Sections attempted: {len(sections_to_create)}")
            print(f"✅ Sections created: {len(created_sections)}")
            print(f"🌐 Course URL: {moodle_url}/course/view.php?id={course_id}")

            if created_sections:
                print(f"\nCreated sections:")
                for section in created_sections:
                    print(f"  - {section['name']} (ID: {section['id']})")

            return course_id

    except Exception as e:
        print(f"❌ Error creating course: {e}")
        return None


async def add_content_to_section(client, course_id, section_id, section_info, section_index):
    """Add content to a specific section"""
    print(f"   📝 Adding content to section {section_id}...")

    # Create content based on section
    if section_index == 0:  # Python Grundlagen
        content = """
        <h3>Python Grundlagen</h3>
        <p>Python ist eine interpreted, high-level Programmiersprache mit dynamischer Semantik.</p>
        
        <h4>Erstes Python Programm:</h4>
        <div style="background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 15px; margin: 10px 0;">
            <pre><code>print("Hallo Python!")
name = "Welt"
print(f"Hallo {name}!")</code></pre>
        </div>
        """

    elif section_index == 1:  # Datentypen
        content = """
        <h3>Python Datentypen</h3>
        <p>Python hat verschiedene eingebaute Datentypen für verschiedene Arten von Daten.</p>
        
        <h4>Grundlegende Datentypen:</h4>
        <div style="background-color: #f8f9fa; border-left: 4px solid #28a745; padding: 15px; margin: 10px 0;">
            <pre><code># Zahlen
alter = 25
pi = 3.14159

# Strings
name = "Python"
beschreibung = "Eine tolle Sprache"

# Listen
farben = ["rot", "grün", "blau"]
zahlen = [1, 2, 3, 4, 5]

# Dictionary
person = {"name": "Max", "alter": 30}</code></pre>
        </div>
        """

    elif section_index == 2:  # Kontrollstrukturen
        content = """
        <h3>Kontrollstrukturen in Python</h3>
        <p>Mit Kontrollstrukturen steuern wir den Programmfluss.</p>
        
        <h4>If-Statements und Schleifen:</h4>
        <div style="background-color: #f8f9fa; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0;">
            <pre><code># If-Statement
alter = 18
if alter >= 18:
    print("Volljährig")
else:
    print("Minderjährig")

# For-Schleife
for i in range(5):
    print(f"Zahl: {i}")

# Funktion
def begruessung(name):
    return f"Hallo {name}!"</code></pre>
        </div>
        """

    else:  # Praktische Übungen
        content = """
        <h3>Praktische Python Übungen</h3>
        <p>Jetzt setzen wir das Gelernte in die Praxis um!</p>
        
        <h4>Übung: Einfacher Taschenrechner</h4>
        <div style="background-color: #f8f9fa; border-left: 4px solid #dc3545; padding: 15px; margin: 10px 0;">
            <pre><code>def taschenrechner(a, b, operation):
    if operation == "+":
        return a + b
    elif operation == "-":
        return a - b
    elif operation == "*":
        return a * b
    elif operation == "/":
        return a / b if b != 0 else "Division durch Null!"
    else:
        return "Unbekannte Operation"

# Test
result = taschenrechner(10, 5, "+")
print(f"Ergebnis: {result}")</code></pre>
        </div>
        
        <h4>Aufgabe für dich:</h4>
        <ul>
            <li>Erweitere den Taschenrechner um Potenzierung (**)</li>
            <li>Füge eine Benutzeroberfläche hinzu</li>
            <li>Implementiere eine Verlaufsanzeige</li>
        </ul>
        """

    try:
        activity_id = await client.create_page_activity(
            course_id=course_id,
            section_id=section_id,
            name=f"{section_info['name']} - Inhalt",
            content=content,
        )
        print(f"   ✅ Content added to section (Activity ID: {activity_id})")

    except Exception as e:
        print(f"   ⚠️  Could not add content to section: {e}")


async def try_alternative_section_creation(client, course_id, section_info, section_index):
    """Try alternative methods to create section-like content"""
    print(f"   🔄 Trying alternative approach for: '{section_info['name']}'")

    # Create a label or page that acts like a section header
    section_header_content = f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h2 style="margin: 0; color: white;">{section_info['name']}</h2>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">{section_info['description']}</p>
    </div>
    """

    try:
        # Use section 0 (general section) and create a page that looks like a section header
        header_id = await client.create_page_activity(
            course_id=course_id,
            section_id=0,  # General section
            name=f"📖 {section_info['name']}",
            content=section_header_content,
        )

        print(f"   ✅ Section-style header created (ID: {header_id})")

        # Add the content right after the header
        await add_content_to_section(client, course_id, 0, section_info, section_index)

    except Exception as e:
        print(f"   ❌ Alternative method also failed: {e}")


async def main():
    print("🚀 MoodleClaude - Advanced Transfer with Sections")
    print("=" * 55)

    # Set environment variables if needed
    if not os.getenv("MOODLE_URL"):
        os.environ["MOODLE_URL"] = "http://localhost:8080"
    if not os.getenv("MOODLE_TOKEN"):
        os.environ["MOODLE_TOKEN"] = "b2021a7a41309b8c58ad026a751d0cd0"

    print(f"Connecting to: {os.getenv('MOODLE_URL')}")
    print(f"Using token: {os.getenv('MOODLE_TOKEN')[:10]}...")

    course_id = await create_course_with_sections()

    if course_id:
        print(f"\n🎉 SUCCESS!")
        print(f"Kurs mit Sektionen wurde erstellt!")
        print(f"Kurs-ID: {course_id}")
        print(f"URL: {os.getenv('MOODLE_URL')}/course/view.php?id={course_id}")
    else:
        print(f"\n❌ Transfer fehlgeschlagen")


async def create_course_with_enhanced_api():
    """Create a course using the Enhanced Moodle API with advanced section features"""
    
    moodle_url = os.getenv("MOODLE_URL", "http://localhost:8080")
    moodle_token = os.getenv("MOODLE_TOKEN", "b2021a7a41309b8c58ad026a751d0cd0")
    
    print(f"\n🔥 ENHANCED API DEMO - Advanced Section Management")
    print(f"=" * 70)
    
    try:
        # Initialize Enhanced API
        api = EnhancedMoodleAPI(moodle_url, moodle_token)
        
        # Create course using enhanced API
        course_name = "Advanced Python Course - Enhanced Sections"
        course_description = """
        <h3>🚀 Advanced Python Course</h3>
        <p>This course demonstrates the power of the Enhanced Moodle API with:</p>
        <ul>
            <li>✅ Advanced section management</li>
            <li>🔒 Availability conditions</li>
            <li>📊 Bulk operations</li>
            <li>🎯 Structured content delivery</li>
        </ul>
        """
        
        # Create course first using proper parameter format
        import time
        shortname = f"python_enhanced_{int(time.time())}"
        
        params = {
            "courses[0][fullname]": course_name,
            "courses[0][shortname]": shortname,
            "courses[0][categoryid]": 1,
            "courses[0][summary]": course_description,
            "courses[0][summaryformat]": 1,  # HTML format
            "courses[0][format]": "topics",  # Course format
            "courses[0][visible]": 1,  # Visible
            "courses[0][numsections]": 5,  # Create 5 sections upfront
        }
        
        course_response = api._make_request("core_course_create_courses", params)
        course_id = course_response[0]["id"]
        
        print(f"✅ Course created with Enhanced API: {course_id}")
        
        # Define advanced sections with different configurations
        enhanced_sections = [
            SectionConfig(
                name="🎯 Course Introduction",
                summary="<p><strong>Welcome!</strong> Start your Python journey here.</p>",
                visible=True
            ),
            SectionConfig(
                name="📚 Python Fundamentals", 
                summary="<p>Core concepts: variables, data types, operators</p>",
                visible=True
            ),
            SectionConfig(
                name="🔧 Control Structures",
                summary="<p>Loops, conditions, and program flow</p>",
                visible=True
            ),
            SectionConfig(
                name="📊 Data Structures", 
                summary="<p>Lists, dictionaries, sets, and tuples</p>",
                visible=True
            ),
            SectionConfig(
                name="⚙️ Functions & Modules",
                summary="<p>Code organization and reusability</p>",
                visible=True
            )
        ]
        
        # Create sections using Enhanced API
        created_sections = []
        for i, section_config in enumerate(enhanced_sections, 1):
            print(f"📝 Creating enhanced section {i}: {section_config.name}")
            
            try:
                section_result = await api.create_course_section(course_id, section_config)
                created_sections.append({
                    "id": section_result.get("id"),
                    "name": section_config.name,
                    "visible": section_config.visible
                })
                print(f"   ✅ Section created: ID {section_result.get('id')}")
                
            except Exception as e:
                print(f"   ❌ Failed to create section: {e}")
        
        # Demonstrate section update
        if created_sections:
            print(f"\n🔧 Demonstrating section update...")
            try:
                section_to_update = created_sections[0]
                await api.update_section(section_to_update['id'], {
                    "name": f"✨ {section_to_update['name']} (Enhanced!)",
                    "summary": "<p><strong>Updated using Enhanced API!</strong></p>"
                })
                print(f"   ✅ Section updated successfully")
            except Exception as e:
                print(f"   ❌ Section update failed: {e}")
        
        # Final summary
        print(f"\n" + "=" * 70)
        print(f"🎉 ENHANCED API DEMO COMPLETED!")
        print(f"=" * 70)
        print(f"🎓 Course: {course_name}")
        print(f"🆔 Course ID: {course_id}")
        print(f"📊 Sections created: {len(created_sections)}")
        print(f"🌐 Course URL: {moodle_url}/course/view.php?id={course_id}")
        
        return course_id, created_sections
        
    except Exception as e:
        print(f"❌ Enhanced API demo failed: {e}")
        import traceback
        traceback.print_exc()
        return None, []


if __name__ == "__main__":
    print("🚀 Advanced Moodle Section Management Demo")
    print("Choose your demo:")
    print("1. Traditional approach (original)")
    print("2. Enhanced API approach (new)")
    
    try:
        choice = input("Enter choice (1-2) or press Enter for Enhanced API: ").strip()
        
        if choice == "1":
            asyncio.run(main())
        else:  # Default to Enhanced API
            asyncio.run(create_course_with_enhanced_api())
            
    except KeyboardInterrupt:
        print("\n👋 Demo cancelled by user")

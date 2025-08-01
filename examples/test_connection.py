#!/usr/bin/env python3
"""
Test Moodle connection and create course
"""

import asyncio
import os

from moodle_client import MoodleAPIError, MoodleClient


async def test_connection():
    """Test the Moodle connection"""
    moodle_url = os.getenv("MOODLE_URL")
    moodle_token = os.getenv("MOODLE_TOKEN")

    print(f"Testing connection to: {moodle_url}")
    print(f"Using token: {moodle_token[:10]}...")

    try:
        async with MoodleClient(moodle_url, moodle_token) as client:
            print("✅ Client created successfully")

            # Test basic API call
            courses = await client.get_courses()
            print(f"✅ API connection successful - found {len(courses)} courses")

            if courses:
                print("Existing courses:")
                for course in courses[:3]:  # Show first 3 courses
                    print(
                        f"  - ID: {course.get('id')}, Name: {course.get('fullname', 'Unknown')}"
                    )

            return True

    except MoodleAPIError as e:
        print(f"❌ Moodle API Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False


async def create_python_course():
    """Create the Python course with generated content"""
    moodle_url = os.getenv("MOODLE_URL")
    moodle_token = os.getenv("MOODLE_TOKEN")

    course_name = "Python Programmierung - Einführungskurs"
    course_description = "Ein Einführungskurs in die Python-Programmierung mit praktischen Beispielen und Code-Übungen."

    try:
        async with MoodleClient(moodle_url, moodle_token) as client:
            print(f"🎓 Creating course: '{course_name}'")

            # Create course
            course_id = await client.create_course(
                name=course_name, description=course_description, category_id=1
            )

            print(f"✅ Course created with ID: {course_id}")

            # Create section
            section_id = await client.create_section(
                course_id=course_id,
                name="Python Grundlagen",
                description="Einführung in die Python-Programmierung mit praktischen Beispielen",
            )

            print(f"✅ Section created with ID: {section_id}")

            # Create introduction page
            intro_content = """
            <h2>Willkommen zum Python-Kurs!</h2>
            
            <p>Python ist eine der beliebtesten Programmiersprachen der Welt und eignet sich hervorragend für Einsteiger. 
            Mit ihrer klaren Syntax und vielseitigen Anwendungsmöglichkeiten ist Python ideal für:</p>
            
            <ul>
                <li><strong>Webentwicklung</strong> - Frameworks wie Django und Flask</li>
                <li><strong>Datenanalyse</strong> - Bibliotheken wie Pandas und NumPy</li>
                <li><strong>Künstliche Intelligenz</strong> - Machine Learning mit TensorFlow</li>
                <li><strong>Automation</strong> - Skripte und Tools für den Alltag</li>
            </ul>
            
            <h3>Warum Python lernen?</h3>
            <ul>
                <li>🔤 <strong>Einfache Syntax</strong>: Python Code ist leicht zu lesen und zu verstehen</li>
                <li>🔧 <strong>Vielseitigkeit</strong>: Von Webapps bis zu Machine Learning</li>
                <li>👥 <strong>Große Community</strong>: Unzählige Bibliotheken und hilfreiche Ressourcen</li>
                <li>💼 <strong>Karrieremöglichkeiten</strong>: Hohe Nachfrage in der Tech-Branche</li>
            </ul>
            
            <p><em>Viel Erfolg beim Lernen!</em></p>
            """

            intro_activity = await client.create_page_activity(
                course_id=course_id,
                section_id=section_id,
                name="Python Einführung",
                content=intro_content,
            )

            print(f"✅ Introduction page created with ID: {intro_activity}")

            # Create first code example
            hello_code = """# Einfaches "Hallo Welt" Programm
def begruessung(name):
    return f"Hallo {name}! Willkommen bei Python!"

# Programm ausführen
benutzername = "Max"
nachricht = begruessung(benutzername)
print(nachricht)

# Ausgabe: Hallo Max! Willkommen bei Python!"""

            code_content = f"""
            <h3>Erstes Python Beispiel</h3>
            <p>Hier ist ein einfaches Python-Programm, das zeigt, wie Funktionen und String-Formatting funktionieren:</p>
            
            <div style="background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 5px; padding: 15px; margin: 10px 0;">
                <pre><code class="language-python">{hello_code}</code></pre>
            </div>
            
            <h4>Erklärung:</h4>
            <ul>
                <li><code>def begruessung(name):</code> - Definiert eine Funktion namens "begruessung"</li>
                <li><code>f"Hallo {{name}}!"</code> - Verwendet f-string Formatting für dynamische Texte</li>
                <li><code>return</code> - Gibt das Ergebnis der Funktion zurück</li>
                <li><code>print()</code> - Zeigt das Ergebnis auf der Konsole an</li>
            </ul>
            
            <p><strong>Übung:</strong> Versuche den Code zu ändern und deinen eigenen Namen zu verwenden!</p>
            """

            code_activity = await client.create_page_activity(
                course_id=course_id,
                section_id=section_id,
                name="Erstes Python Beispiel",
                content=code_content,
            )

            print(f"✅ Code example page created with ID: {code_activity}")

            # Create downloadable file
            file_activity = await client.create_file_activity(
                course_id=course_id,
                section_id=section_id,
                name="Python Code zum Download",
                content=hello_code,
                filename="hello_world.py",
            )

            print(f"✅ Downloadable file created with ID: {file_activity}")

            print(f"\n🎉 Course successfully created!")
            print(f"📍 Course URL: {moodle_url}/course/view.php?id={course_id}")

            return course_id

    except MoodleAPIError as e:
        print(f"❌ Failed to create course: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


async def main():
    print("🚀 MoodleClaude - Live Transfer Test")
    print("=" * 50)

    # Test connection first
    if await test_connection():
        print("\n" + "=" * 50)
        print("Creating course with generated content...")
        print("=" * 50)

        course_id = await create_python_course()

        if course_id:
            print(f"\n✅ SUCCESS! Course created with ID: {course_id}")
            print(
                f"🌐 Access your course at: {os.getenv('MOODLE_URL')}/course/view.php?id={course_id}"
            )
        else:
            print("\n❌ Failed to create course")
    else:
        print("\n❌ Connection test failed - cannot proceed with course creation")


if __name__ == "__main__":
    asyncio.run(main())

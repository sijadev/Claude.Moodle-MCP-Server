#!/usr/bin/env python3
"""
Simplified Moodle transfer - just create course with basic content
"""

import asyncio
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from moodle_client import MoodleAPIError, MoodleClient


async def create_simple_course():
    """Create a simple course with the generated content"""
    moodle_url = os.getenv("MOODLE_URL")
    moodle_token = os.getenv("MOODLE_TOKEN")

    course_name = "Python Programmierung - Einführung"
    course_description = """
    <h2>Python Programmierung - Einführungskurs</h2>
    
    <p>Python ist eine der beliebtesten Programmiersprachen der Welt und eignet sich hervorragend für Einsteiger. 
    Mit ihrer klaren Syntax und vielseitigen Anwendungsmöglichkeiten ist Python ideal für Webentwicklung, 
    Datenanalyse, Künstliche Intelligenz und vieles mehr.</p>
    
    <h3>Warum Python lernen?</h3>
    <ul>
        <li><strong>Einfache Syntax</strong>: Python Code ist leicht zu lesen und zu verstehen</li>
        <li><strong>Vielseitigkeit</strong>: Von Webapps bis zu Machine Learning</li>
        <li><strong>Große Community</strong>: Unzählige Bibliotheken und hilfreiche Ressourcen</li>
        <li><strong>Karrieremöglichkeiten</strong>: Hohe Nachfrage in der Tech-Branche</li>
    </ul>
    
    <h3>Erstes Beispiel</h3>
    <div style="background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 5px; padding: 15px; margin: 10px 0;">
        <pre><code># Einfaches "Hallo Welt" Programm
def begruessung(name):
    return f"Hallo {name}! Willkommen bei Python!"

# Programm ausführen
benutzername = "Max"
nachricht = begruessung(benutzername)
print(nachricht)</code></pre>
    </div>
    
    <p>Dieses Beispiel zeigt die Grundlagen von Python-Funktionen und String-Formatting.</p>
    
    <p><em>Viel Erfolg beim Lernen!</em></p>
    """

    try:
        async with MoodleClient(moodle_url, moodle_token) as client:
            print(f"🎓 Creating course: '{course_name}'")

            # Create course with embedded content
            course_id = await client.create_course(
                name=course_name, description=course_description, category_id=1
            )

            print(f"✅ Course created successfully!")
            print(f"📍 Course ID: {course_id}")
            print(f"🌐 Course URL: {moodle_url}/course/view.php?id={course_id}")

            return course_id

    except MoodleAPIError as e:
        print(f"❌ Moodle API Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


async def main():
    print("🚀 MoodleClaude - Simplified Transfer")
    print("=" * 40)

    # Set environment variables
    moodle_url = "http://localhost"
    moodle_token = "your-moodle-token-here"

    os.environ["MOODLE_URL"] = moodle_url
    os.environ["MOODLE_TOKEN"] = moodle_token

    print(f"Connecting to: {moodle_url}")
    print(f"Using token: {moodle_token[:10]}...")

    course_id = await create_simple_course()

    if course_id:
        print(f"\n🎉 SUCCESS!")
        print(f"Der generierte Python-Text wurde erfolgreich nach Moodle übertragen!")
        print(f"Kurs-ID: {course_id}")
        print(f"URL: {moodle_url}/course/view.php?id={course_id}")
    else:
        print(f"\n❌ Transfer fehlgeschlagen")


if __name__ == "__main__":
    asyncio.run(main())

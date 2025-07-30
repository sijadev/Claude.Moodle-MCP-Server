#!/usr/bin/env python3
"""
Debug script to understand what happens during course creation
"""

import asyncio
import logging
from mcp_server import MoodleMCPServer
from content_parser import ChatContentParser
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_course_creation():
    """Debug the course creation process"""
    
    # The exact content from the user's example
    chat_content = """Digitale Fotografie für Einsteiger

## Kursübersicht
Willkommen zum Kurs "Digitale Fotografie für Einsteiger"! In diesem Kurs lernen Sie die Grundlagen der digitalen Fotografie kennen und entwickeln praktische Fähigkeiten für bessere Fotos.

## Modul 1: Kamera-Grundlagen
### Die Kamera verstehen
- Verschiedene Kameratypen (DSLR, Spiegellos, Smartphone)
- Wichtige Bedienelemente
- Grundeinstellungen

### Objektive und Brennweiten
- Weitwinkel vs. Teleobjektiv
- Festbrennweite vs. Zoom
- Blende und Schärfentiefe

## Modul 2: Belichtung meistern
### Das Belichtungsdreieck
- Blende (Aperture)
- Verschlusszeit (Shutter Speed) 
- ISO-Wert

### Belichtungsmodi
- Automatik vs. manuelle Modi
- Zeitautomatik (A/Av-Modus)
- Blendenautomatik (S/Tv-Modus)
- Manueller Modus

## Modul 3: Bildkomposition
### Gestaltungsregeln
- Drittel-Regel
- Führende Linien
- Symmetrie und Muster
- Vorder-, Mittel- und Hintergrund

### Licht und Schatten
- Goldene Stunde
- Hartes vs. weiches Licht
- Gegenlicht kreativ nutzen

## Modul 4: Praktische Übungen
### Fotoprojekte
- Porträtfotografie
- Landschaftsaufnahmen
- Streetfotografie
- Makrofotografie

### Bildbearbeitung Grundlagen
- RAW vs. JPEG
- Grundlegende Korrekturen
- Einfache Bildverbesserungen

## Abschlussprojekt
Erstellen Sie eine kleine Fotoserie (5-10 Bilder) zu einem selbst gewählten Thema und wenden Sie die gelernten Techniken an.

## Zusätzliche Ressourcen
- Empfohlene Ausrüstung für Einsteiger
- Weiterführende Literatur
- Online-Communities für Fotografen"""

    course_name = "Digitale Fotografie für Einsteiger"
    course_description = "Ein umfassender Einsteigerkurs in die digitale Fotografie mit praktischen Übungen und Projekten"
    
    print("🧪 Debugging Course Creation Process")
    print("=" * 60)
    
    # Step 1: Test content parsing
    print("1️⃣ Testing Content Parsing...")
    parser = ChatContentParser()
    parsed_content = parser.parse_chat(chat_content)
    
    print(f"   📊 Parsed {len(parsed_content.items)} items")
    for i, item in enumerate(parsed_content.items, 1):
        print(f"   {i}. {item.type}: {item.title[:50]}...")
    
    # Step 2: Test MCP server response
    print("\n2️⃣ Testing MCP Server Process...")
    server = MoodleMCPServer()
    
    if not server.moodle_client:
        print("   ❌ No Moodle client available")
        return
    
    # Simulate the course creation request
    arguments = {
        "chat_content": chat_content,
        "course_name": course_name,
        "course_description": course_description,
        "category_id": 1
    }
    
    print("   🔄 Calling _create_course_from_chat...")
    result = await server._create_course_from_chat(arguments)
    
    if result:
        response_text = result[0].text if result else "No response"
        print("   📝 MCP Server Response:")
        print("   " + "─" * 50)
        print(response_text)
        
        # Try to extract course ID from response
        lines = response_text.split('\n')
        course_id = None
        for line in lines:
            if "Course ID:" in line:
                try:
                    course_id = int(line.split("Course ID:")[1].strip().split()[0])
                    break
                except:
                    pass
        
        print(f"\n   🎯 Extracted Course ID: {course_id}")
        return course_id
    else:
        print("   ❌ No response from MCP server")
        return None

async def check_database_after_creation(course_id):
    """Check what actually exists in the database"""
    if not course_id:
        print("❌ No course ID to check")
        return
    
    print(f"\n3️⃣ Checking Database for Course ID {course_id}...")
    
    # We'll just print instructions since we can't run Docker commands from here
    print(f"   🔍 Run this command to check the database:")
    print(f"   docker exec moodleclaude_db mariadb -u root bitnami_moodle -e \"SELECT id, fullname, shortname, summary FROM mdl_course WHERE id = {course_id};\"")
    print(f"   docker exec moodleclaude_db mariadb -u root bitnami_moodle -e \"SELECT course, section, name, summary FROM mdl_course_sections WHERE course = {course_id} ORDER BY section;\"")

async def main():
    """Main debug function"""
    course_id = await debug_course_creation()
    await check_database_after_creation(course_id)
    
    print("\n" + "=" * 60)
    print("🎯 Debug Summary:")
    print("This script shows the complete flow from content parsing to MCP response")
    print("Check the database manually to see what actually gets stored")

if __name__ == "__main__":
    asyncio.run(main())
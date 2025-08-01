#!/usr/bin/env python3
"""
Debug Moodle API Specification
==============================
Überprüft die genaue API-Spezifikation für core_course_create_courses.
"""

import asyncio
import aiohttp
import json
import os
from pathlib import Path
import urllib.parse

# Load configuration
PROJECT_ROOT = Path(__file__).parent.parent
config_file = PROJECT_ROOT / "config" / "moodle_tokens.env"

config = {}
if config_file.exists():
    with open(config_file, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key] = value.strip('"\'')

MOODLE_URL = config.get('MOODLE_URL', 'http://localhost:8080')
MOODLE_TOKEN = config.get('MOODLE_ADMIN_TOKEN', '')

class MoodleAPIClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

async def get_api_documentation():
    """Rufe die API-Dokumentation direkt von Moodle ab."""
    print("📚 Moodle API-Dokumentation abrufen...")
    
    async with aiohttp.ClientSession() as session:
        # Try to get web service documentation from Moodle
        doc_url = f"{MOODLE_URL}/admin/webservice/documentation.php?wstoken={MOODLE_TOKEN}"
        
        try:
            async with session.get(doc_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Look for course creation function documentation
                    if 'core_course_create_courses' in content:
                        print("✅ Gefunden: core_course_create_courses Dokumentation")
                        
                        # Extract relevant parts (simplified)
                        start = content.find('core_course_create_courses')
                        if start > -1:
                            end = content.find('</div>', start + 1000)  # Approximate end
                            if end > start:
                                doc_section = content[start:end]
                                print("📖 Relevante Dokumentation gefunden")
                                return True
                    else:
                        print("❌ core_course_create_courses nicht in Dokumentation gefunden")
                else:
                    print(f"❌ Dokumentation nicht zugänglich: HTTP {response.status}")
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Dokumentation: {e}")
    
    return False

async def test_direct_api_call():
    """Teste direkte API-Aufrufe mit verschiedenen Methoden."""
    print("\n🧪 Teste direkte API-Aufrufe...")
    
    async with aiohttp.ClientSession() as session:
        url = f"{MOODLE_URL}/webservice/rest/server.php"
        
        # Test 1: GET Request (manchmal funktioniert das)
        print("\n📋 Test 1: GET Request")
        params = {
            'wstoken': MOODLE_TOKEN,
            'wsfunction': 'core_course_create_courses',
            'moodlewsrestformat': 'json',
            'courses[0][fullname]': 'Test Course GET',
            'courses[0][shortname]': 'testget',
            'courses[0][categoryid]': '1'
        }
        
        try:
            async with session.get(url, params=params) as response:
                result = await response.json()
                print(f"   Status: {response.status}")
                print(f"   Result: {result}")
        except Exception as e:
            print(f"   ❌ GET Request Fehler: {e}")
        
        # Test 2: POST mit Form-Encoding
        print("\n📋 Test 2: POST Form-Encoding")
        data = {
            'wstoken': MOODLE_TOKEN,
            'wsfunction': 'core_course_create_courses',
            'moodlewsrestformat': 'json',
            'courses[0][fullname]': 'Test Course POST',
            'courses[0][shortname]': 'testpost',
            'courses[0][categoryid]': '1'
        }
        
        try:
            async with session.post(url, data=data) as response:
                result = await response.json()
                print(f"   Status: {response.status}")
                print(f"   Result: {result}")
        except Exception as e:
            print(f"   ❌ POST Form Fehler: {e}")
        
        # Test 3: POST mit JSON (falls Moodle das unterstützt)
        print("\n📋 Test 3: POST JSON")
        json_data = {
            'wstoken': MOODLE_TOKEN,
            'wsfunction': 'core_course_create_courses',
            'moodlewsrestformat': 'json',
            'courses': [
                {
                    'fullname': 'Test Course JSON',
                    'shortname': 'testjson',
                    'categoryid': 1
                }
            ]
        }
        
        try:
            async with session.post(url, json=json_data) as response:
                result = await response.json()
                print(f"   Status: {response.status}")
                print(f"   Result: {result}")
        except Exception as e:
            print(f"   ❌ POST JSON Fehler: {e}")

async def test_minimal_course_creation():
    """Teste mit absolut minimalen Parametern."""
    print("\n🔬 Teste absolut minimale Parameter...")
    
    async with aiohttp.ClientSession() as session:
        url = f"{MOODLE_URL}/webservice/rest/server.php"
        
        # Nur die absolut notwendigen Parameter
        test_cases = [
            {
                'name': 'Nur erforderliche Felder',
                'data': {
                    'wstoken': MOODLE_TOKEN,
                    'wsfunction': 'core_course_create_courses',
                    'moodlewsrestformat': 'json',
                    'courses[0][fullname]': 'Minimal Test',
                    'courses[0][shortname]': 'minimal',
                    'courses[0][categoryid]': 1
                }
            },
            {
                'name': 'Mit String categoryid',
                'data': {
                    'wstoken': MOODLE_TOKEN,
                    'wsfunction': 'core_course_create_courses',
                    'moodlewsrestformat': 'json',
                    'courses[0][fullname]': 'String Cat Test',
                    'courses[0][shortname]': 'stringcat',
                    'courses[0][categoryid]': '1'
                }
            },
            {
                'name': 'Sehr kurze Namen',
                'data': {
                    'wstoken': MOODLE_TOKEN,
                    'wsfunction': 'core_course_create_courses',
                    'moodlewsrestformat': 'json',
                    'courses[0][fullname]': 'T',
                    'courses[0][shortname]': 't',
                    'courses[0][categoryid]': 1
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n   📋 {test_case['name']}")
            try:
                async with session.post(url, data=test_case['data']) as response:
                    result = await response.json()
                    print(f"      Status: {response.status}")
                    if isinstance(result, dict) and 'exception' in result:
                        print(f"      ❌ Fehler: {result.get('message')}")
                        print(f"      Debug Info: {result.get('debuginfo', 'N/A')}")
                    elif isinstance(result, list) and len(result) > 0:
                        print(f"      ✅ Erfolgreich: {result[0]}")
                    else:
                        print(f"      Result: {result}")
            except Exception as e:
                print(f"      ❌ Exception: {e}")

async def main():
    """Haupt-Debug für API-Spezifikation."""
    print("🚀 Debug: Moodle API-Spezifikation für Kurserstellung")
    print("=" * 65)
    
    if not MOODLE_TOKEN:
        print("❌ Kein Admin Token gefunden!")
        return
    
    print(f"🌐 Moodle URL: {MOODLE_URL}")
    print(f"🔐 Admin Token: {MOODLE_TOKEN[:10]}...")
    
    await get_api_documentation()
    await test_direct_api_call()
    await test_minimal_course_creation()
    
    print("\n" + "=" * 65)
    print("🎯 API-Debug abgeschlossen!")

if __name__ == "__main__":
    asyncio.run(main())
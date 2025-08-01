#!/usr/bin/env python3
"""
Debug Token Permissions 
=======================
Überprüft die Berechtigungen des verwendeten Tokens für Kurserstellung.
"""

import asyncio
import aiohttp
import json
import os
from pathlib import Path

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
    
    async def call_webservice(self, function_name: str, **params):
        """Call Moodle web service function."""
        url = f"{self.base_url}/webservice/rest/server.php"
        
        data = {
            'wstoken': self.token,
            'wsfunction': function_name,
            'moodlewsrestformat': 'json',
            **params
        }
        
        async with self.session.post(url, data=data) as response:
            if response.status == 200:
                result = await response.json()
                if isinstance(result, dict) and 'exception' in result:
                    raise Exception(f"Moodle error: {result.get('message', 'Unknown error')}")
                return result
            else:
                raise Exception(f"HTTP {response.status}: {await response.text()}")

async def test_token(token_name: str, token_value: str):
    """Teste die Berechtigung eines Tokens."""
    print(f"\n🔐 Teste Token: {token_name}")
    print(f"   Wert: {token_value[:10]}...")
    
    if not token_value:
        print("   ❌ Token ist leer!")
        return
    
    async with MoodleAPIClient(MOODLE_URL, token_value) as client:
        try:
            # 1. Site Info abrufen
            site_info = await client.call_webservice("core_webservice_get_site_info")
            print(f"   ✅ Site Info: {site_info.get('fullname')} ({site_info.get('username')})")
            
            # 2. Kurse abrufen
            try:
                courses = await client.call_webservice("core_course_get_courses")
                print(f"   ✅ Kurse abrufen: {len(courses)} Kurse gefunden")
            except Exception as e:
                print(f"   ❌ Kurse abrufen: {e}")
            
            # 3. Kategorien abrufen
            try:
                categories = await client.call_webservice("core_course_get_categories")
                print(f"   ✅ Kategorien abrufen: {len(categories)} Kategorien gefunden")
            except Exception as e:
                print(f"   ❌ Kategorien abrufen: {e}")
            
            # 4. Kurs erstellen versuchen (minimal)
            try:
                test_course_data = [{
                    'fullname': f'Permission Test {token_name}',
                    'shortname': f'permtest_{token_name.lower()}',
                    'categoryid': 1
                }]
                
                result = await client.call_webservice(
                    "core_course_create_courses",
                    courses=test_course_data
                )
                
                if result and len(result) > 0:
                    course_id = result[0].get('id')
                    print(f"   ✅ Kurs erstellen: Erfolgreich! ID: {course_id}")
                    
                    # Kurs wieder löschen
                    try:
                        await client.call_webservice(
                            "core_course_delete_courses",
                            courseids=[course_id]
                        )
                        print(f"   🗑️ Test-Kurs gelöscht")
                    except Exception as delete_error:
                        print(f"   ⚠️ Konnte Test-Kurs nicht löschen: {delete_error}")
                else:
                    print(f"   ❌ Kurs erstellen: Kein Ergebnis erhalten")
                    
            except Exception as e:
                print(f"   ❌ Kurs erstellen: {e}")
                
        except Exception as e:
            print(f"   ❌ Token-Test fehlgeschlagen: {e}")

async def check_webservice_user():
    """Überprüfe die Web Service Konfiguration."""
    print(f"\n🔧 Web Service Konfiguration:")
    print(f"   Moodle URL: {MOODLE_URL}")
    print(f"   WS User: {config.get('MOODLE_WS_USER', 'N/A')}")
    print(f"   Admin User: {config.get('MOODLE_ADMIN_USER', 'N/A')}")

async def main():
    """Haupt-Test für Token-Berechtigungen."""
    print("🚀 Debug: Token-Berechtigungen für Kurserstellung")
    print("=" * 60)
    
    await check_webservice_user()
    
    # Teste alle verfügbaren Tokens
    tokens_to_test = [
        ('BASIC_TOKEN', config.get('MOODLE_BASIC_TOKEN', '')),
        ('PLUGIN_TOKEN', config.get('MOODLE_PLUGIN_TOKEN', '')),
        ('ADMIN_TOKEN', config.get('MOODLE_ADMIN_TOKEN', '')),
        ('WSUSER_TOKEN', config.get('MOODLE_WSUSER_TOKEN', ''))
    ]
    
    for token_name, token_value in tokens_to_test:
        await test_token(token_name, token_value)
    
    print("\n" + "=" * 60)
    print("🎯 Token-Test abgeschlossen!")
    
    # Empfehlungen
    print("\n💡 Empfehlungen:")
    print("   1. Überprüfen Sie die Web Service Benutzer-Rolle in Moodle")
    print("   2. Stellen Sie sicher, dass 'course:create' Berechtigung vorhanden ist")
    print("   3. Überprüfen Sie die Kategorie-Berechtigungen")

if __name__ == "__main__":
    asyncio.run(main())
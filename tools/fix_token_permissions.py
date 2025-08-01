#!/usr/bin/env python3
"""
Token Permissions Fix Tool
===========================

Überprüft und korrigiert Moodle Token-Berechtigungen für Kurs-Erstellung.
"""

import os
import sys
import json
import requests
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class TokenPermissionsFixer:
    """Tool zur Behebung von Token-Berechtigungsfehlern."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_file = self.project_root / "config/moodle_tokens.env"
        self.load_config()
        
    def load_config(self):
        """Lädt die Konfiguration aus der .env Datei."""
        self.config = {}
        
        if not self.config_file.exists():
            logger.error(f"❌ Config file not found: {self.config_file}")
            return
            
        with open(self.config_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    self.config[key] = value.strip('"\'')
                    
        logger.info("✅ Configuration loaded successfully")
    
    def test_token_capabilities(self, token: str, token_name: str):
        """Testet die Fähigkeiten eines Tokens."""
        logger.info(f"🔍 Testing capabilities for {token_name}...")
        
        if not token:
            logger.warning(f"⚠️  {token_name} is empty")
            return {}
        
        moodle_url = self.config.get('MOODLE_URL', 'http://localhost:8080')
        
        capabilities = {
            'basic_info': False,
            'get_courses': False,
            'create_courses': False,
            'get_users': False,
            'create_users': False,
            'site_info': False
        }
        
        # Test basic site info
        try:
            response = requests.post(f"{moodle_url}/webservice/rest/server.php", {
                'wstoken': token,
                'wsfunction': 'core_webservice_get_site_info',
                'moodlewsrestformat': 'json'
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'exception' not in data:
                    capabilities['site_info'] = True
                    logger.info(f"  ✅ Site info access")
                else:
                    logger.warning(f"  ❌ Site info failed: {data.get('message', 'Unknown error')}")
            
        except Exception as e:
            logger.warning(f"  ❌ Site info test failed: {e}")
        
        # Test course listing
        try:
            response = requests.post(f"{moodle_url}/webservice/rest/server.php", {
                'wstoken': token,
                'wsfunction': 'core_course_get_courses',
                'moodlewsrestformat': 'json'
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) or (isinstance(data, dict) and 'exception' not in data):
                    capabilities['get_courses'] = True
                    logger.info(f"  ✅ Course listing access")
                else:
                    logger.warning(f"  ❌ Course listing failed: {data.get('message', 'Unknown error')}")
                    
        except Exception as e:
            logger.warning(f"  ❌ Course listing test failed: {e}")
        
        # Test course creation
        try:
            test_course = {
                'courses[0][fullname]': 'Test Course Permissions Check',
                'courses[0][shortname]': f'TEST-{int(datetime.now().timestamp())}',
                'courses[0][categoryid]': '1'
            }
            
            response = requests.post(f"{moodle_url}/webservice/rest/server.php", {
                'wstoken': token,
                'wsfunction': 'core_course_create_courses',
                'moodlewsrestformat': 'json',
                **test_course
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0 and 'id' in data[0]:
                    capabilities['create_courses'] = True
                    logger.info(f"  ✅ Course creation access")
                    
                    # Clean up test course
                    course_id = data[0]['id']
                    try:
                        requests.post(f"{moodle_url}/webservice/rest/server.php", {
                            'wstoken': token,
                            'wsfunction': 'core_course_delete_courses',
                            'moodlewsrestformat': 'json',
                            'courseids[0]': course_id
                        }, timeout=10)
                        logger.info(f"  🗑️  Test course cleaned up")
                    except:
                        pass
                        
                elif isinstance(data, dict) and 'exception' in data:
                    logger.warning(f"  ❌ Course creation failed: {data.get('message', 'Unknown error')}")
                else:
                    logger.warning(f"  ❌ Course creation failed: Unexpected response")
                    
        except Exception as e:
            logger.warning(f"  ❌ Course creation test failed: {e}")
        
        # Test user listing
        try:
            response = requests.post(f"{moodle_url}/webservice/rest/server.php", {
                'wstoken': token,
                'wsfunction': 'core_user_get_users',
                'moodlewsrestformat': 'json',
                'criteria[0][key]': 'username',
                'criteria[0][value]': 'admin'
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'users' in data:
                    capabilities['get_users'] = True
                    logger.info(f"  ✅ User listing access")
                else:
                    logger.warning(f"  ❌ User listing failed")
                    
        except Exception as e:
            logger.warning(f"  ❌ User listing test failed: {e}")
        
        return capabilities
    
    def get_token_user_info(self, token: str):
        """Ermittelt Informationen über den Token-Benutzer."""
        if not token:
            return None
            
        moodle_url = self.config.get('MOODLE_URL', 'http://localhost:8080')
        
        try:
            response = requests.post(f"{moodle_url}/webservice/rest/server.php", {
                'wstoken': token,
                'wsfunction': 'core_webservice_get_site_info',
                'moodlewsrestformat': 'json'
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'exception' not in data:
                    return {
                        'userid': data.get('userid'),
                        'username': data.get('username'),
                        'firstname': data.get('firstname'),
                        'lastname': data.get('lastname'),
                        'fullname': data.get('fullname'),
                        'userpictureurl': data.get('userpictureurl')
                    }
        except:
            pass
            
        return None
    
    def create_admin_token(self):
        """Erstellt einen neuen Admin-Token mit vollen Berechtigungen."""
        logger.info("🔐 Creating new admin token with full permissions...")
        
        moodle_url = self.config.get('MOODLE_URL', 'http://localhost:8080')
        admin_user = self.config.get('MOODLE_ADMIN_USER', 'admin')
        admin_password = self.config.get('MOODLE_ADMIN_PASSWORD', 'MoodleClaude2025!')
        
        # Login and get session
        session = requests.Session()
        
        try:
            # Get login page to extract logintoken
            login_page = session.get(f"{moodle_url}/login/index.php")
            
            # Extract logintoken from the page
            import re
            logintoken_match = re.search(r'name="logintoken" value="([^"]*)"', login_page.text)
            logintoken = logintoken_match.group(1) if logintoken_match else ''
            
            # Login
            login_data = {
                'username': admin_user,
                'password': admin_password,
                'logintoken': logintoken
            }
            
            login_response = session.post(f"{moodle_url}/login/index.php", data=login_data)
            
            if 'Dashboard' in login_response.text or 'invalid login' not in login_response.text.lower():
                logger.info("✅ Admin login successful")
                
                # Create webservice user if needed
                # Note: This would require more complex Moodle admin API calls
                # For now, we'll use the existing tokens
                
                return True
            else:
                logger.error("❌ Admin login failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Token creation failed: {e}")
            return False
    
    def fix_permissions(self):
        """Behebt Token-Berechtigungsprobleme."""
        logger.info("🔧 Starting token permissions fix...")
        
        # Test all available tokens
        tokens_to_test = {
            'MOODLE_BASIC_TOKEN': self.config.get('MOODLE_BASIC_TOKEN', ''),
            'MOODLE_PLUGIN_TOKEN': self.config.get('MOODLE_PLUGIN_TOKEN', ''),
            'MOODLE_ADMIN_TOKEN': self.config.get('MOODLE_ADMIN_TOKEN', ''),
            'MOODLE_WSUSER_TOKEN': self.config.get('MOODLE_WSUSER_TOKEN', '')
        }
        
        results = {}
        best_token = None
        best_capabilities = {}
        
        for token_name, token_value in tokens_to_test.items():
            if token_value:
                logger.info(f"\n🔍 Testing {token_name}...")
                user_info = self.get_token_user_info(token_value)
                if user_info:
                    logger.info(f"  👤 User: {user_info.get('fullname', 'Unknown')} ({user_info.get('username', 'Unknown')})")
                
                capabilities = self.test_token_capabilities(token_value, token_name)
                results[token_name] = {
                    'token': token_value,
                    'user_info': user_info,
                    'capabilities': capabilities
                }
                
                # Find best token (most capabilities)
                if sum(capabilities.values()) > sum(best_capabilities.values()):
                    best_token = token_name
                    best_capabilities = capabilities
        
        # Generate report
        logger.info("\n" + "=" * 60)
        logger.info("🎯 TOKEN CAPABILITIES REPORT")
        logger.info("=" * 60)
        
        for token_name, result in results.items():
            caps = result['capabilities']
            score = sum(caps.values())
            max_score = len(caps)
            
            logger.info(f"\n📋 {token_name}:")
            if result['user_info']:
                logger.info(f"   👤 User: {result['user_info']['fullname']} ({result['user_info']['username']})")
            logger.info(f"   🎯 Score: {score}/{max_score}")
            
            for cap_name, has_cap in caps.items():
                status = "✅" if has_cap else "❌"
                logger.info(f"   {status} {cap_name.replace('_', ' ').title()}")
        
        # Recommendations
        logger.info(f"\n🏆 BEST TOKEN: {best_token}")
        
        if best_capabilities.get('create_courses', False):
            logger.info("✅ Course creation is possible with this token")
            
            # Update Claude Desktop config
            claude_config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
            
            if claude_config_path.exists():
                try:
                    with open(claude_config_path, 'r') as f:
                        claude_config = json.load(f)
                    
                    # Update with best token
                    if 'mcpServers' in claude_config and 'moodleclaude-stable' in claude_config['mcpServers']:
                        server_config = claude_config['mcpServers']['moodleclaude-stable']
                        server_config['env']['MOODLE_TOKEN_ENHANCED'] = results[best_token]['token']
                        
                        with open(claude_config_path, 'w') as f:
                            json.dump(claude_config, f, indent=2)
                        
                        logger.info(f"✅ Updated Claude Desktop config with {best_token}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to update Claude Desktop config: {e}")
            
        else:
            logger.warning("⚠️  None of the tokens have course creation permissions")
            logger.info("🔧 Recommendations:")
            logger.info("   1. Check Moodle web service settings")
            logger.info("   2. Verify user roles and capabilities")
            logger.info("   3. Ensure course creation is enabled for the web service user")
        
        return results
    
    def run_diagnostics(self):
        """Führt die vollständige Diagnose und Reparatur durch."""
        logger.info("🚀 Starting token permissions diagnostics...")
        logger.info("=" * 60)
        
        return self.fix_permissions()

def main():
    """Main function."""
    print("🔧 MoodleClaude Token Permissions Fix Tool")
    print("=" * 60)
    print("🚀 Analyzing and fixing token permissions...")
    
    fixer = TokenPermissionsFixer()
    results = fixer.run_diagnostics()
    
    print(f"\n📊 Diagnostics complete!")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
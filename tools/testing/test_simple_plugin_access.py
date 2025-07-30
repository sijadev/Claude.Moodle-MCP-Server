#!/usr/bin/env python3
"""
Simple test to verify plugin access step by step
"""

import asyncio
import aiohttp
import json
from dual_token_config import DualTokenConfig

async def test_simple_plugin_access():
    """Test plugin access with direct API calls"""
    
    print("🔍 Simple Plugin Access Test")
    print("=" * 50)
    
    config = DualTokenConfig.from_env()
    plugin_token = config.get_plugin_token()
    
    print(f"🔧 Testing plugin token: ...{plugin_token[-8:]}")
    print(f"🌐 Moodle URL: {config.moodle_url}")
    
    # Test 1: Basic API call
    print(f"\n1️⃣ Testing basic API access...")
    try:
        async with aiohttp.ClientSession() as session:
            data = {
                "wstoken": plugin_token,
                "wsfunction": "core_webservice_get_site_info",
                "moodlewsrestformat": "json"
            }
            
            async with session.post(f"{config.moodle_url}/webservice/rest/server.php", data=data) as response:
                result = await response.json()
                
                if 'exception' in result:
                    print(f"❌ API Error: {result.get('message', 'Unknown error')}")
                    print(f"   Error code: {result.get('errorcode', 'unknown')}")
                    
                    if 'accessexception' in result.get('errorcode', ''):
                        print("\n💡 This is an access control exception.")
                        print("   Possible causes:")
                        print("   1. Token not associated with correct service")
                        print("   2. User not authorized for the service")
                        print("   3. Service not enabled")
                        print("   4. Token expired or invalid")
                        
                else:
                    print(f"✅ Basic API access works!")
                    user_name = result.get('username', 'unknown')
                    print(f"   User: {user_name}")
                    
                    # Check functions
                    functions = result.get('functions', [])
                    moodleclaude_funcs = [f for f in functions if 'moodleclaude' in f.get('name', '').lower()]
                    print(f"   Total functions: {len(functions)}")
                    print(f"   MoodleClaude functions: {len(moodleclaude_funcs)}")
                    
                    if moodleclaude_funcs:
                        print("   🎉 MoodleClaude functions available:")
                        for func in moodleclaude_funcs:
                            print(f"      - {func.get('name')}")
                    else:
                        print("   ⚠️ No MoodleClaude functions available to this token")
                        
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 2: Compare with basic token
    print(f"\n2️⃣ Comparing with basic token...")
    try:
        basic_token = config.get_basic_token()
        
        async with aiohttp.ClientSession() as session:
            data = {
                "wstoken": basic_token,
                "wsfunction": "core_webservice_get_site_info", 
                "moodlewsrestformat": "json"
            }
            
            async with session.post(f"{config.moodle_url}/webservice/rest/server.php", data=data) as response:
                result = await response.json()
                
                if 'exception' not in result:
                    functions = result.get('functions', [])
                    print(f"✅ Basic token works with {len(functions)} functions")
                else:
                    print(f"❌ Basic token also fails: {result.get('message')}")
                    
    except Exception as e:
        print(f"❌ Basic token test failed: {e}")
    
    print(f"\n" + "=" * 50)
    print("🎯 Test Complete")
    
    print(f"\n📋 **Troubleshooting Checklist:**")
    print("□ Custom web service is created and enabled")
    print("□ All MoodleClaude functions are added to the service")
    print("□ Token is created for the custom service (not default)")
    print("□ User 'simon' is added to authorized users for the service")
    print("□ Service has 'Authorised users only' enabled")

if __name__ == "__main__":
    asyncio.run(test_simple_plugin_access())
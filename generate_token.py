#!/usr/bin/env python3
"""
Generate a new Moodle web service token
"""

import requests
import os
from urllib.parse import urljoin

def generate_moodle_token():
    """Generate a new Moodle web service token"""
    
    moodle_url = os.getenv("MOODLE_URL", "http://localhost:8080")
    admin_user = os.getenv("MOODLE_ADMIN_USER", "simon")
    admin_password = os.getenv("MOODLE_ADMIN_PASSWORD", "Pwd1234!")
    
    print(f"🔑 Attempting to generate token for Moodle at {moodle_url}")
    print(f"👤 Username: {admin_user}")
    
    # First, try to get a token using the token service
    token_url = urljoin(moodle_url, "login/token.php")
    
    token_data = {
        'username': admin_user,
        'password': admin_password,
        'service': 'moodle_mobile_app'  # Try mobile app service first
    }
    
    print(f"📡 Requesting token from: {token_url}")
    
    try:
        response = requests.post(token_url, data=token_data, timeout=10)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if 'token' in result:
                token = result['token']
                print(f"✅ Token generated successfully!")
                print(f"🔑 New token: {token}")
                
                # Update .env file
                env_path = "/Users/simonjanke/Projects/MoodleClaude/.env"
                with open(env_path, 'r') as f:
                    content = f.read()
                
                # Replace old token
                content = content.replace(
                    "MOODLE_TOKEN=b2021a7a41309b8c58ad026a751d0cd0",
                    f"MOODLE_TOKEN={token}"
                )
                
                with open(env_path, 'w') as f:
                    f.write(content)
                
                print(f"✅ .env file updated with new token")
                return token
            else:
                print(f"❌ No token in response: {result}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error generating token: {e}")
    
    # Try alternative service names
    alternative_services = [
        'webservice_rest',
        'moodle_rest',
        'external_webservice',
        'ws_rest'
    ]
    
    for service in alternative_services:
        print(f"🔄 Trying alternative service: {service}")
        token_data['service'] = service
        
        try:
            response = requests.post(token_url, data=token_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'token' in result:
                    token = result['token']
                    print(f"✅ Token generated with service {service}!")
                    print(f"🔑 New token: {token}")
                    return token
        except:
            continue
    
    print("❌ Could not generate token with any service")
    return None

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    token = generate_moodle_token()
    
    if token:
        print(f"\n🎉 Success! Use this token in your demos:")
        print(f"export MOODLE_TOKEN={token}")
    else:
        print(f"\n❌ Token generation failed")
        print(f"💡 You may need to:")
        print(f"  1. Enable web services in Moodle admin")
        print(f"  2. Create a web service user")
        print(f"  3. Assign proper capabilities")
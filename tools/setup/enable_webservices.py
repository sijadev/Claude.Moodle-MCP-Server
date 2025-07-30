#!/usr/bin/env python3
"""
Script to enable required Moodle web service functions
This script provides guidance and automation for enabling web services
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_admin_access():
    """Check if we have admin access to enable web services"""
    moodle_url = os.getenv("MOODLE_URL", "http://localhost:8080")
    admin_user = os.getenv("MOODLE_ADMIN_USER", "admin")
    admin_password = os.getenv("MOODLE_ADMIN_PASSWORD", "")
    
    print(f"🔍 Checking admin access to: {moodle_url}")
    print(f"👤 Admin user: {admin_user}")
    
    if not admin_password:
        print("❌ MOODLE_ADMIN_PASSWORD not set in .env file")
        return False
    
    # Try to access admin login
    session = requests.Session()
    
    try:
        # Get login page to retrieve logintoken
        login_page = session.get(f"{moodle_url}/login/index.php")
        if login_page.status_code != 200:
            print(f"❌ Cannot access login page: HTTP {login_page.status_code}")
            return False
            
        print("✅ Can access Moodle login page")
        return True
        
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def get_required_functions():
    """Get list of functions that need to be enabled"""
    return [
        # Core section functions
        "core_course_create_sections",
        "core_course_edit_section", 
        "core_course_update_sections",
        
        # Plugin section management functions (local_wsmanagesections)
        "local_wsmanagesections_create_section",
        "local_wsmanagesections_update_section", 
        "local_wsmanagesections_delete_section",
        "local_wsmanagesections_get_sections",
        "local_wsmanagesections_move_section",
        
        # Activity functions
        "core_course_create_activities",
        "core_course_create_modules",
        "mod_page_create_page",
        "mod_label_add_label",
        
        # File and info functions
        "core_files_upload",
        "core_webservice_get_site_info"
    ]

def print_manual_instructions():
    """Print manual instructions for enabling web services"""
    moodle_url = os.getenv("MOODLE_URL", "http://localhost:8080")
    
    print(f"\n📋 MANUAL SETUP INSTRUCTIONS")
    print(f"=" * 50)
    print(f"🌐 Access your Moodle admin panel: {moodle_url}/admin")
    print(f"👤 Login with admin credentials")
    print()
    print("🔧 Steps to enable web service functions:")
    print("1. Go to: Site Administration → Server → Web services")
    print("2. Click 'Overview' to see current status")
    print("3. Enable web services if not already enabled")
    print("4. Go to 'External services'")
    print("5. Find or create a custom service")
    print("6. Add the following functions to your service:")
    
    functions = get_required_functions()
    for i, func in enumerate(functions, 1):
        print(f"   {i:2d}. {func}")
    
    print()
    print("7. Assign the service to your user or create a service user")
    print("8. Generate a new token for the service")
    print("9. Update MOODLE_TOKEN in your .env file")
    print()
    print("🛡️ Required user capabilities:")
    capabilities = [
        "moodle/course:manageactivities",
        "moodle/course:activityvisibility", 
        "moodle/course:sectionvisibility",
        "moodle/site:config",
        "webservice/rest:use"
    ]
    for cap in capabilities:
        print(f"   • {cap}")

def main():
    print("🚀 Moodle Web Service Enabler")
    print("=" * 40)
    
    if not check_admin_access():
        print("\n❌ Cannot proceed with automatic setup")
        print("📖 Please follow manual instructions below")
        print_manual_instructions()
        return
    
    print("\n✅ Basic connectivity confirmed")
    print("🔄 For security reasons, web service configuration")
    print("   must be done through the Moodle admin interface")
    
    print_manual_instructions()
    
    print(f"\n🧪 After setup, test with:")
    print(f"python demos/check_webservices.py")

if __name__ == "__main__":
    main()
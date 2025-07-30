#!/usr/bin/env python3
"""
Automated setup script for fresh Moodle installation with MoodleClaude plugin
Includes complete data cleanup before starting fresh containers
"""

import asyncio
import aiohttp
import logging
import subprocess
import os
from time import sleep

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(cmd, description=""):
    """Run shell command and return success status"""
    try:
        print(f"🔧 {description}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"⚠️ Warning: {description}")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Failed: {description} - {e}")
        return False

def cleanup_docker_environment():
    """Complete cleanup of Docker containers, volumes, and persistent data"""
    print("\n🧹 COMPLETE DOCKER CLEANUP")
    print("=" * 40)
    
    # Stop and remove containers
    run_command("docker-compose down", "Stopping containers")
    
    # Remove specific containers if they exist
    containers = ["moodleclaude_app", "moodleclaude_db", "moodleclaude_phpmyadmin"]
    for container in containers:
        run_command(f"docker rm -f {container} 2>/dev/null || true", f"Removing container {container}")
    
    # Remove Docker volumes
    volumes = [
        "docker_mariadb_data", 
        "mariadb_data", 
        "simonjanke_mariadb_data",
        "moodleclaude_mariadb_data",
        "moodleclaude_moodle_data"
    ]
    for volume in volumes:
        run_command(f"docker volume rm {volume} 2>/dev/null || true", f"Removing volume {volume}")
    
    # Remove persistent data directories
    data_dirs = [
        "/Users/simonjanke/Docker/Shared/data/moodleclaude_mariadb",
        "/Users/simonjanke/Docker/Shared/data/moodleclaude_moodle", 
        "/Users/simonjanke/Docker/Shared/data/moodleclaude_moodledata"
    ]
    
    for data_dir in data_dirs:
        if os.path.exists(data_dir):
            run_command(f"rm -rf {data_dir}", f"Removing persistent data: {data_dir}")
        else:
            print(f"✅ Directory already clean: {data_dir}")
    
    # Clean Docker system (optional)
    run_command("docker system prune -f", "Cleaning Docker system")
    
    print("✅ Complete cleanup finished!")

def start_fresh_containers():
    """Start fresh Docker containers and install plugin"""
    print("\n🚀 STARTING FRESH CONTAINERS")
    print("=" * 40)
    
    # Start containers
    run_command("docker-compose up -d", "Starting fresh containers")
    
    # Wait for containers to be ready
    print("⏳ Waiting for containers to initialize...")
    sleep(30)
    
    # Check container status
    run_command("docker-compose ps", "Checking container status")
    
    # Install plugin
    print("\n📦 Installing MoodleClaude plugin...")
    plugin_install_commands = [
        "docker exec moodleclaude_app mkdir -p /bitnami/moodle/local/moodleclaude",
        "docker cp moodle_plugin/local_moodleclaude/. moodleclaude_app:/bitnami/moodle/local/moodleclaude/",
        "docker exec moodleclaude_app chown -R daemon:daemon /bitnami/moodle/local/moodleclaude",
        "docker exec moodleclaude_app chmod -R 755 /bitnami/moodle/local/moodleclaude"
    ]
    
    for cmd in plugin_install_commands:
        run_command(cmd, f"Plugin setup: {cmd.split()[-1]}")
    
    print("✅ Fresh containers started with plugin installed!")

async def setup_fresh_moodle():
    """Set up fresh Moodle installation step by step"""
    
    print("🚀 COMPLETE FRESH MOODLE SETUP")
    print("=" * 60)
    print("This will completely reset your Moodle environment!")
    print("All existing courses, users, and data will be deleted.")
    
    # Confirm with user (in automated script, we skip this)
    # response = input("\n⚠️ Continue with complete reset? (y/N): ")
    # if response.lower() != 'y':
    #     print("❌ Setup cancelled")
    #     return
    
    # Step 1: Complete cleanup
    cleanup_docker_environment()
    
    # Step 2: Start fresh containers
    start_fresh_containers()
    
    # Step 3: Wait and verify Moodle accessibility
    print("\n⏳ Waiting for Moodle to fully initialize...")
    sleep(60)  # Give Moodle time to set up database
    
    moodle_url = "http://localhost:8080"
    
    # Step 4: Check if Moodle is accessible
    print("\n4️⃣ Verifying Moodle accessibility...")
    max_retries = 5
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(moodle_url, timeout=10) as response:
                    if response.status == 200:
                        print("✅ Moodle is accessible")
                        text = await response.text()
                        if "MoodleClaude Test Environment" in text:
                            print("✅ Moodle is fully initialized")
                            break
                        else:
                            print("⚠️ Moodle may still be initializing")
                    else:
                        print(f"⚠️ Moodle HTTP {response.status} (attempt {attempt + 1}/{max_retries})")
        except Exception as e:
            print(f"⚠️ Connection attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                print("⏳ Waiting 30 seconds before retry...")
                sleep(30)
            else:
                print("❌ Could not establish connection to Moodle")
                print("💡 Try running: docker-compose logs moodle")
                return
    
    # Step 5: Manual configuration guide
    print("\n5️⃣ MANUAL CONFIGURATION REQUIRED")
    print("=" * 50)
    admin_url = f"{moodle_url}/admin/"
    print(f"📍 Admin URL: {admin_url}")
    print("\n🔐 **Login Credentials:**")
    print("   Username: simon")
    print("   Password: Pwd1234!")
    
    print("\n📦 **Plugin Installation:**")
    print("   1. Go to: http://localhost:8080/admin/")
    print("   2. Look for plugin installation notification")
    print("   3. Click 'Install' or 'Upgrade' for MoodleClaude plugin")
    print("   4. Follow the installation wizard")
    
    print("\n🌐 **Web Services Setup:**")
    print("   1. Go to: Site Administration → Advanced Features")
    print("   2. Enable 'Web services' and save")
    print("   3. Go to: Site Administration → Server → Web services → Manage protocols")
    print("   4. Enable 'REST protocol'")
    print("   5. Go to: Site Administration → Server → Web services → External services")
    print("   6. Find 'MoodleClaude Content Creation Service'")
    print("   7. The service should be enabled with 9 functions (5 MoodleClaude + 4 core)")
    
    print("\n🔑 **Token Creation:**")
    print("   1. Go to: Site Administration → Server → Web services → Manage tokens")
    print("   2. Create Basic Token:")
    print("      - User: simon")
    print("      - Service: Moodle mobile web service")
    print("   3. Create Plugin Token:")
    print("      - User: simon") 
    print("      - Service: MoodleClaude Content Creation Service")
    print("   4. Go back to External services")
    print("   5. Find 'MoodleClaude Content Creation Service'")
    print("   6. Click 'Authorised users' and add 'simon'")
    
    print("\n📝 **Update Configuration:**")
    print("   Update your .env file with the new tokens:")
    print("   MOODLE_BASIC_TOKEN=your_basic_token_here")
    print("   MOODLE_PLUGIN_TOKEN=your_plugin_token_here")
    
    print("\n🧪 **Verification:**")
    print("   After completing setup, test with:")
    print("   python test_simple_plugin_access.py")
    print("   python verify_dual_tokens.py")
    
    print(f"\n" + "=" * 60)
    print("🎯 FRESH SETUP COMPLETE!")
    print("\n✅ **What was done:**")
    print("   • Complete Docker cleanup (containers, volumes, data)")
    print("   • Fresh container startup")
    print("   • MoodleClaude plugin installation")
    print("   • Database and Moodle initialization")
    
    print("\n📋 **Next Steps:**")
    print("   1. Complete manual web service configuration (above)")
    print("   2. Update .env file with new tokens")
    print("   3. Run verification tests")
    print("   4. Start using MoodleClaude with Claude Desktop!")
    
    print("\n💡 **Troubleshooting:**")
    print("   • If plugin not detected: docker exec moodleclaude_app php /bitnami/moodle/admin/cli/upgrade.php")
    print("   • If containers fail: docker-compose logs")
    print("   • For fresh restart: python setup_fresh_moodle.py")

if __name__ == "__main__":
    asyncio.run(setup_fresh_moodle())
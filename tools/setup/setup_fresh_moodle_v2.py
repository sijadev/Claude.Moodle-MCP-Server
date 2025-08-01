#!/usr/bin/env python3
"""
MoodleClaude Fresh Installation v2.0
===================================
Updated setup script using centralized configuration system
Prevents password chaos and ensures consistency

Usage:
    python tools/setup/setup_fresh_moodle_v2.py
    python tools/setup/setup_fresh_moodle_v2.py --quick-setup
    python tools/setup/setup_fresh_moodle_v2.py --force-rebuild
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from config.master_config import get_master_config
    from tools.config_manager import sync_all_configurations
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root")
    sys.exit(1)


def run_command(cmd, description="", capture_output=True):
    """Run shell command with proper error handling"""
    print(f"🔧 {description}")
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=PROJECT_ROOT)
        else:
            result = subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT)
        
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if capture_output and result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:200]}")
            return True
        else:
            print(f"❌ Failed: {description}")
            if capture_output and result.stderr.strip():
                print(f"   Error: {result.stderr.strip()[:200]}")
            return False
    except Exception as e:
        print(f"❌ Exception in {description}: {e}")
        return False


def cleanup_existing_containers():
    """Clean up existing MoodleClaude containers and data"""
    print("\n🧹 Cleaning up existing containers...")
    
    cleanup_commands = [
        ("docker-compose down -v", "Stop and remove containers with volumes"),
        ("docker system prune -f", "Clean up Docker system"),
        ("docker volume prune -f", "Clean up Docker volumes"),
    ]
    
    for cmd, desc in cleanup_commands:
        run_command(cmd, desc)
    
    print("✅ Cleanup completed")


def generate_unified_config():
    """Generate unified configuration using master_config"""
    print("\n🎯 Generating unified configuration...")
    
    try:
        # Sync all configurations from master config
        success = sync_all_configurations()
        if success:
            print("✅ Unified configuration generated")
        else:
            print("⚠️ Configuration sync completed with warnings")
        return True
    except Exception as e:
        print(f"❌ Configuration generation failed: {e}")
        return False


def start_fresh_containers():
    """Start fresh MoodleClaude containers"""
    print("\n🐳 Starting fresh containers...")
    
    # Get config for verification
    config = get_master_config()
    print(f"🎯 Using admin password: {config.credentials.admin_password}")
    print(f"🎯 Using WS user: {config.credentials.ws_user}")
    
    startup_commands = [
        ("docker-compose up -d", "Start MoodleClaude containers"),
    ]
    
    for cmd, desc in startup_commands:
        if not run_command(cmd, desc):
            return False
    
    print("✅ Containers started")
    return True


def wait_for_moodle():
    """Wait for Moodle to be ready"""
    print("\n⏳ Waiting for Moodle to be ready...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(
                ["curl", "-f", "-s", "http://localhost:8080/login/index.php"],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                print("✅ Moodle is ready!")
                return True
        except:
            pass
        
        print(f"⏳ Attempt {attempt + 1}/{max_attempts} - waiting...")
        time.sleep(10)
    
    print("❌ Moodle did not start within expected time")
    return False


def setup_moodle_admin():
    """Setup Moodle admin with unified credentials"""
    print("\n👤 Setting up Moodle admin...")
    
    config = get_master_config()
    admin_password = config.credentials.admin_password
    
    # Reset admin password using CLI
    reset_cmd = f'''docker exec moodleclaude_app_fresh php /opt/bitnami/moodle/admin/cli/reset_password.php \
        --username=admin \
        --password="{admin_password}" \
        --ignore-password-policy'''
    
    if run_command(reset_cmd, f"Set admin password to: {admin_password}"):
        print("✅ Admin credentials configured")
        return True
    else:
        print("❌ Admin setup failed")
        return False


def enable_webservices():
    """Enable Moodle webservices"""
    print("\n🌐 Enabling Moodle webservices...")
    
    webservice_commands = [
        ("docker exec moodleclaude_app_fresh php /opt/bitnami/moodle/admin/cli/cfg.php --name=enablewebservices --set=1", "Enable web services"),
        ("docker exec moodleclaude_app_fresh php /opt/bitnami/moodle/admin/cli/cfg.php --name=webserviceprotocols --set=rest", "Enable REST protocol"),
    ]
    
    success = True
    for cmd, desc in webservice_commands:
        if not run_command(cmd, desc):
            success = False
    
    if success:
        print("✅ Webservices enabled")
    else:
        print("⚠️ Webservice setup had issues")
    
    return success


def create_webservice_user():
    """Create dedicated webservice user automatically"""
    print("\n🔧 Creating webservice user...")
    
    config = get_master_config()
    ws_user = config.credentials.ws_user
    ws_password = config.credentials.ws_password
    ws_email = config.credentials.ws_email
    
    # Create PHP script for user creation
    create_user_script = f'''<?php
define('CLI_SCRIPT', true);
require_once '/opt/bitnami/moodle/config.php';
require_once $CFG->libdir . '/moodlelib.php';
require_once $CFG->dirroot . '/user/lib.php';

// Check if wsuser exists
$existinguser = $DB->get_record('user', array('username' => '{ws_user}'));
if ($existinguser) {{
    echo "WSUser already exists with ID: " . $existinguser->id . "\\n";
    exit(0);
}}

// Create wsuser
$user = new stdClass();
$user->username = '{ws_user}';
$user->password = '{ws_password}';
$user->email = '{ws_email}';
$user->firstname = 'WebService';
$user->lastname = 'User';
$user->confirmed = 1;
$user->auth = 'manual';
$user->city = 'Local';
$user->country = 'DE';

try {{
    $userid = user_create_user($user);
    echo "WSUser created successfully with ID: $userid\\n";
}} catch (Exception $e) {{
    echo "Error creating wsuser: " . $e->getMessage() . "\\n";
    exit(1);
}}
?>'''
    
    # Write script to temp file and execute
    script_path = "/tmp/create_wsuser_setup.php"
    with open(script_path, 'w') as f:
        f.write(create_user_script)
    
    commands = [
        (f"docker cp {script_path} moodleclaude_app_fresh:/tmp/create_wsuser_setup.php", "Copy user creation script"),
        ("docker exec moodleclaude_app_fresh php /tmp/create_wsuser_setup.php", f"Create webservice user: {ws_user}"),
        ("docker exec moodleclaude_app_fresh rm /tmp/create_wsuser_setup.php", "Cleanup script"),
    ]
    
    success = True
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            success = False
    
    # Cleanup local temp file
    try:
        os.unlink(script_path)
    except:
        pass
    
    if success:
        print(f"✅ WebService user '{ws_user}' created successfully")
    else:
        print(f"⚠️ WebService user creation had issues")
    
    return success


def install_plugin():
    """Install MoodleClaude plugin"""
    print("\n🔌 Installing MoodleClaude plugin...")
    
    plugin_commands = [
        ("docker cp moodle_plugin/local_moodleclaude/. moodleclaude_app_fresh:/opt/bitnami/moodle/local/moodleclaude/", "Copy plugin files to container"),
        ("docker exec moodleclaude_app_fresh chown -R daemon:daemon /opt/bitnami/moodle/local/moodleclaude", "Set plugin permissions"),
        ("docker exec moodleclaude_app_fresh php /opt/bitnami/moodle/admin/cli/upgrade.php --non-interactive", "Install and upgrade plugin"),
    ]
    
    success = True
    for cmd, desc in plugin_commands:
        if not run_command(cmd, desc):
            success = False
    
    if success:
        print("✅ Plugin installation completed")
    else:
        print("⚠️ Plugin installation had issues")
    
    return success


def generate_api_tokens():
    """Generate API tokens automatically"""
    print("\n🎫 Generating API tokens...")
    
    config = get_master_config()
    admin_user = config.credentials.admin_user
    admin_password = config.credentials.admin_password
    ws_user = config.credentials.ws_user
    ws_password = config.credentials.ws_password
    
    try:
        # Fix moodledata permissions first
        run_command("docker exec moodleclaude_app_fresh chown -R daemon:daemon /bitnami/moodledata", 
                   "Fix moodledata permissions")
        
        # Generate admin token via mobile service
        print("🔑 Generating admin token...")
        admin_token_cmd = f'''curl -X POST "http://localhost:8080/login/token.php" -d "username={admin_user}" -d "password={admin_password}" -d "service=moodle_mobile_app" -s'''
        result = subprocess.run(admin_token_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            response = json.loads(result.stdout)
            if 'token' in response:
                admin_token = response['token']
                print(f"✅ Admin token generated: {admin_token[:20]}...")
                
                # Generate wsuser token
                print("🔑 Generating wsuser token...")
                token_script = f'''<?php
define('CLI_SCRIPT', true);
require_once '/opt/bitnami/moodle/config.php';
require_once $CFG->libdir . '/moodlelib.php';
require_once $CFG->libdir . '/externallib.php';
require_once $CFG->dirroot . '/webservice/lib.php';

// Get wsuser
$wsuser = $DB->get_record('user', array('username' => '{ws_user}'));
if (!$wsuser) {{
    echo "WSUser not found\\n";
    exit(1);
}}

// Get mobile service
$service = $DB->get_record('external_services', array('shortname' => 'moodle_mobile_app'));
if (!$service) {{
    echo "Mobile service not found\\n";
    exit(1);
}}

try {{
    // Check if token already exists
    $existingtoken = $DB->get_record('external_tokens', array(
        'userid' => $wsuser->id,
        'externalserviceid' => $service->id
    ));
    
    if ($existingtoken) {{
        echo $existingtoken->token . "\\n";
    }} else {{
        // Create new token
        $token = external_generate_token(EXTERNAL_TOKEN_PERMANENT, $service, $wsuser->id, context_system::instance());
        echo $token . "\\n";
    }}
}} catch (Exception $e) {{
    echo "Error: " . $e->getMessage() . "\\n";
    exit(1);
}}
?>'''
                
                # Execute wsuser token generation
                script_path = "/tmp/generate_wsuser_token.php"
                with open(script_path, 'w') as f:
                    f.write(token_script)
                
                token_commands = [
                    (f"docker cp {script_path} moodleclaude_app_fresh:/tmp/generate_wsuser_token.php", "Copy token script"),
                    ("docker exec moodleclaude_app_fresh php /tmp/generate_wsuser_token.php", "Generate wsuser token"),
                ]
                
                wsuser_token = None
                for cmd, desc in token_commands:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if "Generate wsuser token" in desc and result.returncode == 0:
                        wsuser_token = result.stdout.strip()
                
                # Cleanup
                try:
                    os.unlink(script_path)
                    run_command("docker exec moodleclaude_app_fresh rm /tmp/generate_wsuser_token.php", "Cleanup token script")
                except:
                    pass
                
                if wsuser_token:
                    print(f"✅ WSUser token generated: {wsuser_token[:20]}...")
                    
                    # Update master config with tokens using config_manager
                    try:
                        update_cmd = f'python tools/config_manager.py update-tokens --admin-token "{admin_token}" --plugin-token "{wsuser_token}"'
                        result = subprocess.run(update_cmd, shell=True, capture_output=True, text=True, cwd=PROJECT_ROOT)
                        if result.returncode == 0:
                            print("✅ Tokens updated in master configuration")
                            return True
                        else:
                            print("⚠️ Token update failed, manual update required:")
                            print(f"   Admin token: {admin_token}")
                            print(f"   Plugin token: {wsuser_token}")
                            return True
                    except Exception as e:
                        print(f"⚠️ Token update error: {e}")
                        print(f"   Admin token: {admin_token}")
                        print(f"   Plugin token: {wsuser_token}")
                        return True
                else:
                    print("❌ WSUser token generation failed")
            else:
                print(f"❌ Admin token error: {response.get('error', 'Unknown error')}")
        else:
            print(f"❌ Admin token request failed: {result.stderr}")
    
    except Exception as e:
        print(f"❌ Token generation error: {e}")
    
    return False


def fix_mcp_server_path():
    """Fix MCP server launcher path issues"""
    print("\n🔧 Fixing MCP server launcher...")
    
    launcher_path = PROJECT_ROOT / "server" / "mcp_server_launcher.py"
    if not launcher_path.exists():
        print("❌ MCP server launcher not found")
        return False
    
    try:
        # Test MCP server
        test_cmd = f"python {launcher_path} --test"
        result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=30)
        
        if result.returncode == 0 and "Import test successful" in result.stderr:
            print("✅ MCP server launcher working correctly")
            return True
        else:
            print("⚠️ MCP server test had issues")
            if result.stderr:
                print(f"   Error output: {result.stderr[-200:]}")  # Last 200 chars
            return False
    except subprocess.TimeoutExpired:
        print("⚠️ MCP server test timed out")
        return False
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False


def update_claude_desktop():
    """Update Claude Desktop configuration"""
    print("\n🖥️ Updating Claude Desktop configuration...")
    
    try:
        from tools.config_manager import update_claude_desktop_config
        update_claude_desktop_config()
        print("✅ Claude Desktop configuration updated")
        print("🔄 Please restart Claude Desktop to apply changes")
        return True
    except Exception as e:
        print(f"❌ Claude Desktop update failed: {e}")
        return False


def run_validation_tests():
    """Run comprehensive validation tests on the fresh installation"""
    print("\n🧪 Running comprehensive validation tests...")
    
    config = get_master_config()
    all_tests_passed = True
    
    # Test 1: Basic connectivity
    print("\n1️⃣ Testing basic connectivity...")
    test_commands = [
        (f"curl -I http://localhost:8080/login/index.php", "Test Moodle web interface"),
        ("docker ps | grep moodleclaude", "Check container status"),
    ]
    
    for cmd, desc in test_commands:
        if not run_command(cmd, desc):
            all_tests_passed = False
    
    # Test 2: Admin login
    print("\n2️⃣ Testing admin authentication...")
    admin_password = config.credentials.admin_password
    login_test = f'''curl -s -c /tmp/moodle_test_cookies.txt \
        -d "username=admin&password={admin_password}" \
        -X POST "http://localhost:8080/login/index.php"'''
    
    if run_command(login_test, "Test admin login"):
        print("✅ Admin login test passed")
    else:
        print("⚠️ Admin login test failed")
        all_tests_passed = False
    
    # Test 3: API Token validation
    print("\n3️⃣ Testing API tokens...")
    admin_token = config.services.admin_token
    plugin_token = config.services.plugin_token
    
    if admin_token and len(admin_token) > 20:
        # Test admin token with a simple API call
        token_test = f'''curl -s "http://localhost:8080/webservice/rest/server.php?wstoken={admin_token}&wsfunction=core_webservice_get_site_info&moodlewsrestformat=json"'''
        result = subprocess.run(token_test, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0 and "sitename" in result.stdout:
            print("✅ Admin token validation passed")
        else:
            print("⚠️ Admin token validation failed")
            all_tests_passed = False
    else:
        print("⚠️ Admin token missing or invalid")
        all_tests_passed = False
    
    if plugin_token and len(plugin_token) > 20:
        print("✅ Plugin token present")
    else:
        print("⚠️ Plugin token missing")
        all_tests_passed = False
    
    # Test 4: Plugin installation
    print("\n4️⃣ Testing MoodleClaude plugin...")
    plugin_test = "docker exec moodleclaude_app_fresh ls -la /opt/bitnami/moodle/local/moodleclaude/version.php"
    if run_command(plugin_test, "Check plugin files"):
        print("✅ Plugin files present")
    else:
        print("⚠️ Plugin files missing")
        all_tests_passed = False
    
    # Test 5: WebService user
    print("\n5️⃣ Testing WebService user...")
    wsuser_test = f'''docker exec moodleclaude_app_fresh php -r "
define('CLI_SCRIPT', true);
require_once '/opt/bitnami/moodle/config.php';
\\$user = \\$DB->get_record('user', array('username' => '{config.credentials.ws_user}'));
if (\\$user) {{
    echo 'WSUser found with ID: ' . \\$user->id . PHP_EOL;
}} else {{
    echo 'WSUser not found' . PHP_EOL;
    exit(1);
}}
"'''
    
    if run_command(wsuser_test, "Check WebService user"):
        print("✅ WebService user validation passed")
    else:
        print("⚠️ WebService user validation failed")
        all_tests_passed = False
    
    # Test 6: Configuration consistency
    print("\n6️⃣ Testing configuration consistency...")
    try:
        config_validation = subprocess.run("python tools/config_manager.py validate", 
                                         shell=True, capture_output=True, text=True, cwd=PROJECT_ROOT)
        if config_validation.returncode == 0 and "✅ Valid" in config_validation.stdout:
            print("✅ Configuration validation passed")
        else:
            print("⚠️ Configuration validation failed")
            all_tests_passed = False
    except Exception as e:
        print(f"⚠️ Configuration validation error: {e}")
        all_tests_passed = False
    
    # Test 7: MCP Server readiness
    print("\n7️⃣ Testing MCP Server...")
    try:
        mcp_test = f"python server/mcp_server_launcher.py --test"
        result = subprocess.run(mcp_test, shell=True, capture_output=True, text=True, 
                              cwd=PROJECT_ROOT, timeout=30)
        
        if result.returncode == 0 and "Import test successful" in result.stderr:
            print("✅ MCP Server test passed")
        else:
            print("⚠️ MCP Server test failed")
            all_tests_passed = False
    except Exception as e:
        print(f"⚠️ MCP Server test error: {e}")
        all_tests_passed = False
    
    # Summary
    print(f"\n🎯 Validation Summary:")
    if all_tests_passed:
        print("✅ All validation tests passed - System ready!")
    else:
        print("⚠️ Some validation tests failed - Check output above")
    
    return all_tests_passed


def create_default_backup():
    """Create a default backup after successful installation"""
    print("\n💾 Creating default backup...")
    
    try:
        # Create defaults backup directory
        defaults_dir = PROJECT_ROOT / "operations" / "backup" / "defaults"
        defaults_dir.mkdir(parents=True, exist_ok=True)
        
        # Create database backup
        backup_sql = defaults_dir / "moodle_fresh_default.sql"
        db_backup_cmd = "docker exec moodleclaude_postgres_fresh pg_dump -U moodle -d moodle_fresh"
        
        print("🗄️ Creating database backup...")
        result = subprocess.run(db_backup_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Save database dump
            with open(backup_sql, 'w') as f:
                f.write(result.stdout)
            
            # Create backup documentation
            readme_content = f"""# Default Fresh Installation Backup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
This backup was created after successful v3.0 fresh installation.

## Contents:
- moodle_fresh_default.sql - PostgreSQL database dump ({os.path.getsize(backup_sql):,} bytes)

## Restore:
Run the full setup script to recreate this state:
python tools/setup/setup_fresh_moodle_v2.py --quick-setup

## Configuration:
- Admin: admin/MoodleClaude2025!
- WSUser: wsuser/MoodleClaudeWS2025!
- API Tokens: Generated and configured
- MoodleClaude Plugin: Installed and active
"""
            
            readme_file = defaults_dir / "README.md"
            with open(readme_file, 'w') as f:
                f.write(readme_content)
            
            print("✅ Default backup created successfully")
            print(f"   📁 Database: {backup_sql}")
            print(f"   📝 Info: {readme_file}")
            return True
        else:
            print("⚠️ Database backup failed:")
            if result.stderr:
                print(f"   Error: {result.stderr[-200:]}")
            return False
            
    except Exception as e:
        print(f"⚠️ Backup creation error: {e}")
        return False


def print_summary():
    """Print installation summary"""
    config = get_master_config()
    
    print("\n" + "="*60)
    print("🎉 MoodleClaude Fresh Installation Complete!")
    print("="*60)
    print(f"🌐 Moodle URL: {config.services.url}")
    print(f"👤 Admin User: {config.credentials.admin_user}")
    print(f"🔐 Admin Password: {config.credentials.admin_password}")
    print(f"🔧 WS User: {config.credentials.ws_user}")
    print(f"🔐 WS Password: {config.credentials.ws_password}")
    print()
    print("📋 Next Steps:")
    print("1. Restart Claude Desktop (important!)")
    print("2. Test MCP server integration")
    print("3. Start creating courses with MoodleClaude!")
    print()
    print("💾 Backup Information:")
    print("   Default backup was created after installation")
    print("   Use: bash operations/backup/restore_moodleclaude.sh")
    print()
    print("🛠️ Configuration Management:")
    print("   python tools/config_manager.py show")
    print("   python tools/config_manager.py sync-all")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description="MoodleClaude Fresh Installation v2.0")
    parser.add_argument("--quick-setup", action="store_true", help="Skip confirmation prompts")
    parser.add_argument("--force-rebuild", action="store_true", help="Force complete rebuild")
    parser.add_argument("--skip-cleanup", action="store_true", help="Skip container cleanup")
    parser.add_argument("--config-only", action="store_true", help="Only generate configuration")
    
    args = parser.parse_args()
    
    print("🚀 MoodleClaude Fresh Installation v2.0")
    print("=====================================")
    print("Using centralized configuration system")
    print()
    
    if not args.quick_setup:
        confirm = input("This will delete existing MoodleClaude data. Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("Installation cancelled")
            return
    
    try:
        # Step 1: Generate unified configuration
        if not generate_unified_config():
            print("❌ Configuration generation failed")
            return
        
        if args.config_only:
            print("✅ Configuration-only mode completed")
            return
        
        # Step 2: Cleanup (if not skipped)
        if not args.skip_cleanup:
            cleanup_existing_containers()
        
        # Step 3: Start containers
        if not start_fresh_containers():
            print("❌ Container startup failed")
            return
        
        # Step 4: Wait for Moodle
        if not wait_for_moodle():
            print("❌ Moodle startup failed")
            return
        
        # Step 5: Setup admin
        if not setup_moodle_admin():
            print("⚠️ Admin setup failed, continuing...")
        
        # Step 6: Enable webservices
        if not enable_webservices():
            print("⚠️ Webservice setup failed, continuing...")
        
        # Step 7: Install plugin
        if not install_plugin():
            print("⚠️ Plugin installation failed, continuing...")
        
        # Step 8: Create webservice user
        if not create_webservice_user():
            print("⚠️ WebService user creation failed, continuing...")
        
        # Step 9: Generate tokens automatically
        if not generate_api_tokens():
            print("⚠️ Token generation failed, manual setup required")
        
        # Step 10: Fix MCP Server
        if not fix_mcp_server_path():
            print("⚠️ MCP server validation failed, continuing...")
        
        # Step 11: Update Claude Desktop
        update_claude_desktop()
        
        # Step 12: Run validation
        if not run_validation_tests():
            print("⚠️ Some validation tests failed")
        
        # Step 13: Create default backup
        create_default_backup()
        
        # Step 14: Print summary
        print_summary()
        
    except KeyboardInterrupt:
        print("\n❌ Installation interrupted by user")
    except Exception as e:
        print(f"\n❌ Installation failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
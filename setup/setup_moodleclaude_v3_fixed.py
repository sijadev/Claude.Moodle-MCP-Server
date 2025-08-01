#!/usr/bin/env python3
"""
MoodleClaude v3.0 Complete Setup with Bug Fixes
==============================================
Comprehensive setup script that includes all discovered fixes and optimizations.

Includes fixes for:
- MCP Server 'Server disconnected' error (spawn python ENOENT)
- Access control exception for course creation
- Token permissions and web service configuration
- Claude Desktop integration

Usage:
    python setup_moodleclaude_v3_fixed.py
    python setup_moodleclaude_v3_fixed.py --quick-setup
    python setup_moodleclaude_v3_fixed.py --fix-permissions-only
"""

import os
import sys
import subprocess
import argparse
import time
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Project paths
PROJECT_ROOT = Path(__file__).parent
CLAUDE_CONFIG_PATH = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"

class MoodleClaudeSetupV3:
    """Complete MoodleClaude setup with all bug fixes"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.setup_log = []
        self.config = {}
        
        # Load existing config
        self.load_config()
        
    def log_step(self, message: str, success: bool = True):
        """Log setup steps"""
        emoji = "✅" if success else "❌"
        log_entry = f"{emoji} {message}"
        print(log_entry)
        self.setup_log.append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "success": success
        })
    
    def load_config(self):
        """Load configuration from token file"""
        config_file = self.project_root / "config" / "moodle_tokens.env"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        self.config[key] = value.strip('"\'')
        
        # Set defaults
        self.config.setdefault('MOODLE_URL', 'http://localhost:8080')
        self.config.setdefault('MOODLE_ADMIN_USER', 'admin')
        self.config.setdefault('MOODLE_ADMIN_PASSWORD', 'MoodleClaude2025!')
    
    def run_command(self, cmd: str, description: str = "", capture_output: bool = True, timeout: int = 300) -> tuple[bool, str]:
        """Run shell command with proper error handling"""
        print(f"🔧 {description}")
        try:
            if capture_output:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, 
                    cwd=self.project_root, timeout=timeout
                )
            else:
                result = subprocess.run(cmd, shell=True, cwd=self.project_root, timeout=timeout)
            
            if result.returncode == 0:
                self.log_step(f"Success: {description}")
                output = result.stdout.strip() if capture_output else ""
                if output:
                    print(f"   Output: {output[:200]}...")
                return True, output
            else:
                error_msg = result.stderr.strip() if result.stderr else 'Unknown error'
                self.log_step(f"Failed: {description} - {error_msg[:200]}", False)
                return False, error_msg
        except subprocess.TimeoutExpired:
            self.log_step(f"Timeout: {description}", False)
            return False, "Command timed out"
        except Exception as e:
            self.log_step(f"Exception in {description}: {str(e)}", False)
            return False, str(e)
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        print("🔍 Checking system prerequisites...")
        
        checks = [
            ("docker --version", "Docker installation"),
            ("docker-compose --version", "Docker Compose installation"),
            ("python3 --version", "Python 3 installation"),
        ]
        
        all_good = True
        for cmd, desc in checks:
            success, _ = self.run_command(cmd, f"Checking {desc}")
            if not success:
                all_good = False
        
        return all_good
    
    def setup_docker_environment(self) -> bool:
        """Setup and start Docker environment"""
        print("🐳 Setting up Docker environment...")
        
        # Check if containers are already running
        success, output = self.run_command(
            "docker ps --filter 'name=moodleclaude' --format '{{.Names}}'",
            "Checking running containers"
        )
        
        if success and 'moodleclaude_app_fresh' in output:
            self.log_step("Moodle containers already running")
            return True
        
        # Start Docker containers
        docker_compose_file = self.project_root / "docker-compose.yml"
        if not docker_compose_file.exists():
            # Try alternative locations
            for alt_path in ["operations/docker/docker-compose.yml", "docker/docker-compose.yml"]:
                alt_file = self.project_root / alt_path
                if alt_file.exists():
                    docker_compose_file = alt_file
                    break
        
        if not docker_compose_file.exists():
            self.log_step("Docker compose file not found", False)
            return False
        
        # Start containers
        success, _ = self.run_command(
            f"docker-compose -f {docker_compose_file} up -d",
            "Starting Docker containers",
            timeout=600
        )
        
        if success:
            # Wait for containers to be healthy
            print("⏳ Waiting for containers to be ready...")
            time.sleep(30)
            return True
        
        return False
    
    def get_python_path(self) -> str:
        """Get the correct Python path for MCP server"""
        # Check virtual environment first
        venv_python = self.project_root / ".venv" / "bin" / "python3"
        if venv_python.exists():
            return str(venv_python)
        
        # Check system Python
        success, output = self.run_command("which python3", "Finding Python3 path")
        if success and output.strip():
            return output.strip()
        
        # Fallback
        return "python3"
    
    def create_web_service_setup(self) -> bool:
        """Create and run web service setup script"""
        print("🌐 Setting up Moodle web services...")
        
        # Create web service setup script
        setup_script = '''<?php
// MoodleClaude Web Service Setup Script
define('CLI_SCRIPT', true);
require_once('/bitnami/moodle/config.php');
require_once($CFG->libdir.'/adminlib.php');

echo "🚀 MoodleClaude Web Service Setup\\n";
echo "================================\\n";

try {
    // Enable web services
    echo "🌐 Enabling web services...\\n";
    set_config('enablewebservices', 1);
    
    // Enable REST protocol
    echo "🔌 Enabling REST protocol...\\n";
    $protocols = explode(',', get_config('core', 'webserviceprotocols'));
    if (!in_array('rest', $protocols)) {
        $protocols[] = 'rest';
        set_config('webserviceprotocols', implode(',', $protocols));
    }
    
    // Create/update web service
    echo "⚙️  Setting up web service...\\n";
    $webservice = $DB->get_record('external_services', array('shortname' => 'moodleclaude_ws'));
    
    if (!$webservice) {
        $webservice = new stdClass();
        $webservice->name = 'MoodleClaude Web Service';
        $webservice->shortname = 'moodleclaude_ws';
        $webservice->component = 'core';
        $webservice->timecreated = time();
        $webservice->timemodified = time();
        $webservice->enabled = 1;
        $webservice->restrictedusers = 0;
        $webservice->downloadfiles = 1;
        $webservice->uploadfiles = 1;
        $webservice->id = $DB->insert_record('external_services', $webservice);
        echo "✅ Created new web service\\n";
    } else {
        $webservice->enabled = 1;
        $webservice->restrictedusers = 0;
        $webservice->downloadfiles = 1;
        $webservice->uploadfiles = 1;
        $webservice->timemodified = time();
        $DB->update_record('external_services', $webservice);
        echo "✅ Updated existing web service\\n";
    }
    
    // Add functions to web service
    echo "🔧 Adding functions to web service...\\n";
    $functions = [
        'core_webservice_get_site_info',
        'core_course_get_courses',
        'core_course_create_courses',
        'core_course_delete_courses',
        'core_course_get_contents',
        'core_user_get_users',
        'core_user_create_users',
        'core_enrol_get_enrolled_users',
        'core_course_get_categories'
    ];
    
    foreach ($functions as $function) {
        $exists = $DB->get_record('external_services_functions', [
            'externalserviceid' => $webservice->id,
            'functionname' => $function
        ]);
        
        if (!$exists) {
            $service_function = new stdClass();
            $service_function->externalserviceid = $webservice->id;
            $service_function->functionname = $function;
            $DB->insert_record('external_services_functions', $service_function);
            echo "  ✅ Added function: $function\\n";
        }
    }
    
    echo "\\n🎯 Web service setup complete!\\n";
    
} catch (Exception $e) {
    echo "❌ Error: " . $e->getMessage() . "\\n";
    exit(1);
}
?>'''
        
        # Write setup script to temporary file
        setup_file = self.project_root / "temp_webservice_setup.php"
        with open(setup_file, 'w') as f:
            f.write(setup_script)
        
        try:
            # Copy to container and run
            success1, _ = self.run_command(
                "docker cp temp_webservice_setup.php moodleclaude_app_fresh:/bitnami/moodle/",
                "Copying web service setup script to container"
            )
            
            if success1:
                success2, _ = self.run_command(
                    "docker exec moodleclaude_app_fresh php -f /bitnami/moodle/temp_webservice_setup.php",
                    "Running web service setup script"
                )
                
                if success2:
                    self.log_step("Web service setup completed successfully")
                    return True
            
            return False
            
        finally:
            # Clean up temporary file
            if setup_file.exists():
                setup_file.unlink()
    
    def fix_token_permissions(self) -> bool:
        """Fix token permissions and roles"""
        print("🔐 Fixing token permissions and roles...")
        
        # Create permissions fix script
        fix_script = '''<?php
// Fix course creation capabilities directly
define('CLI_SCRIPT', true);
require_once('/bitnami/moodle/config.php');

echo "🔧 Fixing course creation capabilities\\n";
echo "=====================================\\n";

try {
    $context_system = context_system::instance();
    
    // Get admin and wsuser
    $admin = $DB->get_record('user', array('username' => 'admin'));
    $wsuser = $DB->get_record('user', array('username' => 'wsuser'));
    
    // Get manager role
    $manager_role = $DB->get_record('role', array('shortname' => 'manager'));
    
    if (!$manager_role) {
        echo "❌ Manager role not found\\n";
        exit(1);
    }
    
    echo "✅ Found manager role (ID: {$manager_role->id})\\n";
    
    // Ensure course creation capability is allowed for manager role
    $capability = 'moodle/course:create';
    
    $role_capability = $DB->get_record('role_capabilities', [
        'roleid' => $manager_role->id,
        'capability' => $capability,
        'contextid' => $context_system->id
    ]);
    
    if (!$role_capability) {
        $role_capability = new stdClass();
        $role_capability->contextid = $context_system->id;
        $role_capability->roleid = $manager_role->id;
        $role_capability->capability = $capability;
        $role_capability->permission = 1; // Allow
        $role_capability->timemodified = time();
        $role_capability->modifierid = 2; // Admin user ID
        $DB->insert_record('role_capabilities', $role_capability);
        echo "✅ Added course creation capability to Manager role\\n";
    } else {
        if ($role_capability->permission != 1) {
            $role_capability->permission = 1;
            $role_capability->timemodified = time();
            $DB->update_record('role_capabilities', $role_capability);
            echo "✅ Updated course creation capability for Manager role\\n";
        } else {
            echo "ℹ️  Course creation capability already exists for Manager role\\n";
        }
    }
    
    // Assign manager role to users
    foreach (['admin' => $admin, 'wsuser' => $wsuser] as $username => $user) {
        if ($user) {
            $existing_assignment = $DB->get_record('role_assignments', [
                'roleid' => $manager_role->id,
                'userid' => $user->id,
                'contextid' => $context_system->id
            ]);
            
            if (!$existing_assignment) {
                $role_assignment = new stdClass();
                $role_assignment->roleid = $manager_role->id;
                $role_assignment->contextid = $context_system->id;
                $role_assignment->userid = $user->id;
                $role_assignment->timemodified = time();
                $role_assignment->modifierid = 2;
                $role_assignment->component = '';
                $role_assignment->itemid = 0;
                $role_assignment->sortorder = 0;
                $DB->insert_record('role_assignments', $role_assignment);
                echo "✅ Assigned Manager role to $username\\n";
            } else {
                echo "ℹ️  Manager role already assigned to $username\\n";
            }
        }
    }
    
    echo "\\n🎯 Capabilities setup complete!\\n";
    
} catch (Exception $e) {
    echo "❌ Error: " . $e->getMessage() . "\\n";
    exit(1);
}
?>'''
        
        # Write and run fix script
        fix_file = self.project_root / "temp_fix_permissions.php"
        with open(fix_file, 'w') as f:
            f.write(fix_script)
        
        try:
            # Copy to container and run
            success1, _ = self.run_command(
                "docker cp temp_fix_permissions.php moodleclaude_app_fresh:/bitnami/moodle/",
                "Copying permissions fix script to container"
            )
            
            if success1:
                success2, _ = self.run_command(
                    "docker exec moodleclaude_app_fresh php -f /bitnami/moodle/temp_fix_permissions.php",
                    "Running permissions fix script"
                )
                
                return success2
            
            return False
            
        finally:
            # Clean up temporary file
            if fix_file.exists():
                fix_file.unlink()
    
    def reassign_tokens_to_service(self) -> bool:
        """Reassign existing tokens to MoodleClaude web service"""
        print("🔄 Reassigning tokens to MoodleClaude web service...")
        
        reassign_script = '''<?php
// Reassign existing tokens to MoodleClaude web service
define('CLI_SCRIPT', true);
require_once('/bitnami/moodle/config.php');

echo "🔄 Reassigning tokens to MoodleClaude web service\\n";
echo "===============================================\\n";

try {
    // Get our web service
    $moodleclaude_service = $DB->get_record('external_services', array('shortname' => 'moodleclaude_ws'));
    $mobile_service = $DB->get_record('external_services', array('shortname' => 'moodle_mobile_app'));
    
    if (!$moodleclaude_service) {
        echo "❌ MoodleClaude web service not found!\\n";
        exit(1);
    }
    
    if (!$mobile_service) {
        echo "❌ Mobile app web service not found!\\n";
        exit(1);
    }
    
    echo "✅ Found MoodleClaude web service (ID: {$moodleclaude_service->id})\\n";
    echo "✅ Found Mobile app web service (ID: {$mobile_service->id})\\n";
    
    // Get tokens for admin and wsuser from mobile service
    $admin = $DB->get_record('user', array('username' => 'admin'));
    $wsuser = $DB->get_record('user', array('username' => 'wsuser'));
    
    $tokens_updated = 0;
    
    if ($admin) {
        $admin_token = $DB->get_record('external_tokens', [
            'userid' => $admin->id,
            'externalserviceid' => $mobile_service->id
        ]);
        
        if ($admin_token) {
            // Update the token to use our service
            $admin_token->externalserviceid = $moodleclaude_service->id;
            $DB->update_record('external_tokens', $admin_token);
            echo "✅ Reassigned admin token ({$admin_token->token}) to MoodleClaude service\\n";
            $tokens_updated++;
        }
    }
    
    if ($wsuser) {
        $wsuser_token = $DB->get_record('external_tokens', [
            'userid' => $wsuser->id,
            'externalserviceid' => $mobile_service->id
        ]);
        
        if ($wsuser_token) {
            // Update the token to use our service
            $wsuser_token->externalserviceid = $moodleclaude_service->id;
            $DB->update_record('external_tokens', $wsuser_token);
            echo "✅ Reassigned wsuser token ({$wsuser_token->token}) to MoodleClaude service\\n";
            $tokens_updated++;
        }
    }
    
    echo "\\n🎯 Reassigned {$tokens_updated} tokens to MoodleClaude web service!\\n";
    echo "🔄 Tokens should now have course creation permissions.\\n";
    
} catch (Exception $e) {
    echo "❌ Error: " . $e->getMessage() . "\\n";
    exit(1);
}
?>'''
        
        # Write and run reassign script
        reassign_file = self.project_root / "temp_reassign_tokens.php"
        with open(reassign_file, 'w') as f:
            f.write(reassign_script)
        
        try:
            # Copy to container and run
            success1, _ = self.run_command(
                "docker cp temp_reassign_tokens.php moodleclaude_app_fresh:/bitnami/moodle/",
                "Copying token reassignment script to container"
            )
            
            if success1:
                success2, _ = self.run_command(
                    "docker exec moodleclaude_app_fresh php -f /bitnami/moodle/temp_reassign_tokens.php",
                    "Running token reassignment script"
                )
                
                return success2
            
            return False
            
        finally:
            # Clean up temporary file
            if reassign_file.exists():
                reassign_file.unlink()
    
    def setup_claude_desktop_config(self) -> bool:
        """Setup Claude Desktop configuration with correct Python path"""
        print("🖥️  Setting up Claude Desktop configuration...")
        
        # Get correct Python path
        python_path = self.get_python_path()
        
        # Get tokens from config
        basic_token = self.config.get('MOODLE_BASIC_TOKEN', self.config.get('MOODLE_ADMIN_TOKEN', ''))
        enhanced_token = self.config.get('MOODLE_PLUGIN_TOKEN', basic_token)
        
        # Create Claude Desktop config
        claude_config = {
            "mcpServers": {
                "moodleclaude-stable": {
                    "command": python_path,
                    "args": [
                        str(self.project_root / "src/core/working_mcp_server.py")
                    ],
                    "env": {
                        "MOODLE_URL": self.config.get('MOODLE_URL', 'http://localhost:8080'),
                        "MOODLE_TOKEN_BASIC": basic_token,
                        "MOODLE_TOKEN_ENHANCED": enhanced_token,
                        "MOODLE_USERNAME": self.config.get('MOODLE_ADMIN_USER', 'admin'),
                        "SERVER_NAME": "stable-moodle-mcp",
                        "LOG_LEVEL": "INFO"
                    },
                    "timeout": 30,
                    "autoApprove": [
                        "test_connection",
                        "get_courses",
                        "create_course"
                    ],
                    "disabled": False,
                    "description": "Stable MoodleClaude MCP Server - dependency-free and working",
                    "version": "1.0.0"
                }
            },
            "globalSettings": {
                "logging": {
                    "level": "INFO",
                    "enableFileLogging": True,
                    "logDirectory": str(self.project_root / "logs")
                }
            }
        }
        
        # Ensure Claude config directory exists
        CLAUDE_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Write Claude Desktop config
        try:
            with open(CLAUDE_CONFIG_PATH, 'w') as f:
                json.dump(claude_config, f, indent=2)
            
            self.log_step(f"Claude Desktop config written to {CLAUDE_CONFIG_PATH}")
            self.log_step(f"Using Python path: {python_path}")
            return True
            
        except Exception as e:
            self.log_step(f"Failed to write Claude Desktop config: {str(e)}", False)
            return False
    
    def validate_setup(self) -> bool:
        """Validate the complete setup"""
        print("🔍 Validating setup...")
        
        validation_checks = []
        
        # Check if containers are running
        success, output = self.run_command(
            "docker ps --filter 'name=moodleclaude_app_fresh' --format '{{.Names}}'",
            "Checking Moodle container"
        )
        validation_checks.append(("Moodle container running", success and 'moodleclaude_app_fresh' in output))
        
        # Check if Moodle is accessible
        success, _ = self.run_command(
            f"curl -s -o /dev/null -w '%{{http_code}}' {self.config.get('MOODLE_URL', 'http://localhost:8080')}",
            "Checking Moodle accessibility"
        )
        validation_checks.append(("Moodle accessible", success))
        
        # Check if Claude config exists
        validation_checks.append(("Claude Desktop config exists", CLAUDE_CONFIG_PATH.exists()))
        
        # Check if MCP server file exists
        mcp_server_path = self.project_root / "src/core/working_mcp_server.py"
        validation_checks.append(("MCP server file exists", mcp_server_path.exists()))
        
        # Check if Python path is correct
        python_path = self.get_python_path()
        validation_checks.append(("Python path valid", Path(python_path).exists()))
        
        # Display validation results
        print("\n📋 Validation Results:")
        all_passed = True
        for check_name, passed in validation_checks:
            emoji = "✅" if passed else "❌"
            print(f"  {emoji} {check_name}")
            if not passed:
                all_passed = False
        
        return all_passed
    
    def generate_setup_report(self):
        """Generate a comprehensive setup report"""
        report = {
            "setup_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "python_path": self.get_python_path(),
            "moodle_url": self.config.get('MOODLE_URL', 'http://localhost:8080'),
            "claude_config_path": str(CLAUDE_CONFIG_PATH),
            "setup_log": self.setup_log,
            "validation_passed": self.validate_setup()
        }
        
        # Save report
        report_file = self.project_root / "setup_report_v3_fixed.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Setup report saved to: {report_file}")
        return report
    
    def run_complete_setup(self, quick_setup: bool = False, fix_permissions_only: bool = False) -> bool:
        """Run the complete setup process"""
        print("🚀 Starting MoodleClaude v3.0 Complete Setup with Bug Fixes")
        print("=" * 80)
        
        if fix_permissions_only:
            print("🔧 Running permissions fix only...")
            success = (
                self.create_web_service_setup() and
                self.fix_token_permissions() and
                self.reassign_tokens_to_service()
            )
            
            if success:
                print("✅ Permissions fix completed successfully!")
            else:
                print("❌ Permissions fix failed!")
            
            return success
        
        success = True
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites check failed!")
            return False
        
        # Step 2: Setup Docker environment (unless quick setup)
        if not quick_setup:
            if not self.setup_docker_environment():
                print("❌ Docker environment setup failed!")
                success = False
        
        # Step 3: Setup web services and fix permissions
        if not self.create_web_service_setup():
            print("❌ Web service setup failed!")
            success = False
        
        if not self.fix_token_permissions():
            print("❌ Token permissions fix failed!")
            success = False
        
        if not self.reassign_tokens_to_service():
            print("❌ Token reassignment failed!")
            success = False
        
        # Step 4: Setup Claude Desktop configuration
        if not self.setup_claude_desktop_config():
            print("❌ Claude Desktop setup failed!")
            success = False
        
        # Step 5: Validate setup
        if not self.validate_setup():
            print("❌ Setup validation failed!")
            success = False
        
        # Step 6: Generate report
        self.generate_setup_report()
        
        if success:
            print("\n🎉 MoodleClaude v3.0 setup completed successfully!")
            print("=" * 60)
            print("✅ All components are configured and working")
            print("✅ MCP Server connectivity fixed")
            print("✅ Course creation permissions enabled")
            print("✅ Claude Desktop integration ready")
            print("\n🔄 Please restart Claude Desktop to load the new configuration")
        else:
            print("\n❌ Setup completed with some errors!")
            print("📋 Check the setup log for details")
        
        return success


def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="MoodleClaude v3.0 Complete Setup with Bug Fixes")
    parser.add_argument("--quick-setup", action="store_true", 
                       help="Skip Docker setup (assumes containers are already running)")
    parser.add_argument("--fix-permissions-only", action="store_true",
                       help="Run only the permissions fix (for existing installations)")
    
    args = parser.parse_args()
    
    setup = MoodleClaudeSetupV3()
    success = setup.run_complete_setup(
        quick_setup=args.quick_setup,
        fix_permissions_only=args.fix_permissions_only
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Moodle Course Creation Enabler
===============================

Aktiviert Kurs-Erstellungsberechtigungen in Moodle direkt über die Datenbank.
"""

import os
import sys
from pathlib import Path
import logging
from datetime import datetime
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class MoodleCourseCreationEnabler:
    """Tool zur Aktivierung von Kurs-Erstellungsberechtigungen."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_file = self.project_root / "config/moodle_tokens.env"
        self.load_config()
        
    def load_config(self):
        """Lädt die Konfiguration."""
        self.config = {}
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        self.config[key] = value.strip('"\'')
        
        self.moodle_url = self.config.get('MOODLE_URL', 'http://localhost:8080')
        logger.info(f"✅ Configuration loaded for: {self.moodle_url}")
    
    def fix_via_moodle_cli(self):
        """Versucht die Berechtigungen über Moodle CLI zu korrigieren."""
        logger.info("🔧 Attempting to fix permissions via Moodle CLI...")
        
        # Common Moodle installation paths
        possible_moodle_paths = [
            "/Applications/MAMP/htdocs/moodle",
            "/var/www/html/moodle",
            "/usr/local/var/www/moodle",
            "/opt/homebrew/var/www/moodle",
            Path.home() / "Sites/moodle"
        ]
        
        moodle_path = None
        for path in possible_moodle_paths:
            path = Path(path)
            if path.exists() and (path / "config.php").exists():
                moodle_path = path
                logger.info(f"📁 Found Moodle installation: {moodle_path}")
                break
        
        if not moodle_path:
            logger.warning("⚠️  Could not find Moodle installation directory")
            return False
        
        cli_path = moodle_path / "admin/cli"
        
        if not cli_path.exists():
            logger.warning("⚠️  Moodle CLI directory not found")
            return False
        
        try:
            # Enable web services
            logger.info("🌐 Enabling web services...")
            subprocess.run([
                'php', str(cli_path / 'cfg.php'),
                '--name=enablewebservices',
                '--set=1'
            ], check=True, capture_output=True)
            
            # Enable REST protocol
            logger.info("🔌 Enabling REST protocol...")
            subprocess.run([
                'php', str(cli_path / 'cfg.php'),
                '--name=webserviceprotocols',
                '--set=rest'
            ], check=True, capture_output=True)
            
            logger.info("✅ Moodle web service settings updated")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ CLI command failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error running CLI commands: {e}")
            return False
    
    def create_web_service_setup_script(self):
        """Erstellt ein PHP-Script zur Web Service-Konfiguration."""
        logger.info("📝 Creating web service setup script...")
        
        php_script = """<?php
// MoodleClaude Web Service Setup Script
define('CLI_SCRIPT', true);
require_once(__DIR__ . '/../../config.php');
require_once($CFG->libdir.'/adminlib.php');

echo "🚀 MoodleClaude Web Service Setup\\n";
echo "================================\\n";

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
    } else {
        echo "  ℹ️  Function already exists: $function\\n";
    }
}

// Get or create admin user token
echo "🔑 Setting up admin token...\\n";
$admin = $DB->get_record('user', array('username' => 'admin'));
if ($admin) {
    $existing_token = $DB->get_record('external_tokens', [
        'userid' => $admin->id,
        'externalserviceid' => $webservice->id
    ]);
    
    if (!$existing_token) {
        $token = new stdClass();
        $token->token = md5(uniqid(rand(), true));
        $token->userid = $admin->id;
        $token->externalserviceid = $webservice->id;
        $token->contextid = context_system::instance()->id;
        $token->creatorid = $admin->id;
        $token->timecreated = time();
        $token->validuntil = 0; // Never expires
        $DB->insert_record('external_tokens', $token);
        echo "✅ Created admin token: {$token->token}\\n";
    } else {
        echo "✅ Admin token exists: {$existing_token->token}\\n";
    }
}

// Get or create wsuser token
echo "🔑 Setting up wsuser token...\\n";
$wsuser = $DB->get_record('user', array('username' => 'wsuser'));
if ($wsuser) {
    $existing_token = $DB->get_record('external_tokens', [
        'userid' => $wsuser->id,
        'externalserviceid' => $webservice->id
    ]);
    
    if (!$existing_token) {
        $token = new stdClass();
        $token->token = md5(uniqid(rand(), true));
        $token->userid = $wsuser->id;
        $token->externalserviceid = $webservice->id;
        $token->contextid = context_system::instance()->id;
        $token->creatorid = $admin->id ?? 2;
        $token->timecreated = time();
        $token->validuntil = 0; // Never expires
        $DB->insert_record('external_tokens', $token);
        echo "✅ Created wsuser token: {$token->token}\\n";
    } else {
        echo "✅ WSUser token exists: {$existing_token->token}\\n";
    }
}

// Assign course creation capability to Manager role
echo "🎓 Setting up course creation capabilities...\\n";
$manager_role = $DB->get_record('role', array('shortname' => 'manager'));
$context_system = context_system::instance();

if ($manager_role) {
    // Assign course creation capability
    $capability = 'moodle/course:create';
    
    $existing = $DB->get_record('role_capabilities', [
        'roleid' => $manager_role->id,
        'capability' => $capability,
        'contextid' => $context_system->id
    ]);
    
    if (!$existing) {
        $role_capability = new stdClass();
        $role_capability->contextid = $context_system->id;
        $role_capability->roleid = $manager_role->id;
        $role_capability->capability = $capability;
        $role_capability->permission = 1; // Allow
        $role_capability->timemodified = time();
        $role_capability->modifierid = $admin->id ?? 2;
        $DB->insert_record('role_capabilities', $role_capability);
        echo "✅ Added course creation capability to Manager role\\n";
    } else {
        if ($existing->permission != 1) {
            $existing->permission = 1;
            $existing->timemodified = time();
            $DB->update_record('role_capabilities', $existing);
            echo "✅ Updated course creation capability for Manager role\\n";
        } else {
            echo "ℹ️  Course creation capability already exists for Manager role\\n";
        }
    }
    
    // Assign Manager role to admin and wsuser in system context
    foreach (['admin', 'wsuser'] as $username) {
        $user = $DB->get_record('user', array('username' => $username));
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
                $role_assignment->modifierid = $admin->id ?? 2;
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
}

echo "\\n🎯 Setup complete! Web services should now work properly.\\n";
echo "🔄 Please restart your web server and test the course creation functionality.\\n";
?>"""
        
        # Find Moodle installation
        possible_paths = [
            "/Applications/MAMP/htdocs/moodle",
            "/var/www/html/moodle",
            "/usr/local/var/www/moodle",
            "/opt/homebrew/var/www/moodle"
        ]
        
        moodle_path = None
        for path in possible_paths:
            path = Path(path)
            if path.exists() and (path / "config.php").exists():
                moodle_path = path
                break
        
        if not moodle_path:
            logger.warning("⚠️  Could not find Moodle installation")
            # Save script to project directory instead
            script_path = self.project_root / "setup_webservices.php"
            with open(script_path, 'w') as f:
                f.write(php_script)
            logger.info(f"📝 Web service setup script saved to: {script_path}")
            logger.info("📋 To run: Copy this file to your Moodle root directory and run: php setup_webservices.php")
            return script_path
        
        # Save script to Moodle directory
        script_path = moodle_path / "setup_webservices.php"
        with open(script_path, 'w') as f:
            f.write(php_script)
        
        logger.info(f"📝 Web service setup script created: {script_path}")
        
        # Try to run the script
        try:
            logger.info("🚀 Running web service setup script...")
            result = subprocess.run([
                'php', str(script_path)
            ], capture_output=True, text=True, cwd=str(moodle_path))
            
            if result.returncode == 0:
                logger.info("✅ Setup script executed successfully!")
                logger.info("📋 Output:")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        logger.info(f"  {line}")
                
                # Clean up script
                script_path.unlink()
                return True
            else:
                logger.error(f"❌ Setup script failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error running setup script: {e}")
            return False
    
    def update_tokens_file(self):
        """Aktualisiert die Token-Datei mit neuen Tokens."""
        logger.info("🔄 Updating tokens file...")
        
        # This would typically involve extracting the new tokens from Moodle
        # For now, we'll trigger a regeneration
        try:
            subprocess.run([
                'python', str(self.project_root / 'setup_moodle.py'), '--regenerate-tokens'
            ], check=True, capture_output=True)
            
            logger.info("✅ Tokens regenerated successfully")
            return True
            
        except subprocess.CalledProcessError:
            logger.warning("⚠️  Could not regenerate tokens automatically")
            return False
        except Exception as e:
            logger.error(f"❌ Error regenerating tokens: {e}")
            return False
    
    def run_fix(self):
        """Führt die komplette Reparatur durch."""
        logger.info("🚀 Starting Moodle course creation fix...")
        logger.info("=" * 60)
        
        success = False
        
        # Try PHP script method
        if self.create_web_service_setup_script():
            success = True
            logger.info("✅ Web service setup completed via PHP script")
        
        # Try CLI method as backup
        if not success:
            logger.info("🔄 Trying CLI method...")
            if self.fix_via_moodle_cli():
                success = True
                logger.info("✅ Web service setup completed via CLI")
        
        if success:
            # Update tokens
            self.update_tokens_file()
            
            logger.info("\n" + "=" * 60)
            logger.info("🎯 FIX COMPLETE")
            logger.info("=" * 60)
            logger.info("✅ Moodle web services have been configured")
            logger.info("🔧 Course creation should now work")
            logger.info("🔄 Please restart Claude Desktop to reload the MCP server")
        else:
            logger.warning("⚠️  Automatic fix failed")
            logger.info("📋 Manual steps required:")
            logger.info("  1. Log into Moodle as admin")
            logger.info("  2. Go to Site Administration > Server > Web services")
            logger.info("  3. Enable web services")
            logger.info("  4. Add course creation functions to your web service")
            logger.info("  5. Assign appropriate roles to your web service users")
        
        return success

def main():
    """Main function."""
    print("🔧 MoodleClaude Course Creation Enabler")
    print("=" * 60)
    print("🚀 Fixing Moodle course creation permissions...")
    
    enabler = MoodleCourseCreationEnabler()
    success = enabler.run_fix()
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
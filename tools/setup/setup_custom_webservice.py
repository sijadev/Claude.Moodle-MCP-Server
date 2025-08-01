#!/usr/bin/env python3
"""
MoodleClaude Custom Web Service Setup
====================================

This script automates the creation and configuration of a dedicated
MoodleClaude web service instead of relying on the mobile app service.

Features:
- Creates custom web service with all required functions
- Sets up service user with proper permissions
- Generates secure token
- Tests the configuration
- Updates environment variables

Usage: python setup_custom_webservice.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

import requests


class MoodleWebServiceSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.env_file = self.project_root / ".env"
        self.config_file = Path(__file__).parent / "moodleclaude_webservice_config.json"

        # Load current environment
        self.moodle_url = os.getenv("MOODLE_URL", "http://localhost:8080")
        self.moodle_admin_user = os.getenv("MOODLE_ADMIN_USER", "admin")
        self.moodle_admin_password = os.getenv("MOODLE_ADMIN_PASSWORD", "")

    def print_header(self):
        print("🚀 MoodleClaude Custom Web Service Setup")
        print("=" * 50)
        print(f"🌐 Moodle URL: {self.moodle_url}")
        print(f"👤 Admin User: {self.moodle_admin_user}")
        print()

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        print("🔍 Checking prerequisites...")

        # Check if we can access Moodle
        try:
            response = requests.get(f"{self.moodle_url}/login/index.php", timeout=10)
            if response.status_code != 200:
                print(f"❌ Cannot access Moodle at {self.moodle_url}")
                return False
            print("✅ Moodle is accessible")
        except Exception as e:
            print(f"❌ Cannot access Moodle: {e}")
            return False

        # Check if admin credentials are provided
        if not self.moodle_admin_password:
            print("❌ MOODLE_ADMIN_PASSWORD not set in environment")
            print("   Please set it in your .env file or environment")
            return False
        print("✅ Admin credentials available")

        # Check if PHP script exists
        php_script = Path(__file__).parent / "create_moodleclaude_webservice.php"
        if not php_script.exists():
            print(f"❌ PHP setup script not found: {php_script}")
            return False
        print("✅ PHP setup script found")

        return True

    def run_php_setup(self) -> bool:
        """Run the PHP script to create the web service."""
        print("\n🔧 Running PHP web service creation script...")

        php_script = Path(__file__).parent / "create_moodleclaude_webservice.php"

        # Set environment variables for the PHP script
        env = os.environ.copy()
        env.update(
            {
                "MOODLE_URL": self.moodle_url,
                "MOODLE_ADMIN_USER": self.moodle_admin_user,
                "MOODLE_ADMIN_PASSWORD": self.moodle_admin_password,
            }
        )

        try:
            # Try different PHP executables
            php_executables = ["php", "php8.1", "php8.0", "php7.4", "/usr/bin/php"]
            php_exe = None

            for exe in php_executables:
                try:
                    subprocess.run([exe, "--version"], capture_output=True, check=True)
                    php_exe = exe
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue

            if not php_exe:
                print("❌ PHP not found. Please install PHP or add it to PATH")
                return False

            print(f"✅ Using PHP: {php_exe}")

            # Run the PHP script
            result = subprocess.run(
                [php_exe, str(php_script)],
                cwd=str(self.project_root),
                env=env,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                print("✅ PHP script executed successfully:")
                print(result.stdout)
                return True
            else:
                print("❌ PHP script failed:")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("❌ PHP script timed out")
            return False
        except Exception as e:
            print(f"❌ Error running PHP script: {e}")
            return False

    def load_config(self) -> Dict[str, Any]:
        """Load the configuration created by the PHP script."""
        if not self.config_file.exists():
            raise Exception(f"Configuration file not found: {self.config_file}")

        with open(self.config_file, "r") as f:
            return json.load(f)

    def update_environment(self, config: Dict[str, Any]) -> bool:
        """Update the .env file with new web service configuration."""
        print("\n🔧 Updating environment configuration...")

        try:
            # Read existing .env file
            env_content = []
            if self.env_file.exists():
                with open(self.env_file, "r") as f:
                    env_content = f.readlines()

            # Remove old MoodleClaude token entries
            env_content = [
                line
                for line in env_content
                if not any(
                    key in line
                    for key in [
                        "MOODLE_TOKEN_ENHANCED",
                        "MOODLE_WS_USER",
                        "MOODLE_SERVICE_ID",
                    ]
                )
            ]

            # Add new configuration
            new_lines = [
                f"\n# MoodleClaude Custom Web Service Configuration\n",
                f"MOODLE_TOKEN_ENHANCED=\"{config['token']}\"\n",
                f"MOODLE_WS_USER=\"{config['user']}\"\n",
                f"MOODLE_SERVICE_ID=\"{config['service_id']}\"\n",
                f"# Created: {config['created']}\n\n",
            ]

            env_content.extend(new_lines)

            # Write back to .env file
            with open(self.env_file, "w") as f:
                f.writelines(env_content)

            print(f"✅ Environment updated: {self.env_file}")
            return True

        except Exception as e:
            print(f"❌ Error updating environment: {e}")
            return False

    def test_webservice(self, config: Dict[str, Any]) -> bool:
        """Test the newly created web service."""
        print("\n🧪 Testing web service configuration...")

        try:
            # Test basic connectivity
            test_url = f"{self.moodle_url}/webservice/rest/server.php"
            test_data = {
                "wstoken": config["token"],
                "wsfunction": "core_webservice_get_site_info",
                "moodlewsrestformat": "json",
            }

            response = requests.post(test_url, data=test_data, timeout=30)

            if response.status_code == 200:
                result = response.json()

                if "exception" in result:
                    print(
                        f"❌ Web service error: {result.get('message', 'Unknown error')}"
                    )
                    return False

                print("✅ Web service test successful!")
                print(f"   Site: {result.get('sitename', 'Unknown')}")
                print(f"   Version: {result.get('release', 'Unknown')}")
                print(f"   User: {result.get('username', 'Unknown')}")
                print(f"   Functions available: {len(result.get('functions', []))}")

                return True
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Web service test failed: {e}")
            return False

    def run_setup(self) -> bool:
        """Run the complete setup process."""
        self.print_header()

        if not self.check_prerequisites():
            return False

        if not self.run_php_setup():
            return False

        try:
            config = self.load_config()
            print(
                f"\n✅ Configuration loaded: {config['functions_added']} functions added"
            )
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            return False

        if not self.update_environment(config):
            return False

        if not self.test_webservice(config):
            print("⚠️  Web service created but test failed - check configuration")
            return False

        self.print_success_summary(config)
        return True

    def print_success_summary(self, config: Dict[str, Any]):
        """Print final success summary."""
        print("\n🎉 SUCCESS! MoodleClaude Custom Web Service Ready!")
        print("=" * 60)
        print(f"✅ Service: {config['service_name']}")
        print(f"✅ Functions: {config['functions_added']} added")
        print(f"✅ Token: {config['token'][:8]}...")
        print(f"✅ User: {config['user']}")
        print(f"✅ Environment: Updated")
        print(f"✅ Test: Passed")
        print()
        print("🚀 Next Steps:")
        print("   1. Restart your MCP server")
        print("   2. Test with Claude Desktop")
        print("   3. All functions should now work without fallbacks!")
        print()
        print("🔧 Troubleshooting:")
        print("   • Configuration saved to:", self.config_file)
        print("   • Environment updated in:", self.env_file)
        print("   • Web service URL:", config["webservice_url"])


def main():
    """Main setup function."""
    setup = MoodleWebServiceSetup()

    try:
        success = setup.run_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

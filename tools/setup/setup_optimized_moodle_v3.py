#!/usr/bin/env python3
"""
MoodleClaude Optimized Installation v3.0
=======================================
Complete setup with performance optimizations and enhanced features
Automatically configures optimized MCP server and Claude Desktop integration

Usage:
    python tools/setup/setup_optimized_moodle_v3.py
    python tools/setup/setup_optimized_moodle_v3.py --quick-setup
    python tools/setup/setup_optimized_moodle_v3.py --skip-docker
    python tools/setup/setup_optimized_moodle_v3.py --setup-only-claude-config
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

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


class OptimizedMoodleSetup:
    """Optimized MoodleClaude setup with performance enhancements"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.master_config = get_master_config()
        self.setup_log = []

    def log_step(self, message: str, success: bool = True):
        """Log setup steps"""
        emoji = "✅" if success else "❌"
        log_entry = f"{emoji} {message}"
        print(log_entry)
        self.setup_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "success": success,
            }
        )

    def run_command(
        self, cmd: str, description: str = "", capture_output: bool = True
    ) -> bool:
        """Run shell command with proper error handling"""
        print(f"🔧 {description}")
        try:
            if capture_output:
                result = subprocess.run(
                    cmd,
                    shell=True,  # nosec B602 - admin setup script with controlled input
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
            else:
                result = subprocess.run(
                    cmd, shell=True, cwd=self.project_root
                )  # nosec B602 - admin setup script

            if result.returncode == 0:
                self.log_step(f"Success: {description}")
                if capture_output and result.stdout.strip():
                    print(f"   Output: {result.stdout.strip()[:200]}")
                return True
            else:
                self.log_step(
                    f"Failed: {description} - {result.stderr.strip()[:200] if result.stderr else 'Unknown error'}",
                    False,
                )
                return False
        except Exception as e:
            self.log_step(f"Exception in {description}: {str(e)}", False)
            return False

    def check_prerequisites(self) -> bool:
        """Check system prerequisites for optimized setup"""
        print("🔍 Checking prerequisites for optimized setup...")

        checks = [
            ("docker --version", "Docker installation"),
            ("docker-compose --version", "Docker Compose installation"),
            ("python --version", "Python installation"),
        ]

        all_good = True
        for cmd, desc in checks:
            if not self.run_command(cmd, f"Checking {desc}"):
                all_good = False

        # Check for optimized files
        optimized_files = [
            "src/core/optimized_mcp_server.py",
            "src/core/enhanced_error_handling.py",
            "src/core/context_aware_processor.py",
            "config/claude_desktop_optimized.json",
            "tools/performance_monitor.py",
        ]

        for file_path in optimized_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                self.log_step(f"Missing optimized file: {file_path}", False)
                all_good = False
            else:
                self.log_step(f"Found optimized file: {file_path}")

        return all_good

    def setup_docker_environment(self, force_rebuild: bool = False) -> bool:
        """Setup Docker environment for Moodle"""
        print("🐳 Setting up Docker environment...")

        # Clean up existing containers if force rebuild
        if force_rebuild:
            self.run_command(
                "docker-compose -f operations/docker/docker-compose.fresh.yml down -v",
                "Removing existing containers",
            )

        # Start fresh containers
        compose_file = "operations/docker/docker-compose.fresh.yml"
        if not self.run_command(
            f"docker-compose -f {compose_file} up -d", "Starting Docker containers"
        ):
            return False

        # Wait for Moodle to be ready
        print("⏳ Waiting for Moodle to initialize...")
        max_attempts = 30
        for attempt in range(max_attempts):
            if self.run_command(
                "curl -s http://localhost:8080 > /dev/null",
                f"Checking Moodle readiness (attempt {attempt + 1})",
            ):
                self.log_step("Moodle is ready")
                return True
            time.sleep(10)

        self.log_step("Moodle failed to start within timeout", False)
        return False

    def setup_moodle_configuration(self) -> bool:
        """Setup Moodle with admin user and webservices"""
        print("👤 Setting up Moodle configuration...")

        config = self.master_config

        # Setup admin user
        admin_setup_script = f"""
        cd /var/www/html
        php admin/cli/install_database.php --agree-license --fullname="MoodleClaude Demo" --shortname="moodleclaude" --adminuser="{config.credentials.admin_user}" --adminpass="{config.credentials.admin_password}" --adminemail="{config.credentials.admin_email}"
        """

        if not self.run_command(
            f'docker exec moodle_app bash -c "{admin_setup_script}"',
            "Setting up Moodle admin user",
        ):
            return False

        # Enable webservices
        webservice_script = f"""
        cd /var/www/html
        php admin/cli/cfg.php --name=enablewebservices --set=1
        php admin/cli/cfg.php --name=webserviceprotocols --set=rest
        """

        if not self.run_command(
            f'docker exec moodle_app bash -c "{webservice_script}"',
            "Enabling Moodle webservices",
        ):
            return False

        return True

    def install_moodleclaude_plugin(self) -> bool:
        """Install MoodleClaude plugin"""
        print("🔌 Installing MoodleClaude plugin...")

        plugin_source = self.project_root / "moodle_plugin" / "local_moodleclaude"

        if not plugin_source.exists():
            self.log_step("MoodleClaude plugin source not found", False)
            return False

        # Copy plugin to Moodle
        copy_cmd = (
            f"docker cp {plugin_source} moodle_app:/var/www/html/local/moodleclaude"
        )
        if not self.run_command(copy_cmd, "Copying MoodleClaude plugin"):
            return False

        # Install plugin
        install_cmd = 'docker exec moodle_app bash -c "cd /var/www/html && php admin/cli/upgrade.php --non-interactive"'
        if not self.run_command(install_cmd, "Installing MoodleClaude plugin"):
            return False

        return True

    def create_webservice_users_and_tokens(self) -> Dict[str, str]:
        """Create webservice users and generate tokens"""
        print("🎫 Creating webservice users and generating tokens...")

        config = self.master_config
        tokens = {}

        # Create webservice user
        create_user_script = f"""
        cd /var/www/html
        php -r "
        require_once('config.php');
        require_once(\\$CFG->libdir . '/setup.php');

        // Create webservice user
        \\$user = new stdClass();
        \\$user->username = '{config.credentials.ws_user}';
        \\$user->password = '{config.credentials.ws_password}';
        \\$user->firstname = 'WebService';
        \\$user->lastname = 'User';
        \\$user->email = 'wsuser@moodleclaude.local';
        \\$user->confirmed = 1;
        \\$user->mnethostid = \\$CFG->mnet_localhost_id;

        if (!\\$DB->record_exists('user', array('username' => \\$user->username))) {{
            \\$user->id = user_create_user(\\$user, false, false);
            echo 'WebService user created with ID: ' . \\$user->id . PHP_EOL;
        }} else {{
            echo 'WebService user already exists' . PHP_EOL;
        }}
        "
        """

        self.run_command(
            f'docker exec moodle_app bash -c "{create_user_script}"',
            "Creating webservice user",
        )

        # Generate tokens
        token_script = f"""
        cd /var/www/html
        php -r "
        require_once('config.php');
        require_once(\\$CFG->libdir . '/setup.php');

        // Generate admin token
        \\$admin = \\$DB->get_record('user', array('username' => '{config.credentials.admin_user}'));
        if (\\$admin) {{
            \\$service = \\$DB->get_record('external_services', array('shortname' => 'moodle_mobile_app'));
            if (!\\$service) {{
                \\$service = new stdClass();
                \\$service->name = 'Moodle Mobile Web Service';
                \\$service->shortname = 'moodle_mobile_app';
                \\$service->enabled = 1;
                \\$service->restrictedusers = 0;
                \\$service->downloadfiles = 1;
                \\$service->uploadfiles = 1;
                \\$service->timecreated = time();
                \\$service->id = \\$DB->insert_record('external_services', \\$service);
            }}

            \\$token = external_generate_token(EXTERNAL_TOKEN_PERMANENT, \\$service, \\$admin->id);
            echo 'ADMIN_TOKEN:' . \\$token . PHP_EOL;
        }}

        // Generate webservice user token
        \\$wsuser = \\$DB->get_record('user', array('username' => '{config.credentials.ws_user}'));
        if (\\$wsuser) {{
            \\$token = external_generate_token(EXTERNAL_TOKEN_PERMANENT, \\$service, \\$wsuser->id);
            echo 'WSUSER_TOKEN:' . \\$token . PHP_EOL;
        }}
        "
        """

        result = subprocess.run(
            f'docker exec moodle_app bash -c "{token_script}"',
            shell=True,  # nosec B602 - admin setup script with controlled input
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if line.startswith("ADMIN_TOKEN:"):
                    tokens["admin"] = line.split(":", 1)[1].strip()
                elif line.startswith("WSUSER_TOKEN:"):
                    tokens["wsuser"] = line.split(":", 1)[1].strip()

        self.log_step(
            f"Generated tokens: Admin={bool(tokens.get('admin'))}, WSUser={bool(tokens.get('wsuser'))}"
        )
        return tokens

    def update_environment_with_tokens(self, tokens: Dict[str, str]) -> bool:
        """Update environment file with new tokens"""
        print("🔄 Updating environment configuration with new tokens...")

        try:
            env_file = self.project_root / ".env"

            # Read current .env
            env_content = ""
            if env_file.exists():
                with open(env_file, "r") as f:
                    env_content = f.read()

            # Update tokens
            if tokens.get("admin"):
                env_content = self._update_env_var(
                    env_content, "MOODLE_BASIC_TOKEN", tokens["admin"]
                )
                env_content = self._update_env_var(
                    env_content, "MOODLE_ADMIN_TOKEN", tokens["admin"]
                )

            if tokens.get("wsuser"):
                env_content = self._update_env_var(
                    env_content, "MOODLE_PLUGIN_TOKEN", tokens["wsuser"]
                )
                env_content = self._update_env_var(
                    env_content, "MOODLE_WSUSER_TOKEN", tokens["wsuser"]
                )

            # Write updated .env
            with open(env_file, "w") as f:
                f.write(env_content)

            self.log_step("Environment file updated with new tokens")
            return True

        except Exception as e:
            self.log_step(f"Failed to update environment file: {str(e)}", False)
            return False

    def _update_env_var(self, content: str, var_name: str, value: str) -> str:
        """Update or add environment variable in content"""
        lines = content.split("\n")
        updated = False

        for i, line in enumerate(lines):
            if line.startswith(f"{var_name}="):
                lines[i] = f"{var_name}={value}"
                updated = True
                break

        if not updated:
            lines.append(f"{var_name}={value}")

        return "\n".join(lines)

    def setup_optimized_claude_desktop_config(self) -> bool:
        """Setup optimized Claude Desktop configuration with current tokens"""
        print("🖥️ Setting up optimized Claude Desktop configuration...")

        try:
            # Load the optimized config template
            template_path = (
                self.project_root / "config" / "claude_desktop_optimized.json"
            )
            with open(template_path, "r") as f:
                config = json.load(f)

            # Get current tokens from .env
            env_file = self.project_root / ".env"
            tokens = {}
            if env_file.exists():
                with open(env_file, "r") as f:
                    for line in f:
                        if line.startswith("MOODLE_BASIC_TOKEN="):
                            tokens["basic"] = line.split("=", 1)[1].strip()
                        elif line.startswith("MOODLE_PLUGIN_TOKEN="):
                            tokens["plugin"] = line.split("=", 1)[1].strip()

            # Update config with current tokens and absolute paths
            for server_name, server_config in config.get("mcpServers", {}).items():
                # Update environment variables with actual tokens
                if "env" in server_config:
                    if tokens.get("basic"):
                        server_config["env"]["MOODLE_TOKEN_BASIC"] = tokens["basic"]
                    if tokens.get("plugin"):
                        server_config["env"]["MOODLE_TOKEN_ENHANCED"] = tokens["plugin"]

                # Make paths absolute
                if "args" in server_config and server_config["args"]:
                    relative_path = server_config["args"][0]
                    if not os.path.isabs(relative_path):
                        server_config["args"][0] = str(
                            self.project_root / relative_path
                        )

            # Get Claude Desktop config directory
            claude_config_dir = self._get_claude_config_directory()
            if not claude_config_dir:
                self.log_step(
                    "Could not determine Claude Desktop config directory", False
                )
                return False

            claude_config_file = claude_config_dir / "claude_desktop_config.json"

            # Backup existing config
            if claude_config_file.exists():
                backup_path = (
                    claude_config_dir
                    / f"claude_desktop_config.json.backup.{int(time.time())}"
                )
                shutil.copy2(claude_config_file, backup_path)
                self.log_step(f"Backed up existing config to {backup_path}")

            # Write optimized config
            with open(claude_config_file, "w") as f:
                json.dump(config, f, indent=2)

            self.log_step(f"Claude Desktop config updated: {claude_config_file}")
            return True

        except Exception as e:
            self.log_step(f"Failed to setup Claude Desktop config: {str(e)}", False)
            return False

    def _get_claude_config_directory(self) -> Optional[Path]:
        """Get Claude Desktop configuration directory"""
        system = os.name

        if system == "nt":  # Windows
            config_dir = Path.home() / "AppData" / "Roaming" / "Claude"
        elif system == "posix":  # macOS/Linux
            if sys.platform == "darwin":  # macOS
                config_dir = Path.home() / "Library" / "Application Support" / "Claude"
            else:  # Linux
                config_dir = Path.home() / ".config" / "Claude"
        else:
            return None

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def run_system_validation(self) -> bool:
        """Run comprehensive system validation"""
        print("🧪 Running system validation...")

        try:
            # Import and run the optimization setup validation
            sys.path.append(str(self.project_root / "tools"))
            from setup_optimized_system import OptimizedSystemSetup

            optimizer = OptimizedSystemSetup(str(self.project_root))
            validation_results = optimizer.validate_optimizations()

            overall_score = validation_results.get("overall_score", 0)
            self.log_step(f"System validation score: {overall_score:.1f}%")

            if overall_score >= 80:
                self.log_step("System validation passed")
                return True
            else:
                self.log_step("System validation failed - check components", False)
                return False

        except Exception as e:
            self.log_step(f"Validation failed: {str(e)}", False)
            return False

    def create_backup(self) -> bool:
        """Create system backup after successful setup"""
        print("💾 Creating system backup...")

        backup_name = f"optimized_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_script = f"""
        cd operations/backup
        python create_backup.py --name {backup_name} --include-tokens
        """

        return self.run_command(backup_script, "Creating system backup")

    def print_setup_summary(self, success: bool):
        """Print setup summary"""
        print("\n" + "=" * 60)
        print("🚀 MOODLECLAUDE OPTIMIZED SETUP SUMMARY")
        print("=" * 60)

        if success:
            print("✅ Setup completed successfully!")
            print(f"📊 Total steps: {len(self.setup_log)}")
            successful_steps = len([s for s in self.setup_log if s["success"]])
            print(f"✅ Successful: {successful_steps}")
            print(f"❌ Failed: {len(self.setup_log) - successful_steps}")
        else:
            print("❌ Setup completed with errors!")

        print("\n🎯 NEXT STEPS:")
        print("1. 🔄 Restart Claude Desktop to load optimized configuration")
        print("2. 🧪 Test with: 'Create a Python programming course'")
        print(
            "3. 📊 Monitor performance: python tools/performance_monitor.py --metrics"
        )
        print("4. 🔍 Health check: python tools/performance_monitor.py --health-check")

        print("\n🌐 ACCESS POINTS:")
        print("• Moodle: http://localhost:8080")
        print("• Admin: admin / MoodleClaude2025!")
        print("• WSUser: wsuser / MoodleClaudeWS2025!")
        print("• PgAdmin: http://localhost:8082")

        print("\n🛠️ OPTIMIZATION FEATURES ACTIVE:")
        print("• ⚡ Connection Pooling (10 max connections)")
        print("• 💾 LRU Caching (100 entries)")
        print("• 🚦 Rate Limiting (50 calls/60s)")
        print("• 🌊 Streaming Responses")
        print("• 🧠 Context-Aware Processing")
        print("• 📊 Performance Monitoring")
        print("• 🛡️ Enhanced Error Handling")

        if not success:
            print("\n🔍 TROUBLESHOOTING:")
            failed_steps = [s for s in self.setup_log if not s["success"]]
            for step in failed_steps[-3:]:  # Last 3 failures
                print(f"• {step['message']}")

        print("=" * 60)

    def run_full_setup(
        self, skip_docker: bool = False, force_rebuild: bool = False
    ) -> bool:
        """Run complete optimized setup"""
        print("🚀 Starting MoodleClaude Optimized Setup v3.0...")

        # Check prerequisites
        if not self.check_prerequisites():
            self.log_step("Prerequisites check failed", False)
            return False

        success = True

        # Docker setup
        if not skip_docker:
            if not self.setup_docker_environment(force_rebuild):
                success = False

            if success and not self.setup_moodle_configuration():
                success = False

            if success and not self.install_moodleclaude_plugin():
                success = False

        # Generate tokens
        tokens = {}
        if success:
            tokens = self.create_webservice_users_and_tokens()
            if not tokens:
                self.log_step("Token generation failed", False)
                success = False

        # Update environment
        if success and tokens:
            if not self.update_environment_with_tokens(tokens):
                success = False

        # Setup Claude Desktop config
        if success:
            if not self.setup_optimized_claude_desktop_config():
                success = False

        # Sync all configurations
        if success:
            try:
                sync_all_configurations()
                self.log_step("All configurations synchronized")
            except Exception as e:
                self.log_step(f"Configuration sync failed: {str(e)}", False)
                success = False

        # System validation
        if success:
            if not self.run_system_validation():
                success = False

        # Create backup
        if success:
            self.create_backup()

        # Print summary
        self.print_setup_summary(success)

        return success


def main():
    parser = argparse.ArgumentParser(description="MoodleClaude Optimized Setup v3.0")
    parser.add_argument(
        "--quick-setup",
        action="store_true",
        help="Run quick setup with minimal prompts",
    )
    parser.add_argument(
        "--skip-docker",
        action="store_true",
        help="Skip Docker setup (use existing containers)",
    )
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Force rebuild of Docker containers",
    )
    parser.add_argument(
        "--setup-only-claude-config",
        action="store_true",
        help="Only setup Claude Desktop configuration",
    )

    args = parser.parse_args()

    setup = OptimizedMoodleSetup()

    if args.setup_only_claude_config:
        # Only setup Claude Desktop config
        print("🖥️ Setting up Claude Desktop configuration only...")
        success = setup.setup_optimized_claude_desktop_config()
        if success:
            print("✅ Claude Desktop configuration updated successfully!")
            print("🔄 Please restart Claude Desktop to load the new configuration.")
        else:
            print("❌ Failed to update Claude Desktop configuration.")
        return

    # Run full setup
    success = setup.run_full_setup(
        skip_docker=args.skip_docker, force_rebuild=args.force_rebuild
    )

    if success:
        print("\n🎉 MoodleClaude Optimized Setup completed successfully!")
    else:
        print("\n⚠️ Setup completed with issues. Check the log above for details.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Setup failed with exception: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Update Existing Setup with Bug Fixes
===================================
Updates existing MoodleClaude installations with the discovered bug fixes.

Fixes applied:
- MCP Server 'Server disconnected' error (spawn python ENOENT)
- Access control exception for course creation
- Token permissions and web service configuration
- Claude Desktop integration improvements

Usage:
    python tools/update_existing_setup.py
    python tools/update_existing_setup.py --claude-config-only
    python tools/update_existing_setup.py --moodle-permissions-only
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
CLAUDE_CONFIG_PATH = (
    Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
)


class SetupUpdater:
    """Updates existing MoodleClaude setup with bug fixes"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.config = {}
        self.load_config()

    def load_config(self):
        """Load configuration from token file"""
        config_file = self.project_root / "config" / "moodle_tokens.env"

        if config_file.exists():
            with open(config_file, "r") as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        key, value = line.strip().split("=", 1)
                        self.config[key] = value.strip("\"'")

        # Set defaults
        self.config.setdefault("MOODLE_URL", "http://localhost:8080")
        self.config.setdefault("MOODLE_ADMIN_USER", "admin")

    def get_python_path(self) -> str:
        """Get the correct Python path for MCP server"""
        # Check virtual environment first
        venv_python = self.project_root / ".venv" / "bin" / "python3"
        if venv_python.exists():
            return str(venv_python)

        # Check system Python
        try:
            result = subprocess.run(
                ["which", "python3"], capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass

        # Fallback
        return "python3"

    def update_claude_desktop_config(self) -> bool:
        """Update Claude Desktop configuration with bug fixes"""
        print("🖥️  Updating Claude Desktop configuration...")

        # Get correct Python path (fixes spawn python ENOENT)
        python_path = self.get_python_path()
        print(f"   Using Python path: {python_path}")

        # Get tokens from config
        basic_token = self.config.get(
            "MOODLE_BASIC_TOKEN", self.config.get("MOODLE_ADMIN_TOKEN", "")
        )
        enhanced_token = basic_token  # Use the same token with permissions

        # Create updated Claude Desktop config
        claude_config = {
            "mcpServers": {
                "moodleclaude-stable": {
                    "command": python_path,  # Fixed: Use absolute Python path
                    "args": [str(self.project_root / "src/core/working_mcp_server.py")],
                    "env": {
                        "MOODLE_URL": self.config.get(
                            "MOODLE_URL", "http://localhost:8080"
                        ),
                        "MOODLE_TOKEN_BASIC": basic_token,
                        "MOODLE_TOKEN_ENHANCED": enhanced_token,  # Use same token
                        "MOODLE_USERNAME": self.config.get(
                            "MOODLE_ADMIN_USER", "admin"
                        ),
                        "SERVER_NAME": "stable-moodle-mcp",
                        "LOG_LEVEL": "INFO",
                    },
                    "timeout": 30,
                    "autoApprove": ["test_connection", "get_courses", "create_course"],
                    "disabled": False,
                    "description": "Stable MoodleClaude MCP Server with bug fixes",
                    "version": "1.0.0",
                }
            },
            "globalSettings": {
                "logging": {
                    "level": "INFO",
                    "enableFileLogging": True,
                    "logDirectory": str(self.project_root / "logs"),
                }
            },
        }

        # Ensure Claude config directory exists
        CLAUDE_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Backup existing config if it exists
        if CLAUDE_CONFIG_PATH.exists():
            backup_path = CLAUDE_CONFIG_PATH.with_suffix(
                f".backup.{int(datetime.now().timestamp())}"
            )
            CLAUDE_CONFIG_PATH.rename(backup_path)
            print(f"   Backed up existing config to: {backup_path.name}")

        # Write updated Claude Desktop config
        try:
            with open(CLAUDE_CONFIG_PATH, "w") as f:
                json.dump(claude_config, f, indent=2)

            print(f"✅ Claude Desktop config updated: {CLAUDE_CONFIG_PATH}")
            return True

        except Exception as e:
            print(f"❌ Failed to update Claude Desktop config: {str(e)}")
            return False

    def run_moodle_permissions_fix(self) -> bool:
        """Run the Moodle permissions fix for existing installation"""
        print("🔐 Applying Moodle permissions fixes...")

        # Check if containers are running
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=moodleclaude_app_fresh",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0 or "moodleclaude_app_fresh" not in result.stdout:
                print("❌ Moodle container not found or not running")
                print("   Please start your Moodle Docker containers first")
                return False

        except Exception as e:
            print(f"❌ Error checking Docker containers: {e}")
            return False

        # Run the comprehensive permissions fix script
        try:
            setup_script_path = self.project_root / "setup_moodleclaude_v3_fixed.py"
            if not setup_script_path.exists():
                print(f"❌ Setup script not found: {setup_script_path}")
                return False

            # Run permissions fix only
            result = subprocess.run(
                ["python3", str(setup_script_path), "--fix-permissions-only"],
                cwd=self.project_root,
            )

            return result.returncode == 0

        except Exception as e:
            print(f"❌ Error running permissions fix: {e}")
            return False

    def validate_fixes(self) -> Dict[str, bool]:
        """Validate that the fixes are working"""
        print("🔍 Validating applied fixes...")

        validation_results = {}

        # Check Claude Desktop config
        validation_results["claude_config_exists"] = CLAUDE_CONFIG_PATH.exists()

        if CLAUDE_CONFIG_PATH.exists():
            try:
                with open(CLAUDE_CONFIG_PATH, "r") as f:
                    config = json.load(f)

                # Check if Python path is absolute
                command = (
                    config.get("mcpServers", {})
                    .get("moodleclaude-stable", {})
                    .get("command", "")
                )
                validation_results["python_path_absolute"] = os.path.isabs(command)

                # Check if Python executable exists
                validation_results["python_executable_exists"] = (
                    Path(command).exists() if command else False
                )

            except Exception:
                validation_results["claude_config_valid"] = False

        # Check if MCP server file exists
        mcp_server_path = self.project_root / "src/core/working_mcp_server.py"
        validation_results["mcp_server_exists"] = mcp_server_path.exists()

        # Check if Moodle is accessible
        try:
            import requests

            response = requests.get(
                self.config.get("MOODLE_URL", "http://localhost:8080"), timeout=5
            )
            validation_results["moodle_accessible"] = response.status_code < 400
        except:
            validation_results["moodle_accessible"] = False

        # Display results
        print("\n📋 Validation Results:")
        for check_name, passed in validation_results.items():
            emoji = "✅" if passed else "❌"
            display_name = check_name.replace("_", " ").title()
            print(f"  {emoji} {display_name}")

        return validation_results

    def generate_update_report(self, applied_fixes: Dict[str, bool]):
        """Generate update report"""
        report = {
            "update_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "python_path": self.get_python_path(),
            "claude_config_path": str(CLAUDE_CONFIG_PATH),
            "applied_fixes": applied_fixes,
            "validation_results": self.validate_fixes(),
            "config_summary": {
                "moodle_url": self.config.get("MOODLE_URL"),
                "tokens_available": bool(self.config.get("MOODLE_BASIC_TOKEN")),
            },
        }

        # Save report
        report_file = self.project_root / "setup_update_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 Update report saved to: {report_file}")
        return report

    def run_update(
        self, claude_config_only: bool = False, moodle_permissions_only: bool = False
    ) -> bool:
        """Run the setup update process"""
        print("🔄 Updating MoodleClaude Setup with Bug Fixes")
        print("=" * 60)

        applied_fixes = {}
        success = True

        if claude_config_only:
            print("🖥️  Updating Claude Desktop configuration only...")
            applied_fixes["claude_config"] = self.update_claude_desktop_config()
            success = applied_fixes["claude_config"]

        elif moodle_permissions_only:
            print("🔐 Applying Moodle permissions fixes only...")
            applied_fixes["moodle_permissions"] = self.run_moodle_permissions_fix()
            success = applied_fixes["moodle_permissions"]

        else:
            # Full update
            print("🔄 Applying all bug fixes...")

            # Update Claude Desktop config
            applied_fixes["claude_config"] = self.update_claude_desktop_config()

            # Apply Moodle permissions fixes
            applied_fixes["moodle_permissions"] = self.run_moodle_permissions_fix()

            success = all(applied_fixes.values())

        # Generate report
        self.generate_update_report(applied_fixes)

        if success:
            print("\n🎉 Setup update completed successfully!")
            print("=" * 50)
            print("✅ Bug fixes applied successfully")
            if "claude_config" in applied_fixes and applied_fixes["claude_config"]:
                print("✅ Claude Desktop configuration updated")
                print("🔄 Please restart Claude Desktop to load the changes")
            if (
                "moodle_permissions" in applied_fixes
                and applied_fixes["moodle_permissions"]
            ):
                print("✅ Moodle permissions fixed")
                print("✅ Course creation should now work")
        else:
            print("\n❌ Setup update completed with errors!")
            print("📋 Check the update report for details")

        return success


def main():
    """Main update function"""
    parser = argparse.ArgumentParser(
        description="Update MoodleClaude Setup with Bug Fixes"
    )
    parser.add_argument(
        "--claude-config-only",
        action="store_true",
        help="Update only the Claude Desktop configuration",
    )
    parser.add_argument(
        "--moodle-permissions-only",
        action="store_true",
        help="Apply only the Moodle permissions fixes",
    )

    args = parser.parse_args()

    updater = SetupUpdater()
    success = updater.run_update(
        claude_config_only=args.claude_config_only,
        moodle_permissions_only=args.moodle_permissions_only,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

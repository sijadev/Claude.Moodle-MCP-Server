#!/usr/bin/env python3
"""
Validate Claude Desktop configuration JSON file
"""

import json
import os
import sys


def validate_claude_config():
    """Validate the Claude Desktop configuration file"""

    # Common config file locations
    config_paths = [
        os.path.expanduser(
            "~/Library/Application Support/Claude/claude_desktop_config.json"
        ),  # macOS
        os.path.expanduser("~/.config/claude/claude_desktop_config.json"),  # Linux
        os.path.expanduser("%APPDATA%/Claude/claude_desktop_config.json"),  # Windows
    ]

    config_file = None
    for path in config_paths:
        if os.path.exists(path):
            config_file = path
            break

    if not config_file:
        print("❌ Claude Desktop config file not found in common locations:")
        for path in config_paths:
            print(f"   - {path}")
        return False

    print(f"🔍 Validating: {config_file}")

    try:
        with open(config_file, "r") as f:
            config = json.load(f)

        print("✅ JSON syntax is valid")

        # Check MoodleClaude configuration
        if "mcpServers" in config:
            servers = config["mcpServers"]
            print(f"📊 Found {len(servers)} MCP servers")

            if "moodle-course-creator" in servers:
                moodle_config = servers["moodle-course-creator"]
                print("✅ MoodleClaude server configuration found")

                # Check required fields
                required_fields = ["command", "args", "cwd", "env"]
                for field in required_fields:
                    if field in moodle_config:
                        print(
                            f"   ✅ {field}: {moodle_config[field] if field != 'env' else '[configured]'}"
                        )
                    else:
                        print(f"   ❌ Missing: {field}")

                # Check environment variables
                if "env" in moodle_config:
                    env = moodle_config["env"]
                    required_env = [
                        "MOODLE_URL",
                        "MOODLE_BASIC_TOKEN",
                        "MOODLE_PLUGIN_TOKEN",
                        "MOODLE_USERNAME",
                    ]

                    print("   🔧 Environment variables:")
                    for var in required_env:
                        if var in env:
                            value = env[var]
                            if "TOKEN" in var:
                                print(
                                    f"      ✅ {var}: ...{value[-8:] if len(value) > 8 else 'set'}"
                                )
                            else:
                                print(f"      ✅ {var}: {value}")
                        else:
                            print(f"      ❌ Missing: {var}")

            else:
                print("❌ MoodleClaude server configuration not found")
                print("   Available servers:", list(servers.keys()))

        return True

    except json.JSONDecodeError as e:
        print(f"❌ JSON syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading config file: {e}")
        return False


if __name__ == "__main__":
    print("🔍 Claude Desktop Configuration Validator")
    print("=" * 50)

    if validate_claude_config():
        print("\n🎯 Configuration validation complete!")
    else:
        print("\n❌ Configuration validation failed!")
        sys.exit(1)

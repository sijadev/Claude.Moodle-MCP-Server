#!/usr/bin/env python3
"""
Claude Desktop Diagnose Tool
============================

Umfassende Diagnose der Claude Desktop Konfiguration und MCP Server Status.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path


def get_claude_config_path():
    """Get Claude Desktop config path."""
    return (
        Path.home()
        / "Library"
        / "Application Support"
        / "Claude"
        / "claude_desktop_config.json"
    )


def get_claude_log_path():
    """Get Claude Desktop log path."""
    return Path.home() / "Library" / "Logs" / "Claude" / "main.log"


def read_config():
    """Read and validate Claude Desktop config."""
    config_path = get_claude_config_path()

    print(f"📋 Reading config from: {config_path}")

    if not config_path.exists():
        print("❌ Claude Desktop config file not found!")
        return None

    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        print("✅ Config file loaded successfully")
        return config
    except Exception as e:
        print(f"❌ Failed to read config: {e}")
        return None


def validate_mcp_servers(config):
    """Validate MCP servers configuration."""
    print("\n🔧 Validating MCP Servers:")

    if not config or "mcpServers" not in config:
        print("❌ No mcpServers section found")
        return False

    servers = config["mcpServers"]
    if not servers:
        print("❌ No MCP servers configured")
        return False

    print(f"✅ Found {len(servers)} MCP server(s) configured")

    all_valid = True
    for server_name, server_config in servers.items():
        print(f"\n  📡 Server: {server_name}")
        print(
            f"     Status: {'🟢 Enabled' if not server_config.get('disabled', False) else '🔴 Disabled'}"
        )

        # Check command and args
        command = server_config.get("command", "")
        args = server_config.get("args", [])

        if not command:
            print(f"     ❌ No command specified")
            all_valid = False
            continue

        if not args:
            print(f"     ❌ No args specified")
            all_valid = False
            continue

        script_path = Path(args[0]) if args else None
        if script_path and script_path.exists():
            print(f"     ✅ Script exists: {script_path}")
        else:
            print(f"     ❌ Script not found: {script_path}")
            all_valid = False

        # Check environment variables
        env_vars = server_config.get("env", {})
        print(f"     📝 Environment variables: {len(env_vars)}")

        for key, value in env_vars.items():
            if "TOKEN" in key:
                status = "✅ Set" if value else "❌ Empty"
                print(f"       - {key}: {status}")
            elif key in ["MOODLE_URL", "SERVER_NAME"]:
                print(f"       - {key}: {value}")

    return all_valid


def test_mcp_server_startup():
    """Test if MCP server can start."""
    print("\n🚀 Testing MCP Server Startup:")

    config = read_config()
    if not config or "mcpServers" not in config:
        print("❌ No valid config to test")
        return False

    servers = config["mcpServers"]

    for server_name, server_config in servers.items():
        if server_config.get("disabled", False):
            print(f"  ⏭️  Skipping disabled server: {server_name}")
            continue

        print(f"  🧪 Testing server: {server_name}")

        command = server_config.get("command", "")
        args = server_config.get("args", [])
        env_vars = server_config.get("env", {})

        if not command or not args:
            print(f"     ❌ Invalid configuration")
            continue

        # Set up environment
        test_env = os.environ.copy()
        test_env.update(env_vars)

        try:
            # Try to start the server with a short timeout
            process = subprocess.Popen(
                [command] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=test_env,
                text=True,
            )

            # Wait a bit for startup
            time.sleep(2)

            if process.poll() is None:
                # Process is still running - good sign
                print(f"     ✅ Server started successfully")
                process.terminate()
                process.wait(timeout=5)
                return True
            else:
                # Process exited
                stdout, stderr = process.communicate()
                print(f"     ❌ Server exited: {stderr[:200]}...")
                return False

        except Exception as e:
            print(f"     ❌ Failed to start server: {e}")
            return False

    return False


def check_recent_logs():
    """Check recent Claude Desktop logs for errors."""
    print("\n📜 Checking Recent Logs:")

    log_path = get_claude_log_path()

    if not log_path.exists():
        print(f"❌ Log file not found: {log_path}")
        return

    try:
        with open(log_path, "r") as f:
            lines = f.readlines()

        # Get last 50 lines
        recent_lines = lines[-50:]

        # Look for relevant messages
        warnings = []
        errors = []
        mcp_messages = []

        for line in recent_lines:
            line_lower = line.lower()
            if "mcp" in line_lower or "moodleclaude" in line_lower:
                mcp_messages.append(line.strip())
            elif "[warn]" in line:
                warnings.append(line.strip())
            elif "[error]" in line:
                errors.append(line.strip())

        print(f"📊 Log Analysis (last 50 lines):")
        print(f"   - MCP-related messages: {len(mcp_messages)}")
        print(f"   - Warnings: {len(warnings)}")
        print(f"   - Errors: {len(errors)}")

        if mcp_messages:
            print(f"\n🔍 Recent MCP Messages:")
            for msg in mcp_messages[-5:]:  # Show last 5
                print(f"   {msg}")

        if warnings:
            print(f"\n⚠️  Recent Warnings:")
            for warning in warnings[-3:]:  # Show last 3
                print(f"   {warning}")

        if errors:
            print(f"\n❌ Recent Errors:")
            for error in errors[-3:]:  # Show last 3
                print(f"   {error}")

    except Exception as e:
        print(f"❌ Failed to read logs: {e}")


def check_mcp_functionality():
    """Check if MCP functionality is working."""
    print("\n🔌 Checking MCP Integration:")

    # This is just informational since we can't directly test Claude Desktop integration
    print("  ℹ️  To test MCP integration:")
    print("     1. Restart Claude Desktop after configuration changes")
    print("     2. In Claude Desktop, try using MCP tools like:")
    print("        - 'test_connection' - Test Moodle connection")
    print("        - 'get_courses' - List available courses")
    print("     3. Check if tools appear in Claude's interface")
    print("     4. Monitor logs for connection attempts")


def main():
    """Main diagnostic function."""
    print("🏥 Claude Desktop Diagnostic Tool")
    print("=" * 50)

    # Read and validate config
    config = read_config()
    if not config:
        print("\n❌ Cannot proceed without valid configuration")
        return False

    # Validate MCP servers
    servers_valid = validate_mcp_servers(config)

    # Test server startup
    startup_success = test_mcp_server_startup()

    # Check logs
    check_recent_logs()

    # MCP functionality check
    check_mcp_functionality()

    # Summary
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSTIC SUMMARY")
    print("=" * 50)

    print(f"Configuration Valid: {'✅' if config else '❌'}")
    print(f"MCP Servers Valid: {'✅' if servers_valid else '❌'}")
    print(f"Server Startup Test: {'✅' if startup_success else '❌'}")

    if config and servers_valid and startup_success:
        print("\n✅ Overall Status: HEALTHY")
        print("   Your MCP servers should work with Claude Desktop.")
        print(
            "   The warnings about 'extensions not found' are normal and not critical."
        )
    else:
        print("\n⚠️  Overall Status: NEEDS ATTENTION")
        print("   Some issues were found that may affect MCP functionality.")

    print(f"\n📋 Next Steps:")
    print(f"   1. Restart Claude Desktop if you made config changes")
    print(f"   2. Test MCP tools within Claude Desktop interface")
    print(f"   3. Monitor logs at: {get_claude_log_path()}")

    return config and servers_valid and startup_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

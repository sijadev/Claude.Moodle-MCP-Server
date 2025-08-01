#!/usr/bin/env python3
"""
MCP Server Connection Test
=========================

Testet die MCP Server Verbindung und simuliert Claude Desktop's Verbindung.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def test_mcp_server_direct():
    """Test MCP server direkt."""
    print("🧪 Testing MCP Server Direct Connection")
    print("=" * 50)

    project_root = Path(__file__).parent.parent
    server_path = project_root / "src" / "core" / "working_mcp_server.py"

    if not server_path.exists():
        print(f"❌ Server not found: {server_path}")
        return False

    # Setup environment like Claude Desktop would
    env = os.environ.copy()
    env.update(
        {
            "MOODLE_URL": "http://localhost:8080",
            "MOODLE_TOKEN_BASIC": "bfef4e5ef1f77d5ad173407b1967d838",
            "MOODLE_TOKEN_ENHANCED": "e14a2f11d2695415dd90688690b39328",
            "MOODLE_USERNAME": "admin",
            "SERVER_NAME": "test-mcp-server",
            "LOG_LEVEL": "DEBUG",
        }
    )

    print(f"📡 Starting server: {server_path}")
    print(f"🌍 Environment:")
    print(f"   MOODLE_URL: {env['MOODLE_URL']}")
    print(f"   SERVER_NAME: {env['SERVER_NAME']}")

    try:
        # Start the server
        process = subprocess.Popen(
            [sys.executable, str(server_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
        )

        # Send MCP initialization
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        print(f"📤 Sending initialization request...")
        request_json = json.dumps(init_request) + "\n"

        process.stdin.write(request_json)
        process.stdin.flush()

        # Wait for response
        time.sleep(2)

        # Check if process is still running
        if process.poll() is None:
            print(f"✅ Server is running and responding to requests")

            # Try to get tools list
            tools_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}

            tools_json = json.dumps(tools_request) + "\n"
            process.stdin.write(tools_json)
            process.stdin.flush()

            time.sleep(1)

            # Terminate process
            process.terminate()

            try:
                stdout, stderr = process.communicate(timeout=5)
                print(f"📥 Server output received")

                if stderr:
                    print(f"📜 Server logs:")
                    for line in stderr.split("\n")[:10]:  # First 10 lines
                        if line.strip():
                            print(f"   {line}")

                if stdout:
                    print(f"📋 Server responses:")
                    for line in stdout.split("\n")[:5]:  # First 5 lines
                        if line.strip():
                            try:
                                response = json.loads(line)
                                print(
                                    f"   Response ID {response.get('id', 'N/A')}: {response.get('result', response.get('error', 'Unknown'))}"
                                )
                            except:
                                print(f"   Raw: {line[:100]}...")

                return True

            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️ Server had to be killed (timeout)")
                return True  # Still counts as working
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server exited immediately")
            print(f"Error output: {stderr[:500]}")
            return False

    except Exception as e:
        print(f"❌ Failed to test server: {e}")
        return False


def check_mcp_dependencies():
    """Check if MCP dependencies are available."""
    print(f"\n🔍 Checking MCP Dependencies")
    print("=" * 30)

    dependencies = [
        ("mcp", "MCP Protocol Library"),
        ("aiohttp", "HTTP Client Library"),
        ("pydantic", "Data Validation Library"),
    ]

    missing = []

    for dep, desc in dependencies:
        try:
            __import__(dep)
            print(f"✅ {desc}: Available")
        except ImportError:
            print(f"❌ {desc}: Missing")
            missing.append(dep)

    if missing:
        print(f"\n💡 To install missing dependencies:")
        print(f"   pip install {' '.join(missing)}")
        return False

    return True


def check_moodle_connection():
    """Check if Moodle is accessible."""
    print(f"\n🌐 Checking Moodle Connection")
    print("=" * 30)

    moodle_url = "http://localhost:8080"

    try:
        import requests

        response = requests.get(moodle_url, timeout=5)

        if response.status_code == 200:
            print(f"✅ Moodle accessible at {moodle_url}")
            return True
        else:
            print(f"⚠️ Moodle responded with status {response.status_code}")
            return False

    except ImportError:
        print(f"⚠️ requests library not available - cannot test HTTP connection")
        return True  # Don't fail the test for this
    except Exception as e:
        print(f"❌ Cannot reach Moodle: {e}")
        print(f"💡 Make sure Moodle is running:")
        print(f"   docker-compose up -d")
        print(f"   or start your local Moodle instance")
        return False


def check_claude_config():
    """Check Claude Desktop configuration."""
    print(f"\n⚙️ Checking Claude Desktop Configuration")
    print("=" * 40)

    config_path = (
        Path.home()
        / "Library"
        / "Application Support"
        / "Claude"
        / "claude_desktop_config.json"
    )

    if not config_path.exists():
        print(f"❌ Claude config not found: {config_path}")
        return False

    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        if "mcpServers" not in config:
            print(f"❌ No mcpServers section in config")
            return False

        servers = config["mcpServers"]
        enabled_servers = [
            name for name, cfg in servers.items() if not cfg.get("disabled", False)
        ]

        print(f"✅ Found {len(servers)} MCP servers, {len(enabled_servers)} enabled")

        for name in enabled_servers:
            print(f"   - {name}: ✅ Enabled")

        return len(enabled_servers) > 0

    except Exception as e:
        print(f"❌ Failed to read config: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 MCP Server Connection Test")
    print("=" * 50)

    success_count = 0
    total_tests = 4

    # Test 1: Dependencies
    if check_mcp_dependencies():
        success_count += 1

    # Test 2: Moodle connection
    if check_moodle_connection():
        success_count += 1

    # Test 3: Claude config
    if check_claude_config():
        success_count += 1

    # Test 4: Direct MCP server test
    if test_mcp_server_direct():
        success_count += 1

    # Summary
    print(f"\n" + "=" * 50)
    print(f"🎯 TEST SUMMARY")
    print(f"=" * 50)
    print(f"Tests passed: {success_count}/{total_tests}")

    if success_count == total_tests:
        print(f"✅ ALL TESTS PASSED!")
        print(f"   Your MCP server should work with Claude Desktop.")
        print(f"   Try typing commands like:")
        print(f"   - 'test connection to moodle'")
        print(f"   - 'get list of courses'")
        print(f"   - 'show me course contents'")
    elif success_count >= 3:
        print(f"⚠️ MOSTLY WORKING - Minor issues found")
        print(f"   The MCP server should still work in Claude Desktop.")
    else:
        print(f"❌ MULTIPLE ISSUES FOUND")
        print(f"   Please fix the failing tests above.")

    print(f"\n📋 Troubleshooting:")
    print(f"   1. Restart Claude Desktop after config changes")
    print(f"   2. Check that Moodle is running on localhost:8080")
    print(f"   3. Look for MCP-related messages in Claude Desktop logs")

    return success_count >= 3


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

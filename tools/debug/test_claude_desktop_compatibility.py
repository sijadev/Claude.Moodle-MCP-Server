#!/usr/bin/env python3
"""
Test Claude Desktop MCP server compatibility
"""

import asyncio
import json
import subprocess
import sys
import time


async def test_mcp_server_output():
    """Test that MCP server produces only valid JSON on stdout"""

    print("🔍 Testing Claude Desktop MCP Server Compatibility")
    print("=" * 60)

    # Start the MCP server
    startup_script = "tools/setup/start_mcp_server.py"

    print(f"📋 Starting MCP server: {startup_script}")

    try:
        # Use subprocess to capture stdout and stderr separately
        process = subprocess.Popen(
            [sys.executable, startup_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        print("⏳ Waiting for server initialization...")
        time.sleep(3)

        # Check if process is still running
        if process.poll() is not None:
            # Process has terminated
            stdout, stderr = process.communicate()
            print(f"❌ MCP server terminated early")
            print(f"📋 STDOUT (should be empty or valid JSON):")
            print(repr(stdout))
            print(f"📋 STDERR (logs and errors):")
            print(stderr)
            return False

        # Try to read some output
        print("📊 Testing JSON output from stdout...")

        # Send a simple JSON-RPC message to test the server
        init_message = {
            "jsonrpc": "2.0",
            "id": "test",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        # Write the message to stdin
        message_str = json.dumps(init_message) + "\n"
        process.stdin.write(message_str.encode())
        process.stdin.flush()

        # Try to read response
        time.sleep(1)

        # Terminate the process cleanly
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)

        print("✅ MCP server started and terminated cleanly")
        print(f"📋 STDOUT length: {len(stdout)} characters")
        print(f"📋 STDERR length: {len(stderr)} characters")

        # Check stdout for any non-JSON content
        if stdout.strip():
            lines = stdout.strip().split("\n")
            json_lines = 0
            invalid_lines = []

            for i, line in enumerate(lines):
                if line.strip():
                    try:
                        json.loads(line.strip())
                        json_lines += 1
                    except json.JSONDecodeError:
                        invalid_lines.append(f"Line {i+1}: {repr(line)}")

            if invalid_lines:
                print(f"❌ Found {len(invalid_lines)} invalid JSON lines in stdout:")
                for invalid_line in invalid_lines[:5]:  # Show first 5
                    print(f"   {invalid_line}")
                return False
            else:
                print(f"✅ All {json_lines} stdout lines are valid JSON")
        else:
            print(
                "📋 No stdout output (this is normal for MCP servers waiting for input)"
            )

        # Check stderr for expected log messages
        if stderr:
            print("📋 STDERR contains expected log messages:")
            stderr_lines = stderr.split("\n")[:5]  # Show first 5 lines
            for line in stderr_lines:
                if line.strip():
                    print(f"   {line}")

        return True

    except subprocess.TimeoutExpired:
        print("❌ MCP server process timed out")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False


async def main():
    """Main test function"""
    success = await test_mcp_server_output()

    print("\n" + "=" * 60)
    if success:
        print("✅ Claude Desktop Compatibility: PASSED")
        print("🎯 The MCP server should work correctly with Claude Desktop")
    else:
        print("❌ Claude Desktop Compatibility: FAILED")
        print("🔧 Fix required: Ensure only JSON goes to stdout")

    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)

#!/usr/bin/env python3
"""
Comprehensive validation script to check MCP server, logs, and Moodle data
"""

import asyncio
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv


def check_claude_desktop_logs():
    """Check Claude Desktop MCP logs"""
    print("🔍 Checking Claude Desktop Logs")
    print("=" * 50)

    log_base = Path.home() / "Library" / "Application Support" / "Code" / "logs"

    if not log_base.exists():
        print("❌ Claude Desktop log directory not found")
        return

    # Find recent log directories
    recent_dirs = sorted(
        [d for d in log_base.iterdir() if d.is_dir()],
        key=lambda x: x.name,
        reverse=True,
    )[:5]

    print(f"📁 Found {len(recent_dirs)} recent log sessions")

    for log_dir in recent_dirs:
        mcp_log = (
            log_dir
            / "window1"
            / "mcpServer.claude-desktop.null.moodle-course-creator.log"
        )
        if mcp_log.exists():
            size = mcp_log.stat().st_size
            print(f"   📝 {log_dir.name}: {size} bytes")

            if size > 0:
                print(f"      Content preview:")
                with open(mcp_log, "r") as f:
                    content = f.read()
                    print(f"      {content[:200]}{'...' if len(content) > 200 else ''}")
            else:
                print(f"      ⚠️  Log file is empty")


def check_mcp_server_logs():
    """Check local MCP server logs"""
    print("\n🔍 Checking MCP Server Logs")
    print("=" * 50)

    log_files = ["mcp_server.log", "mcp_server_debug.log"]

    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"📝 {log_file}: {size} bytes")

            if size > 0:
                with open(log_file, "r") as f:
                    lines = f.readlines()
                    print(f"   Last 5 lines:")
                    for line in lines[-5:]:
                        print(f"   {line.strip()}")
            else:
                print(f"   ⚠️  Log file is empty")
        else:
            print(f"❌ {log_file} not found")


def check_moodle_database():
    """Check Moodle database directly"""
    print("\n🔍 Checking Moodle Database")
    print("=" * 50)

    try:
        # Check if Docker container is running
        result = subprocess.run(
            ["docker", "ps", "-q", "--filter", "name=moodleclaude_db"],
            capture_output=True,
            text=True,
        )

        if not result.stdout.strip():
            print("❌ Moodle database container not running")
            return

        print("✅ Database container is running")

        # Query recent courses
        sql_query = """
        SELECT 
            c.id, 
            c.fullname, 
            c.timecreated,
            FROM_UNIXTIME(c.timecreated) as created_date,
            COUNT(DISTINCT s.id) as sections,
            COUNT(DISTINCT cm.id) as activities
        FROM mdl_course c
        LEFT JOIN mdl_course_sections s ON c.id = s.course 
        LEFT JOIN mdl_course_modules cm ON c.id = cm.course
        WHERE c.id > 1 
        GROUP BY c.id, c.fullname, c.timecreated
        ORDER BY c.timecreated DESC 
        LIMIT 10;
        """

        result = subprocess.run(
            [
                "docker",
                "exec",
                "moodleclaude_db",
                "mysql",
                "-u",
                "bn_moodle",
                "-D",
                "bitnami_moodle",
                "-e",
                sql_query,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("📊 Recent Courses:")
            lines = result.stdout.strip().split("\n")
            for line in lines:
                if line and not line.startswith("mysql:"):
                    print(f"   {line}")
        else:
            print(f"❌ Database query failed: {result.stderr}")

        # Check enrollments
        enrollment_query = """
        SELECT 
            c.id,
            c.fullname,
            COUNT(DISTINCT ue.userid) as enrolled_users
        FROM mdl_course c
        JOIN mdl_enrol e ON c.id = e.courseid
        JOIN mdl_user_enrolments ue ON e.id = ue.enrolid
        WHERE c.id > 1
        GROUP BY c.id, c.fullname
        ORDER BY c.id;
        """

        result = subprocess.run(
            [
                "docker",
                "exec",
                "moodleclaude_db",
                "mysql",
                "-u",
                "bn_moodle",
                "-D",
                "bitnami_moodle",
                "-e",
                enrollment_query,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("\n👥 Course Enrollments:")
            lines = result.stdout.strip().split("\n")
            for line in lines:
                if line and not line.startswith("mysql:"):
                    print(f"   {line}")

    except Exception as e:
        print(f"❌ Database check failed: {e}")


async def test_mcp_server_functionality():
    """Test MCP server functionality"""
    print("\n🔍 Testing MCP Server Functionality")
    print("=" * 50)

    load_dotenv()

    if not os.getenv("MOODLE_URL") or not os.getenv("MOODLE_TOKEN"):
        print("❌ MOODLE_URL or MOODLE_TOKEN not configured")
        return

    print("✅ Environment variables configured")

    # Test content parser
    from content_parser import ChatContentParser

    parser = ChatContentParser()
    test_content = """
    User: Show me a Python function
    
    Assistant: Here's an example:
    
    ```python
    def hello(name):
        return f"Hello, {name}!"
    ```
    
    This function takes a name and returns a greeting.
    """

    parsed = parser.parse_chat(test_content)
    print(f"📝 Content Parser Test:")
    print(f"   Items found: {len(parsed.items)}")
    for item in parsed.items:
        print(f"   - {item.type}: {item.title}")

    # Test Moodle connection
    try:
        from moodle_client import MoodleClient

        async with MoodleClient(
            os.getenv("MOODLE_URL"), os.getenv("MOODLE_TOKEN")
        ) as client:
            courses = await client.get_courses()
            print(f"🎓 Moodle Connection Test:")
            print(f"   Accessible courses: {len(courses)}")

            # Test course creation (but don't actually create one)
            print(f"   Moodle URL: {client.base_url}")
            print(f"   API Endpoint: {client.api_url}")

    except Exception as e:
        print(f"❌ Moodle connection test failed: {e}")


def check_claude_desktop_config():
    """Check Claude Desktop MCP configuration"""
    print("\n🔍 Checking Claude Desktop MCP Configuration")
    print("=" * 50)

    config_paths = [
        Path.home()
        / "Library"
        / "Application Support"
        / "Claude"
        / "claude_desktop_config.json",
        Path.home() / ".config" / "claude-desktop" / "config.json",
    ]

    config_found = False
    for config_path in config_paths:
        if config_path.exists():
            config_found = True
            print(f"✅ Config found: {config_path}")

            try:
                with open(config_path, "r") as f:
                    config = json.load(f)

                if "mcpServers" in config:
                    mcp_servers = config["mcpServers"]
                    print(f"📋 MCP Servers configured: {len(mcp_servers)}")

                    for server_name, server_config in mcp_servers.items():
                        print(f"   📡 {server_name}:")
                        if "command" in server_config:
                            command = server_config["command"]
                            if isinstance(command, list):
                                print(f"      Command: {' '.join(command)}")
                            else:
                                print(f"      Command: {command}")

                        if "args" in server_config:
                            print(f"      Args: {server_config['args']}")

                        # Check if moodle-course-creator is configured
                        if "moodle" in server_name.lower():
                            print(f"      🎯 Moodle MCP server found!")

                            # Check if the command path exists
                            if "command" in server_config:
                                cmd = server_config["command"]
                                if isinstance(cmd, list) and len(cmd) > 1:
                                    script_path = Path(cmd[1])
                                    if script_path.exists():
                                        print(f"      ✅ Script exists: {script_path}")
                                    else:
                                        print(
                                            f"      ❌ Script not found: {script_path}"
                                        )
                else:
                    print("⚠️  No MCP servers configured")

            except Exception as e:
                print(f"❌ Failed to read config: {e}")

    if not config_found:
        print("❌ Claude Desktop config not found")
        print("   Expected locations:")
        for path in config_paths:
            print(f"   - {path}")


async def main():
    """Run comprehensive validation"""
    print("🔧 MCP Integration Validation")
    print("=" * 60)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Run all checks
    check_claude_desktop_config()
    check_claude_desktop_logs()
    check_mcp_server_logs()
    check_moodle_database()
    await test_mcp_server_functionality()

    print("\n" + "=" * 60)
    print("🎯 Validation Summary")
    print("=" * 60)
    print("✅ Check completed - review output above for issues")
    print("💡 If Claude Desktop logs are empty, MCP server may not be connecting")
    print("💡 If database shows courses but Claude Desktop fails, check MCP config")
    print("💡 If content parser shows 0 items, check regex patterns")


if __name__ == "__main__":
    asyncio.run(main())

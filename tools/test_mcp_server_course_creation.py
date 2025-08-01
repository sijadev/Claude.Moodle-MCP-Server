#!/usr/bin/env python3
"""
Test MCP Server Course Creation
==============================
Testet die MCP Server Kurserstellung über MCP-Protokoll.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set environment variables from config
PROJECT_ROOT = Path(__file__).parent.parent
config_file = PROJECT_ROOT / "config" / "moodle_tokens.env"

if config_file.exists():
    with open(config_file, "r") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value.strip("\"'")

# Now import the MCP server components
from core.working_mcp_server import config, handle_create_course


async def test_mcp_course_creation():
    """Teste MCP Server Kurserstellung."""
    print("🚀 Test: MCP Server Kurserstellung")
    print("=" * 40)

    print(f"🌐 Moodle URL: {config.moodle_url}")
    print(f"🔐 Basic Token: {os.environ.get('MOODLE_BASIC_TOKEN', 'N/A')[:10]}...")
    print(f"🔐 Admin Token: {os.environ.get('MOODLE_ADMIN_TOKEN', 'N/A')[:10]}...")

    # Test create_course handler
    print("\n📋 Teste create_course Handler...")

    arguments = {
        "fullname": "MCP Handler Test Course",
        "shortname": "mcphandler",
        "category_id": 1,
    }

    try:
        result = await handle_create_course(arguments)

        if result and len(result) > 0:
            response_text = result[0].text
            print("✅ MCP Handler erfolgreich!")
            print("📄 Response:")
            print("   " + response_text.replace("\n", "\n   "))
        else:
            print("❌ Kein Ergebnis vom MCP Handler")

    except Exception as e:
        print(f"❌ MCP Handler Fehler: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 40)
    print("🎯 MCP Server Test abgeschlossen!")


if __name__ == "__main__":
    asyncio.run(test_mcp_course_creation())

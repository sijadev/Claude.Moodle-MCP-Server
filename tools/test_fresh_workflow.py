#!/usr/bin/env python3
"""
Test script for the new v3.0 fresh installation workflow
Tests the setup without actually running containers
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_workflow_components():
    """Test all components of the fresh installation workflow"""

    print("🧪 Testing MoodleClaude v3.0 Fresh Installation Workflow")
    print("=" * 60)

    tests_passed = 0
    total_tests = 0

    # Test 1: Master Config System
    print("\n1️⃣ Testing Master Configuration System...")
    total_tests += 1
    try:
        from config.master_config import get_master_config

        config = get_master_config()

        # Validate config structure
        assert hasattr(config, "credentials"), "Missing credentials"
        assert hasattr(config, "services"), "Missing services"
        assert hasattr(config, "server"), "Missing server config"
        assert (
            config.credentials.admin_password == "MoodleClaude2025!"
        ), "Wrong admin password"
        assert config.credentials.ws_user == "wsuser", "Wrong WS user"

        print("✅ Master configuration system working")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Master configuration failed: {e}")

    # Test 2: Config Manager
    print("\n2️⃣ Testing Configuration Manager...")
    total_tests += 1
    try:
        from tools.config_manager import sync_all_configurations

        success = sync_all_configurations()

        # Check generated files
        env_file = PROJECT_ROOT / ".env"
        assert env_file.exists(), ".env file not generated"

        with open(env_file) as f:
            env_content = f.read()
            assert (
                "MOODLE_ADMIN_PASSWORD=MoodleClaude2025!" in env_content
            ), "Wrong password in .env"
            assert "MOODLE_WS_USER=wsuser" in env_content, "Wrong WS user in .env"

        print("✅ Configuration manager working")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Configuration manager failed: {e}")

    # Test 3: Setup Script Components
    print("\n3️⃣ Testing Setup Script Components...")
    total_tests += 1
    try:
        from tools.setup.setup_fresh_moodle_v2 import (
            create_webservice_user,
            fix_mcp_server_path,
            generate_api_tokens,
            generate_unified_config,
            run_validation_tests,
        )

        # Test function availability
        assert callable(generate_unified_config), "generate_unified_config not callable"
        assert callable(create_webservice_user), "create_webservice_user not callable"
        assert callable(generate_api_tokens), "generate_api_tokens not callable"
        assert callable(fix_mcp_server_path), "fix_mcp_server_path not callable"
        assert callable(run_validation_tests), "run_validation_tests not callable"

        print("✅ Setup script components available")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Setup script components failed: {e}")

    # Test 4: MCP Server Launcher
    print("\n4️⃣ Testing MCP Server Launcher...")
    total_tests += 1
    try:
        mcp_launcher = PROJECT_ROOT / "server" / "mcp_server_launcher.py"
        assert mcp_launcher.exists(), "MCP launcher not found"

        # Test import path fix
        with open(mcp_launcher) as f:
            launcher_content = f.read()
            assert (
                "server_dir = os.path.dirname(os.path.abspath(__file__))"
                in launcher_content
            ), "Path fix not applied"
            assert (
                "project_root = os.path.dirname(server_dir)" in launcher_content
            ), "Project root fix not applied"

        print("✅ MCP server launcher path fixes in place")
        tests_passed += 1
    except Exception as e:
        print(f"❌ MCP server launcher failed: {e}")

    # Test 5: Docker Compose Configuration
    print("\n5️⃣ Testing Docker Compose Configuration...")
    total_tests += 1
    try:
        docker_compose = (
            PROJECT_ROOT / "operations" / "docker" / "docker-compose.fresh.yml"
        )
        assert docker_compose.exists(), "Fresh docker-compose not found"

        with open(docker_compose) as f:
            compose_content = f.read()
            assert (
                "MOODLE_PASSWORD: MoodleClaude2025!" in compose_content
            ), "Wrong password in docker-compose"
            assert (
                "PGADMIN_DEFAULT_PASSWORD: MoodleClaude2025!" in compose_content
            ), "Wrong pgadmin password"

        # Check symlink
        main_compose = PROJECT_ROOT / "docker-compose.yml"
        assert main_compose.exists(), "docker-compose.yml symlink missing"

        print("✅ Docker compose configuration consistent")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Docker compose configuration failed: {e}")

    # Test 6: Plugin Directory
    print("\n6️⃣ Testing Plugin Directory...")
    total_tests += 1
    try:
        plugin_dir = PROJECT_ROOT / "moodle_plugin" / "local_moodleclaude"
        assert plugin_dir.exists(), "Plugin directory not found"

        version_file = plugin_dir / "version.php"
        assert version_file.exists(), "Plugin version.php not found"

        classes_dir = plugin_dir / "classes"
        assert classes_dir.exists(), "Plugin classes directory not found"

        print("✅ Plugin directory structure valid")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Plugin directory failed: {e}")

    # Test 7: Setup Guide
    print("\n7️⃣ Testing Setup Guide...")
    total_tests += 1
    try:
        setup_guide = PROJECT_ROOT / "SETUP_GUIDE_V3.md"
        assert setup_guide.exists(), "Setup guide not found"

        with open(setup_guide) as f:
            guide_content = f.read()
            assert "v3.0" in guide_content, "Version not mentioned in guide"
            assert (
                "python tools/setup/setup_fresh_moodle_v2.py --quick-setup"
                in guide_content
            ), "Quick setup command missing"

        print("✅ Setup guide created")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Setup guide failed: {e}")

    # Summary
    print(f"\n🎯 Test Summary:")
    print(f"✅ Tests passed: {tests_passed}/{total_tests}")

    if tests_passed == total_tests:
        print("🎉 All workflow components ready!")
        print("\n📋 Next steps:")
        print("1. Run: python tools/setup/setup_fresh_moodle_v2.py --quick-setup")
        print("2. Restart Claude Desktop")
        print("3. Test MCP integration")
        return True
    else:
        print("⚠️ Some tests failed - check components above")
        return False


if __name__ == "__main__":
    success = test_workflow_components()
    sys.exit(0 if success else 1)

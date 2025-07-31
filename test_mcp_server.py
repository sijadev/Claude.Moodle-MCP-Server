#!/usr/bin/env python3
"""
MCP Server validation script
Tests server initialization and configuration
"""

import subprocess
import sys
import time
import os
import json

def test_mcp_server_initialization():
    """Test if the MCP server initializes correctly"""
    print("🔍 Testing MCP Server Initialization...")
    
    try:
        # Start the server and capture its initialization
        process = subprocess.Popen(
            [sys.executable, "-m", "src.core.advanced_mcp_server"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        # Wait a short time for initialization
        time.sleep(1)
        
        # Terminate to get initialization logs
        process.terminate()
        stdout, stderr = process.communicate()
        
        # Check initialization logs
        stderr_text = stderr.decode()
        
        # Look for key initialization messages
        required_messages = [
            "Advanced MCP Server initialized with dual-token configuration",
            "Enhanced Moodle client initialized successfully", 
            "AdvancedMoodleMCPServer fully initialized with intelligent features",
            "Starting Advanced MoodleMCP Server with intelligent features"
        ]
        
        success = True
        for message in required_messages:
            if message not in stderr_text:
                print(f"❌ Missing initialization message: {message}")
                success = False
            else:
                print(f"✅ Found: {message}")
        
        if success:
            print("\n✅ MCP Server initialization successful!")
            print("📝 Note: Server shuts down when run standalone - this is normal MCP behavior")
            print("🎯 Server will stay running when invoked by Claude Desktop")
        else:
            print("\n❌ MCP Server initialization failed!")
            print("\n📋 Full stderr output:")
            print(stderr_text)
            
        return success
            
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False

def validate_configuration():
    """Validate Claude Desktop configuration files"""
    print("\n🔧 Validating Configuration Files...")
    
    config_files = [
        "config/claude_desktop_config_basic.json",
        "config/claude_desktop_config_advanced.json"
    ]
    
    valid = True
    for config_file in config_files:
        if not os.path.exists(config_file):
            print(f"❌ Missing configuration file: {config_file}")
            valid = False
            continue
            
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Check for placeholder values
            config_str = json.dumps(config)
            if "/path/to/your/MoodleClaude" in config_str:
                print(f"❌ {config_file} contains placeholder path")
                valid = False
            elif "your_basic_token_here" in config_str:
                print(f"❌ {config_file} contains placeholder tokens")
                valid = False
            else:
                print(f"✅ {config_file} is properly configured")
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {config_file}: {e}")
            valid = False
    
    return valid

def check_environment():
    """Check environment variables and .env file"""
    print("\n🌍 Checking Environment Configuration...")
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        required_vars = [
            'MOODLE_URL',
            'MOODLE_BASIC_TOKEN', 
            'MOODLE_PLUGIN_TOKEN',
            'MOODLE_USERNAME'
        ]
        
        with open('.env', 'r') as f:
            env_content = f.read()
        
        missing_vars = []
        for var in required_vars:
            if f"{var}=" not in env_content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        else:
            print("✅ All required environment variables present")
            return True
    else:
        print("❌ .env file not found")
        return False

if __name__ == "__main__":
    print("🚀 MoodleClaude MCP Server Validation\n")
    
    # Run all tests
    init_ok = test_mcp_server_initialization()
    config_ok = validate_configuration()
    env_ok = check_environment()
    
    print(f"\n📊 Results Summary:")
    print(f"  Server Initialization: {'✅' if init_ok else '❌'}")
    print(f"  Configuration Files:   {'✅' if config_ok else '❌'}")
    print(f"  Environment Setup:     {'✅' if env_ok else '❌'}")
    
    if init_ok and config_ok and env_ok:
        print(f"\n🎉 All tests passed! MCP Server is ready for Claude Desktop.")
        sys.exit(0)
    else:
        print(f"\n⚠️  Some issues found. Please fix the above problems.")
        sys.exit(1)
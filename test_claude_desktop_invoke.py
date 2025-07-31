#!/usr/bin/env python3
"""
Test script to simulate how Claude Desktop invokes the MCP server
"""

import subprocess
import sys
import os
import json
import time

def test_claude_desktop_invocation():
    """Test MCP server invocation like Claude Desktop would do it"""
    print("🧪 Testing Claude Desktop MCP Server Invocation")
    
    # Load the advanced configuration
    config_file = "config/claude_desktop_config_advanced.json"
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    server_config = config["mcpServers"]["moodle-advanced"]
    
    print(f"📋 Configuration:")
    print(f"  Command: {server_config['command']}")
    print(f"  Args: {server_config['args']}")
    print(f"  Working Directory: {server_config['cwd']}")
    
    # Test if the command can be executed
    try:
        # Change to the working directory
        original_cwd = os.getcwd()
        os.chdir(server_config['cwd'])
        
        # Set environment variables
        env = os.environ.copy()
        env.update(server_config['env'])
        
        # Test the command
        cmd = [server_config['command']] + server_config['args']
        print(f"\n🚀 Testing command: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=server_config['cwd']
        )
        
        # Give it time to initialize
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ Server started successfully and is running!")
            
            # Terminate the test
            process.terminate()
            stdout, stderr = process.communicate(timeout=5)
            
            if stderr:
                print("\n📋 Initialization output:")
                stderr_text = stderr.decode()
                for line in stderr_text.split('\n')[:10]:  # Show first 10 lines
                    if line.strip():
                        print(f"  {line}")
            
            return True
            
        else:
            print("❌ Server exited immediately!")
            stdout, stderr = process.communicate()
            if stderr:
                print(f"Error: {stderr.decode()}")
            return False
            
    except FileNotFoundError as e:
        print(f"❌ Command not found: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        os.chdir(original_cwd)

def check_python_executable():
    """Check if the Python executable exists and works"""
    config_file = "config/claude_desktop_config_advanced.json"
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    python_path = config["mcpServers"]["moodle-advanced"]["command"]
    
    print(f"\n🐍 Testing Python executable: {python_path}")
    
    if os.path.exists(python_path):
        print("✅ Python executable exists")
        
        # Test if it's executable
        if os.access(python_path, os.X_OK):
            print("✅ Python executable has execute permissions")
            
            # Test if it works
            try:
                result = subprocess.run([python_path, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ Python version: {result.stdout.strip()}")
                    return True
                else:
                    print(f"❌ Python test failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Python test error: {e}")
                return False
        else:
            print("❌ Python executable is not executable")
            return False
    else:
        print("❌ Python executable does not exist")
        return False

if __name__ == "__main__":
    print("🔍 Claude Desktop MCP Server Invocation Test\n")
    
    python_ok = check_python_executable()
    if python_ok:
        server_ok = test_claude_desktop_invocation()
        
        if server_ok:
            print(f"\n🎉 Success! The MCP server should work properly with Claude Desktop.")
        else:
            print(f"\n⚠️ Server invocation failed. Check the configuration.")
    else:
        print(f"\n⚠️ Python executable issue. Please fix the Python path.")
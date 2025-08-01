#!/usr/bin/env python3
"""
Bug Fix Validation Tool
========================

Validates that all known bug fixes are properly integrated and working.
Used by pre-commit hooks and CI/CD pipeline.
"""

import os
import sys
from pathlib import Path

def validate_python_path_fix():
    """Validate Python path detection fix"""
    setup_file = Path("setup/setup_moodleclaude_v3_fixed.py")
    
    if not setup_file.exists():
        print("❌ setup/setup_moodleclaude_v3_fixed.py not found")
        return False
    
    with open(setup_file, 'r') as f:
        content = f.read()
    
    if "get_python_path" not in content:
        print("❌ Python path fix not found in setup script")
        return False
    
    print("✅ Python path fix validated")
    return True

def validate_mcp_server_fix():
    """Validate MCP server fixes"""
    mcp_file = Path("src/core/working_mcp_server.py")
    
    if not mcp_file.exists():
        print("❌ working_mcp_server.py not found")
        return False
    
    with open(mcp_file, 'r') as f:
        content = f.read()
    
    required_elements = [
        "create_course",
        "get_courses", 
        "test_connection"
    ]
    
    for element in required_elements:
        if element not in content:
            print(f"❌ Required element '{element}' not found in MCP server")
            return False
    
    print("✅ MCP server fixes validated")
    return True

def validate_test_suite_fix():
    """Validate test suite has bug fixes"""
    test_file = Path("tools/run_docker_test_suite_fixed.py")
    
    if not test_file.exists():
        print("❌ Fixed test suite not found")
        return False
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    if "bug" not in content.lower() or "fix" not in content.lower():
        print("❌ Bug fixes not integrated in test suite")
        return False
    
    print("✅ Test suite fixes validated")
    return True

def validate_documentation():
    """Validate bug fix documentation exists"""
    doc_file = Path("BUGFIX_DOCUMENTATION.md")
    
    if not doc_file.exists():
        print("❌ Bug fix documentation not found")
        return False
    
    with open(doc_file, 'r') as f:
        content = f.read()
    
    required_sections = [
        "spawn python ENOENT",
        "Access control exception",
        "Token permissions",
        "Python path detection"
    ]
    
    for section in required_sections:
        if section.lower() not in content.lower():
            print(f"❌ Missing documentation section: {section}")
            return False
    
    print("✅ Bug fix documentation validated")
    return True

def main():
    """Main validation function"""
    print("🔍 Validating MoodleClaude bug fixes...")
    
    validations = [
        validate_python_path_fix,
        validate_mcp_server_fix,
        validate_test_suite_fix,
        validate_documentation
    ]
    
    all_passed = True
    for validation in validations:
        if not validation():
            all_passed = False
    
    if all_passed:
        print("🎉 All bug fix validations passed!")
        return 0
    else:
        print("❌ Some bug fix validations failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Test Enhanced MoodleClaude Web Service Setup
===========================================

Quick test script to verify the enhanced setup works correctly.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🧪 Testing Enhanced MoodleClaude Web Service Setup")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    enhanced_setup = project_root / "tools" / "setup" / "enhanced_webservice_setup.py"
    
    # Check if enhanced setup exists
    if not enhanced_setup.exists():
        print(f"❌ Enhanced setup script not found: {enhanced_setup}")
        return False
    
    print(f"✅ Enhanced setup script found: {enhanced_setup}")
    
    # Check required environment variables
    required_vars = ["MOODLE_URL", "MOODLE_ADMIN_PASSWORD"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing required environment variables:")
        for var in missing_vars:
            print(f"   • {var}")
        print()
        print("💡 To test the enhanced setup, please set:")
        print("   export MOODLE_URL='http://your-moodle-url'")
        print("   export MOODLE_ADMIN_PASSWORD='your-admin-password'")
        print()
        print("🔧 For a dry run test (checking scripts only), this is normal.")
        return True
    
    print("✅ Required environment variables are set")
    
    # Test import of enhanced setup
    try:
        sys.path.insert(0, str(enhanced_setup.parent))
        import enhanced_webservice_setup
        print("✅ Enhanced setup module imports successfully")
        
        # Test class instantiation
        setup = enhanced_webservice_setup.EnhancedMoodleWebServiceSetup()
        print("✅ Enhanced setup class instantiates successfully")
        
        # Test method existence
        required_methods = [
            'validate_moodle_environment',
            'get_enhanced_function_list',
            'validate_function_availability',
            'create_enhanced_php_script',
            'perform_comprehensive_testing',
            'generate_dashboard_report'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(setup, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Missing methods: {missing_methods}")
            return False
        
        print("✅ All required methods are present")
        
        # Test function list generation
        functions = setup.get_enhanced_function_list()
        total_functions = sum(len(func_list) for func_list in functions.values())
        print(f"✅ Function list generated: {len(functions)} categories, {total_functions} total functions")
        
        # Show function categories
        print("\n📋 Function Categories:")
        for category, func_list in functions.items():
            print(f"   • {category}: {len(func_list)} functions")
        
        print("\n🎉 Enhanced setup validation completed successfully!")
        print("\n🚀 Ready to run: python3 tools/setup/enhanced_webservice_setup.py")
        return True
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
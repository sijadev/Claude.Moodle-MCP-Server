# 🧪 Manual Testing Scripts

This directory contains manual testing scripts that validate specific functionality and provide detailed output for debugging and verification.

## 📁 Test Files Overview

### Core Functionality Tests
- **`test_direct_moodle.py`** - Basic Moodle API connection and course creation
- **`test_mcp_connection.py`** - MCP server configuration and readiness validation
- **`test_realistic_moodle.py`** - Realistic workflow testing with available functions

### Advanced Feature Tests  
- **`test_enhanced_moodle.py`** - Enhanced MoodleClient with WSManageSections support
- **`test_wsmanage_correct.py`** - WSManageSections plugin with correct parameters
- **`test_wsmanagesections.py`** - WSManageSections functionality exploration
- **`test_wsmanage_params.py`** - Parameter format testing for WSManageSections

### Function Validation Tests
- **`test_core_functions.py`** - Core function availability and parameter validation

## 🚀 Quick Start

### Run All Manual Tests
```bash
# Run all manual tests with summary
python tests/manual/run_manual_tests.py

# Run specific test categories
python tests/manual/run_manual_tests.py --category core
python tests/manual/run_manual_tests.py --category advanced
python tests/manual/run_manual_tests.py --category validation
```

### Run Individual Tests
```bash
# Basic functionality
uv run python tests/manual/test_direct_moodle.py
uv run python tests/manual/test_mcp_connection.py

# Advanced features
uv run python tests/manual/test_enhanced_moodle.py
uv run python tests/manual/test_wsmanage_correct.py

# Function validation
uv run python tests/manual/test_core_functions.py
```

## 📊 Test Categories

### 🔧 Core Functionality (`--category core`)
**Basic system validation and connectivity**

1. **`test_direct_moodle.py`**
   - ✅ Moodle API connection
   - ✅ Site information retrieval
   - ✅ Basic course creation
   - ✅ Course listing and sections

2. **`test_mcp_connection.py`**
   - ✅ Configuration loading
   - ✅ Content parsing readiness
   - ✅ Moodle credentials validation
   - ✅ MCP server functionality

3. **`test_realistic_moodle.py`**
   - ✅ Realistic course creation workflow
   - ✅ Section editing capabilities
   - ✅ Content simulation
   - ✅ Error handling

### 🚀 Advanced Features (`--category advanced`)
**Enhanced functionality and plugin integration**

1. **`test_enhanced_moodle.py`**
   - ✅ WSManageSections integration
   - ✅ Dynamic section creation
   - ✅ Custom section positioning
   - ✅ Content organization by section

2. **`test_wsmanage_correct.py`**
   - ✅ WSManageSections with correct parameters
   - ✅ Section creation at specific positions
   - ✅ Multiple section creation
   - ✅ Section content updates

3. **`test_wsmanagesections.py`**
   - ✅ WSManageSections function exploration
   - ✅ Parameter format discovery
   - ✅ Function availability testing

### 🔍 Function Validation (`--category validation`)
**API function availability and parameter validation**

1. **`test_core_functions.py`**
   - ✅ Core function availability testing
   - ✅ Direct API call validation
   - ✅ Parameter format verification

2. **`test_wsmanage_params.py`**
   - ✅ WSManageSections parameter format testing
   - ✅ Error message analysis
   - ✅ Function signature discovery

## 🎯 Expected Results

### Successful Test Indicators

**Core Tests:**
```
✅ Site: MoodleClaude Test Environment
✅ Course created with ID: X
✅ ALL TESTS PASSED!
```

**Advanced Tests:**
```
✅ Created 'Python Basics' section: 2
✅ Created 'Advanced Topics' section: 3
✅ Enhanced course structure working
```

**Validation Tests:**
```
✅ Available: 10+ functions
✅ core_course_create_courses
✅ local_wsmanagesections_create_sections
```

### Common Issues and Solutions

**Token Issues:**
```
❌ HTTP 403: Forbidden
```
**Solution:** Regenerate token via Moodle web interface

**Function Not Available:**
```
❌ Can't find data record in database table external_functions
```
**Solution:** Add function to web service via Moodle admin

**Parameter Issues:**
```
❌ Invalid parameter value detected
```
**Solution:** Check parameter format and required fields

## 🔧 Configuration Requirements

### Environment Variables
```bash
MOODLE_URL=http://localhost:8080
MOODLE_TOKEN=your_32_character_token
MOODLE_USERNAME=simon
```

### Prerequisites
- Docker containers running (moodleclaude_app, moodleclaude_db)
- Moodle web services configured
- Valid token with appropriate permissions
- WSManageSections plugin enabled (for advanced tests)

## 🚀 Integration with Automated Tests

These manual tests complement the automated test suite:

```bash
# Run automated tests first
make test-unit
make test-integration

# Then run manual validation
python tests/manual/run_manual_tests.py

# Finally run E2E tests
make test-e2e
```

## 🎉 Test Development

### Adding New Manual Tests

1. **Create test file** in `tests/manual/`
2. **Follow naming convention**: `test_[feature]_[aspect].py`
3. **Include descriptive output** with ✅/❌ indicators
4. **Add to test runner** in appropriate category
5. **Update this README** with test description

### Test Template
```python
#!/usr/bin/env python3
"""
Description of what this test validates
"""

import asyncio
import os
from dotenv import load_dotenv

async def test_your_feature():
    load_dotenv()
    
    print(f"🔧 Testing Your Feature")
    print("=" * 40)
    
    try:
        # Your test implementation
        print(f"✅ Test passed")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_your_feature())
```

---

**These manual tests provide comprehensive validation of MoodleClaude functionality and are essential for ensuring system reliability!** 🧪✨
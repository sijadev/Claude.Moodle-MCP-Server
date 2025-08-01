# MoodleClaude Testing Guide

## 🎯 Quick Start

```bash
# Run all tests
make test

# Run specific test types
make test-unit        # Unit tests only
make test-integration # Integration tests only
make test-e2e        # End-to-end tests only

# With options
make test-coverage   # All tests with coverage
make test-html       # All tests with HTML report
```

## 📁 Test Structure

```
tests/
├── README.md                          # Comprehensive test documentation
├── conftest.py                        # Shared pytest fixtures
├── test_runner.py                     # Legacy test runner
├── unit/                             # 🧪 Unit Tests
│   ├── test_config.py                # Configuration validation
│   └── test_content_parser_fixed.py  # Content parsing logic
├── integration/                      # 🔗 Integration Tests
│   └── test_enhanced_moodle_claude.py # Moodle API integration
└── e2e/                             # 🌐 End-to-End Tests
    └── test_e2e_moodle_claude.py    # Browser automation tests
```

## 🚀 Test Runners

### 1. Comprehensive Test Runner (Recommended)

```bash
# All-in-one test runner with advanced features
./run_tests.sh [type] [options]

# Examples:
./run_tests.sh all -v -c --html    # All tests, verbose, coverage, HTML
./run_tests.sh unit -v             # Unit tests with verbose output
./run_tests.sh integration -c      # Integration tests with coverage
./run_tests.sh e2e                 # End-to-end tests
```

### 2. E2E Test Runner (Specialized)

```bash
# Dedicated E2E test runner with browser automation
./run_e2e_tests.sh [options]

# Examples:
./run_e2e_tests.sh --headed        # Run with browser UI visible
./run_e2e_tests.sh --url http://localhost --username admin
```

### 3. Make Commands (Convenient)

```bash
make test              # Run all tests
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-e2e         # E2E tests only
make test-coverage    # All tests with coverage
make test-html        # All tests with HTML report
make e2e-setup        # Setup E2E environment
make e2e-headed       # E2E tests with browser UI
```

### 4. Direct Pytest (Flexible)

```bash
# Run specific tests directly
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v

# With markers
pytest -m unit
pytest -m integration  
pytest -m e2e

# Specific test files
pytest tests/unit/test_config.py
pytest tests/integration/test_enhanced_moodle_claude.py::TestEnhancedMoodleAPI
```

## 📊 Test Categories

### 🧪 Unit Tests (`tests/unit/`)
**Fast, isolated tests for individual components**

- ✅ **Configuration validation** - Environment variables, defaults, validation logic
- ✅ **Content parsing** - Chat content analysis, language detection, topic extraction  
- ✅ **Data models** - Dataclass validation, serialization
- ✅ **Utility functions** - Helper methods, formatters

**Run with:**
```bash
make test-unit
./run_tests.sh unit -v
pytest tests/unit/ -v
```

### 🔗 Integration Tests (`tests/integration/`)
**Component interactions and API integrations**

- ✅ **Moodle API client** - Web services, authentication, error handling
- ✅ **Section management** - Create, update, delete, bulk operations
- ✅ **File upload workflows** - File resources, repositories, validation
- ✅ **Error scenarios** - Network errors, API failures, invalid data

**Run with:**
```bash
make test-integration
./run_tests.sh integration -v
pytest tests/integration/ -v
```

### 🌐 End-to-End Tests (`tests/e2e/`)
**Complete user workflows with browser automation**

- ✅ **Course creation** - From chat content to structured courses
- ✅ **Section management UI** - Create, edit, move, bulk operations
- ✅ **File upload interfaces** - File picker, drag-drop, repositories
- ✅ **Accessibility validation** - Keyboard navigation, screen readers

**Run with:**
```bash
make test-e2e
./run_e2e_tests.sh
pytest tests/e2e/ -v
```

## 🛠️ Test Configuration

### Main Configuration Files

- **`pytest.ini`** - Main pytest configuration
- **`pytest_e2e.ini`** - E2E-specific configuration
- **`requirements-e2e.txt`** - E2E test dependencies
- **`conftest.py`** - Shared fixtures and setup

### Environment Variables

```bash
# E2E test configuration
export MOODLE_URL="http://localhost"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="password"
export HEADLESS="true"
export BROWSER="chromium"
```

### Test Markers

```bash
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m e2e           # E2E tests only
pytest -m "not slow"    # Skip slow tests
pytest -m accessibility # Accessibility tests only
```

## 📈 Test Reports

### Generated Reports

After running tests, reports are available in the `reports/` directory:

- **`junit.xml`** - JUnit XML for CI/CD integration
- **`report.html`** - HTML test report with results
- **`e2e_report.html`** - Specialized E2E test report
- **`htmlcov/`** - Coverage report (when using `-c` flag)

### Viewing Reports

```bash
# Open HTML reports
open reports/report.html      # General test report
open reports/e2e_report.html  # E2E test report
open reports/htmlcov/index.html # Coverage report
```

## 🎯 Common Testing Workflows

### Development Workflow

```bash
# 1. Quick validation during development
make test-unit

# 2. Integration check before commit
make test-fast  # Unit + Integration (skips E2E)

# 3. Full validation before push
make test-coverage
```

### CI/CD Workflow

```bash
# 1. Fast feedback (unit tests)
./run_tests.sh unit -v

# 2. Integration validation
./run_tests.sh integration -v

# 3. E2E validation (separate job)
./run_e2e_tests.sh --headless
```

### Debugging Workflow

```bash
# 1. Run with verbose output
./run_tests.sh unit -v

# 2. Run specific failing test
pytest tests/unit/test_config.py::test_specific_function -v -s

# 3. E2E debugging with browser UI
./run_e2e_tests.sh --headed
```

## 🔧 Setup Requirements

### Unit Tests
```bash
pip install pytest pytest-mock
```

### Integration Tests  
```bash
pip install pytest pytest-asyncio requests responses
```

### E2E Tests
```bash
pip install -r requirements-e2e.txt
playwright install chromium
```

### Complete Setup
```bash
make e2e-setup  # Installs all dependencies including browsers
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   export PYTHONPATH="."
   pytest tests/
   ```

2. **E2E Browser Issues**
   ```bash
   playwright install --force chromium
   ```

3. **Permission Issues**
   ```bash
   chmod +x run_tests.sh run_e2e_tests.sh
   ```

4. **Moodle Connection (E2E)**
   ```bash
   # Verify Moodle is running
   curl -I http://localhost

   # Check credentials
   python demos/check_webservices.py
   ```

### Getting Help

```bash
./run_tests.sh --help        # Comprehensive test runner help
./run_e2e_tests.sh --help    # E2E test runner help
make help-testing            # Makefile testing help
```

## 📚 Writing New Tests

### Unit Test Example

```python
# tests/unit/test_new_feature.py
import pytest
from your_module import YourClass

class TestYourClass:
    def test_basic_functionality(self):
        obj = YourClass()
        result = obj.method()
        assert result == expected_value
```

### Integration Test Example

```python
# tests/integration/test_new_integration.py
import pytest
from unittest.mock import Mock, patch

@pytest.mark.integration
class TestNewIntegration:
    @patch('requests.post')
    def test_api_integration(self, mock_post):
        mock_post.return_value.json.return_value = {"success": True}
        # Test implementation
```

### E2E Test Example

```python
# tests/e2e/test_new_workflow.py
import pytest
from playwright.async_api import Page

@pytest.mark.e2e
@pytest.mark.asyncio
class TestNewWorkflow:
    async def test_user_workflow(self, page: Page):
        await page.goto("http://localhost")
        # Test implementation
```

## 🎉 Best Practices

### Test Organization
- ✅ Keep tests close to code they test
- ✅ Use descriptive test names
- ✅ Group related tests in classes
- ✅ Use appropriate markers

### Test Data
- ✅ Use fixtures for reusable data
- ✅ Clean up test data after tests
- ✅ Avoid hardcoded values
- ✅ Use factories for complex objects

### Assertions
- ✅ Use descriptive assertion messages
- ✅ Test one thing per test method
- ✅ Use pytest's rich assertion features
- ✅ Avoid testing implementation details

---

**Happy Testing!** 🧪✨

*For detailed information on specific test types, see the README files in each test directory.*

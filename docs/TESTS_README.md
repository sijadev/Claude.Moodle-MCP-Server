# MoodleClaude Test Suite

This directory contains the complete test suite for the MoodleClaude integration project.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared pytest fixtures
├── test_runner.py           # Main test runner
├── README.md               # This file
├── unit/                   # Unit tests
│   ├── test_config.py      # Configuration tests
│   └── test_content_parser_fixed.py  # Content parser tests
├── integration/            # Integration tests
│   └── test_enhanced_moodle_claude.py  # Moodle API integration tests
└── e2e/                    # End-to-end tests
    └── test_e2e_moodle_claude.py  # Browser automation tests
```

## Test Categories

### 🧪 Unit Tests (`tests/unit/`)
Fast, isolated tests for individual components:
- Configuration validation
- Content parsing and formatting
- Data model validation
- Utility functions

**Run unit tests:**
```bash
pytest tests/unit/ -v
```

### 🔗 Integration Tests (`tests/integration/`)
Tests for component interactions and API integrations:
- Moodle API client functionality
- Section management operations
- File upload workflows
- Error handling scenarios

**Run integration tests:**
```bash
pytest tests/integration/ -v
```

### 🌐 End-to-End Tests (`tests/e2e/`)
Browser automation tests for complete user workflows:
- Course creation from chat content
- Section management UI interactions
- File upload through browser
- Accessibility validation

**Run E2E tests:**
```bash
pytest tests/e2e/ -v
# or use the dedicated script:
./run_e2e_tests.sh
```

## Running Tests

### All Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run with verbose output
pytest -v
```

### By Category
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only  
pytest tests/integration/

# E2E tests only
pytest tests/e2e/
```

### By Marker
```bash
# Run only tests marked as 'unit'
pytest -m unit

# Run only tests marked as 'integration'
pytest -m integration

# Run only tests marked as 'e2e'
pytest -m e2e

# Skip slow tests
pytest -m "not slow"
```

### Specific Tests
```bash
# Run specific test file
pytest tests/unit/test_config.py

# Run specific test class
pytest tests/integration/test_enhanced_moodle_claude.py::TestEnhancedMoodleAPI

# Run specific test method
pytest tests/e2e/test_e2e_moodle_claude.py::TestSectionManagement::test_create_new_section
```

## Test Configuration

### Pytest Configuration
- Main config: `pytest.ini`
- E2E specific: `pytest_e2e.ini`

### Markers
Available test markers:
- `unit`: Unit tests
- `integration`: Integration tests  
- `e2e`: End-to-end tests
- `slow`: Tests that take longer to run
- `moodle`: Tests requiring Moodle connection
- `section_management`: Section-related tests
- `file_upload`: File upload tests
- `accessibility`: Accessibility tests

### Fixtures
Common fixtures in `conftest.py`:
- Test configuration
- Mock objects
- Database setup/teardown
- Browser automation setup

## Test Data

### Test Files
E2E tests create temporary test files in `test_data/` directory (auto-cleaned).

### Mock Data
Integration tests use mock responses to avoid external dependencies.

### Test Courses
E2E tests create and clean up test courses automatically.

## Prerequisites

### For Unit Tests
```bash
pip install pytest pytest-mock
```

### For Integration Tests
```bash
pip install pytest pytest-asyncio requests responses
```

### For E2E Tests
```bash
pip install -r requirements-e2e.txt
playwright install chromium
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run Unit Tests
  run: pytest tests/unit/ --junitxml=reports/unit-results.xml

- name: Run Integration Tests  
  run: pytest tests/integration/ --junitxml=reports/integration-results.xml

- name: Run E2E Tests
  run: ./run_e2e_tests.sh --headless
```

### Docker
```dockerfile
# Run tests in Docker
RUN pytest tests/unit/ tests/integration/
```

## Writing Tests

### Unit Test Example
```python
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
import pytest
from unittest.mock import Mock, patch

@pytest.mark.integration
class TestMoodleIntegration:
    @patch('requests.post')
    def test_api_call(self, mock_post):
        mock_post.return_value.json.return_value = {"success": True}
        # Test implementation
```

### E2E Test Example
```python
import pytest
from playwright.async_api import Page

@pytest.mark.e2e
@pytest.mark.asyncio
class TestBrowserWorkflow:
    async def test_user_workflow(self, page: Page):
        await page.goto("http://localhost")
        # Test implementation
```

## Test Reports

### HTML Reports
```bash
pytest --html=reports/report.html --self-contained-html
```

### Coverage Reports
```bash
pytest --cov=. --cov-report=html --cov-report=term
```

### JUnit XML (for CI)
```bash
pytest --junitxml=reports/junit.xml
```

## Debugging Tests

### Debug Mode
```bash
# Run with debug output
pytest -v -s

# Drop into debugger on failure
pytest --pdb

# Debug specific test
pytest tests/unit/test_config.py::test_specific_function -v -s
```

### Browser Debugging (E2E)
```bash
# Run E2E tests with visible browser
./run_e2e_tests.sh --headed

# Pause execution for manual inspection
# Add this in your test:
await page.pause()
```

## Best Practices

### Test Organization
- Keep tests close to the code they test
- Use descriptive test names
- Group related tests in classes
- Use appropriate markers

### Test Data
- Use fixtures for reusable test data
- Clean up test data after tests
- Avoid hardcoded values
- Use factories for complex objects

### Assertions
- Use descriptive assertion messages
- Test one thing per test method
- Use pytest's rich assertion features
- Avoid testing implementation details

### Mocking
- Mock external dependencies
- Use patch decorators appropriately
- Verify mock calls when relevant
- Don't over-mock

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Add project root to Python path
   export PYTHONPATH="."
   pytest
   ```

2. **Slow Tests**
   ```bash
   # Skip slow tests
   pytest -m "not slow"
   ```

3. **Browser Issues (E2E)**
   ```bash
   # Reinstall browsers
   playwright install --force
   ```

4. **Permission Issues**
   ```bash
   # Fix file permissions
   chmod -R 755 tests/
   ```

### Getting Help
- Check test output and error messages
- Review the documentation in each test directory
- Run tests with `-v` for verbose output
- Use `--tb=long` for detailed tracebacks

---

**Happy Testing!** 🧪✨

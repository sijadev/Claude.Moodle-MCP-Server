# MoodleClaude End-to-End Testing Guide

This document provides comprehensive guidance for running end-to-end (E2E) tests for the MoodleClaude integration using Playwright browser automation.

## Overview

The E2E test suite validates real browser interactions with Moodle, testing:

- **Section Management**: Course section creation, editing, and bulk operations
- **File Upload**: File resource creation and file picker functionality  
- **MoodleClaude Integration**: Complete workflows simulating Claude-generated content
- **Accessibility**: Keyboard navigation and screen reader compatibility

## Prerequisites

### System Requirements

- **Python 3.8+**
- **Node.js 16+** (for Playwright browsers)
- **Moodle Instance**: Running and accessible (local or remote)
- **Admin Access**: Valid admin credentials for the Moodle instance

### Moodle Setup Requirements

1. **Local Plugin Installation** (if testing advanced features):
   ```bash
   # Install wsmanagesections plugin
   git clone https://github.com/your-repo/local_wsmanagesections.git /path/to/moodle/local/wsmanagesections
   
   # Install via Moodle admin interface or CLI
   php admin/cli/upgrade.php
   ```

2. **Web Services Configuration**:
   - Enable web services: `Site Administration > Advanced features > Enable web services`
   - Create web service user with appropriate capabilities
   - Enable required web service functions

3. **File Upload Configuration**:
   - Configure file upload limits in `php.ini` and Moodle settings
   - Enable file repositories (Upload files, Server files, etc.)

## Quick Start

### 1. Automated Setup and Run

```bash
# Run with default settings (localhost Moodle)
./run_e2e_tests.sh

# Run against custom Moodle instance
./run_e2e_tests.sh --url http://your-moodle.com --username admin --password yourpass

# Run with browser UI visible (for debugging)
./run_e2e_tests.sh --headed --url http://localhost
```

### 2. Manual Setup

```bash
# Create virtual environment
python3 -m venv venv_e2e
source venv_e2e/bin/activate

# Install dependencies
pip install -r requirements-e2e.txt

# Install Playwright browsers
playwright install chromium

# Run tests
python tests/e2e/test_e2e_moodle_claude.py --url http://localhost --username admin --password yourpass
```

## Configuration

### Environment Variables

```bash
export MOODLE_URL="http://localhost"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="password"
export HEADLESS="true"
export CATEGORY_ID="1"
export TIMEOUT="30000"
export BROWSER="chromium"
```

### Test Configuration Class

Modify the `TestConfig` class in `tests/e2e/test_e2e_moodle_claude.py`:

```python
@dataclass
class TestConfig:
    moodle_url: str = "http://your-moodle.com"
    admin_username: str = "your-admin"
    admin_password: str = "your-password"
    test_course_category: int = 1
    default_timeout: int = 30000
    test_data_dir: str = "./test_data"
```

## Test Structure

### Test Classes

1. **TestSectionManagement**
   - `test_create_new_section()`: Creates new course sections
   - `test_edit_section_name()`: Tests inline section editing
   - `test_bulk_section_operations()`: Validates bulk operations
   - `test_section_availability_conditions()`: Tests access restrictions

2. **TestFileUpload**
   - `test_file_resource_creation()`: Creates file resources with uploads
   - `test_file_picker_repositories()`: Tests different file repositories
   - `test_drag_drop_file_upload()`: Validates drag-and-drop functionality

3. **TestMoodleClaudeIntegration**
   - `test_course_creation_from_chat_simulation()`: Simulates Claude course creation
   - `test_bulk_course_management()`: Tests comprehensive course management

4. **TestAccessibilityAndUsability**
   - `test_keyboard_navigation()`: Validates keyboard accessibility
   - `test_screen_reader_compatibility()`: Tests screen reader features

### Test Data Factory

The `TestDataFactory` class provides reusable test data:

```python
# Create test course data
course_data = TestDataFactory.create_course_data("My Test Course")

# Create section data
sections = TestDataFactory.create_section_data("Chapter")

# Create file data
files = TestDataFactory.create_file_data()
```

## Running Tests

### Command Line Options

```bash
# Basic usage
python tests/e2e/test_e2e_moodle_claude.py [options]

# Options:
--url URL              Moodle URL
--username USER        Admin username  
--password PASS        Admin password
--category ID          Course category ID
--timeout MS           Timeout in milliseconds
--headless             Run headless (default)
--report FILE          HTML report output file
```

### Shell Script Options

```bash
# run_e2e_tests.sh options:
-u, --url URL          Moodle URL
-n, --username USER    Admin username
-p, --password PASS    Admin password
-c, --category ID      Course category ID
-t, --timeout MS       Timeout in milliseconds
-b, --browser BROWSER  Browser (chromium, firefox, webkit)
--headless             Run headless (default)
--headed               Show browser UI
--setup-only           Only setup environment
--clean                Clean previous artifacts
```

### Pytest Integration

```bash
# Run with pytest
pytest tests/e2e/test_e2e_moodle_claude.py -v

# Run specific test class
pytest tests/e2e/test_e2e_moodle_claude.py::TestSectionManagementPytest -v

# Run with markers
pytest -m "section_management" -v

# Parallel execution
pytest tests/e2e/test_e2e_moodle_claude.py -n 4  # 4 parallel workers
```

## Test Reports

### Generated Reports

After test execution, reports are generated in the `reports/` directory:

1. **HTML Report**: `e2e_report.html` - Comprehensive visual report
2. **JSON Report**: `e2e_report.json` - Machine-readable results
3. **Comprehensive Report**: `comprehensive_report.html` - Detailed analysis

### Report Features

- ✅ **Test Results**: Pass/fail status for each test
- ⏱️ **Timing Information**: Execution duration per test
- 📊 **Summary Statistics**: Success rates and metrics
- 🐛 **Error Details**: Stack traces and failure information
- 📸 **Screenshots**: Captured on test failures (when enabled)

## Debugging

### Debug Mode

```bash
# Run with browser UI visible
./run_e2e_tests.sh --headed

# Debug specific test
python -m pytest tests/e2e/test_e2e_moodle_claude.py::TestSectionManagement::test_create_new_section -v -s
```

### Browser Developer Tools

```python
# Add debugging breakpoints in test code
async def test_debug_example(self):
    await self.page.goto(f"{self.config.moodle_url}/course/view.php?id={course_id}")
    
    # Pause for manual inspection
    await self.page.pause()  # Opens browser dev tools
    
    # Take screenshot
    await self.page.screenshot(path="debug_screenshot.png")
```

### Logging

Enable detailed logging by setting environment variables:

```bash
export PYTHONPATH="."
export LOG_LEVEL="DEBUG"
python tests/e2e/test_e2e_moodle_claude.py --url http://localhost
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    
    services:
      moodle:
        image: moodlehq/moodle-php-apache:latest
        ports:
          - 80:80
        env:
          MOODLE_DATABASE_TYPE: mariadb
          MOODLE_DATABASE_HOST: db
          MOODLE_DATABASE_NAME: moodle
          MOODLE_DATABASE_USER: moodle
          MOODLE_DATABASE_PASSWORD: password
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements-e2e.txt
        playwright install chromium
    
    - name: Run E2E tests
      run: |
        python tests/e2e/test_e2e_moodle_claude.py \
          --url http://localhost \
          --username admin \
          --password admin \
          --headless
    
    - name: Upload test reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: e2e-reports
        path: reports/
```

## Troubleshooting

### Common Issues

#### 1. Browser Installation Issues

```bash
# Reinstall browsers
playwright install --force chromium

# Check installation
playwright --version
```

#### 2. Moodle Connection Issues

```bash
# Test connectivity
curl -I http://your-moodle-url

# Check credentials by logging in manually
```

#### 3. Timeout Issues

```bash
# Increase timeout for slow systems
python test_e2e_moodle_claude.py --timeout 60000  # 60 seconds
```

#### 4. Permission Issues

Ensure the admin user has appropriate capabilities:
- `moodle/course:create`
- `moodle/course:manageactivities`
- `moodle/site:uploadusers`
- `webservice/rest:use`

### Debug Checklist

- [ ] Moodle instance is running and accessible
- [ ] Admin credentials are correct
- [ ] Web services are enabled in Moodle
- [ ] Required Moodle plugins are installed
- [ ] Python dependencies are installed
- [ ] Playwright browsers are installed
- [ ] File permissions are correct
- [ ] Network connectivity is available

## Performance Considerations

### Test Optimization

1. **Parallel Execution**: Use pytest-xdist for parallel test runs
2. **Browser Reuse**: Configure browser context reuse where possible
3. **Test Data Cleanup**: Implement proper cleanup to avoid test data accumulation
4. **Selective Testing**: Use pytest markers to run specific test subsets

### Resource Management

```python
# Example of efficient resource management
class OptimizedTestBase(MoodleE2ETestBase):
    @classmethod
    async def setup_class(cls):
        """Setup shared resources once per test class"""
        await cls.setup_browser()
        await cls.login_as_admin()
    
    @classmethod  
    async def teardown_class(cls):
        """Cleanup shared resources"""
        await cls.teardown_browser()
```

## Extending Tests

### Adding New Test Cases

1. **Create Test Method**:
   ```python
   async def test_new_functionality(self):
       """Test description"""
       # Test implementation
       pass
   ```

2. **Add to Test Class**:
   ```python
   class TestNewFeature(MoodleE2ETestBase):
       async def test_feature_a(self):
           pass
       async def test_feature_b(self):
           pass
   ```

3. **Update Test Runner**:
   ```python
   test_categories = [
       # ... existing categories
       ("New Feature", TestNewFeature)
   ]
   ```

### Custom Assertions

```python
async def assert_section_exists(self, section_name: str):
    """Custom assertion for section existence"""
    section = self.page.locator(f'.section:has-text("{section_name}")')
    assert await section.count() > 0, f"Section '{section_name}' not found"
```

## Best Practices

### Test Design

1. **Independence**: Each test should be independent and not rely on others
2. **Cleanup**: Always clean up test data (courses, sections, files)
3. **Assertions**: Use meaningful assertions with clear error messages
4. **Wait Strategies**: Use explicit waits instead of fixed sleeps
5. **Page Objects**: Consider using page object pattern for complex UI interactions

### Maintenance

1. **Regular Updates**: Keep browser versions and dependencies updated
2. **Selector Robustness**: Use stable selectors that won't break with UI changes
3. **Test Data**: Use dynamic test data to avoid conflicts
4. **Error Handling**: Implement proper error handling and recovery

### Documentation

1. **Test Descriptions**: Write clear test method docstrings
2. **Comments**: Add comments for complex test logic
3. **README Updates**: Keep documentation current with test changes

## Support

For issues or questions:

1. **Check Logs**: Review test output and generated reports
2. **GitHub Issues**: Report bugs or feature requests
3. **Documentation**: Refer to Moodle and Playwright documentation
4. **Community**: Ask questions in relevant forums

---

**Last Updated**: 2024-01-XX  
**Version**: 1.0.0
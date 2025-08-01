# 🧪 MoodleClaude Testing Guide - Complete Reference

## 🎯 Quick Start

### Automated Test Runners
```bash
# Run all tests with comprehensive reporting
./scripts/run_tests.sh all -v -c --html

# Quick development testing
make test-unit                    # Fast unit tests
make test-integration            # API integration tests
./scripts/run_e2e_tests.sh       # Browser automation tests

# Manual testing scripts
uv run python test_realistic_moodle.py      # Basic functionality
uv run python test_enhanced_moodle.py       # Advanced features
uv run python test_wsmanage_correct.py      # Section management
```

## 📊 Test Categories

### 🧪 Unit Tests - Fast & Isolated
**Test individual components without external dependencies**

```bash
# Run unit tests
uv run pytest tests/unit/ -v
make test-unit
```

**What's Tested:**
- ✅ Content parsing logic (chat → educational content)
- ✅ Configuration validation (environment variables)
- ✅ Data models and serialization
- ✅ Utility functions and formatters
- ✅ Error handling and edge cases

**Key Test Files:**
- `test_config.py` - Configuration management
- `test_content_parser_fixed.py` - Content extraction logic

### 🔗 Integration Tests - Component Interactions
**Test API integrations and component connections**

```bash
# Run integration tests
uv run pytest tests/integration/ -v
make test-integration
```

**What's Tested:**
- ✅ Moodle web services API calls
- ✅ Authentication and token handling
- ✅ Section management operations
- ✅ Error scenarios and recovery
- ✅ Database interactions

**Key Test Files:**
- `test_enhanced_moodle_claude.py` - Full API integration

### 🌐 End-to-End Tests - Complete Workflows
**Test full user workflows with browser automation**

```bash
# Run E2E tests
./scripts/run_e2e_tests.sh
make test-e2e
uv run pytest tests/e2e/ -v
```

**What's Tested:**
- ✅ Complete course creation workflow
- ✅ Browser-based Moodle interactions
- ✅ User interface validation
- ✅ Accessibility compliance
- ✅ Real-world usage scenarios

**Key Test Files:**
- `test_e2e_moodle_claude.py` - Browser automation tests

## 🔍 Manual Testing Scripts

### Core Functionality Tests

**1. Moodle Connection Test**
```bash
uv run python test_direct_moodle.py
```
Expected output:
```
✅ Site: MoodleClaude Test Environment
✅ Course created with ID: X
✅ ALL TESTS PASSED!
```

**2. MCP Server Test**
```bash
uv run python test_mcp_connection.py
```
Expected output:
```
✅ Content parsing: READY
✅ Course creation: READY
✅ Moodle connection: CONFIGURED
```

**3. Enhanced Features Test**
```bash
uv run python test_enhanced_moodle.py
```
Expected output:
```
✅ Created 'Python Basics' section: 2
✅ Created 'Advanced Topics' section: 3
✅ Enhanced course structure working
```

**4. Section Management Test**
```bash
uv run python test_wsmanage_correct.py
```
Expected output:
```
✅ SUCCESS! Created section: [{'sectionid': X, 'sectionnumber': Y}]
✅ Now has N sections
```

**5. Available Functions Check**
```bash
uv run python check_available_functions.py
```
Expected output:
```
✅ Available: 10+ functions
✅ core_course_create_courses
✅ local_wsmanagesections_create_sections
```

### Environment Setup Tests

**1. Fresh Installation Test**
```bash
# Complete environment reset and test
docker-compose down
docker volume rm $(docker volume ls | grep moodle | awk '{print $2}') 2>/dev/null
docker-compose up -d
./scripts/setup_webservice_functions_docker.sh
uv run python test_realistic_moodle.py
```

**2. Web Services Configuration Test**
```bash
# Test token and permissions
curl -s "http://localhost:8080/webservice/rest/server.php" \
  -d "wstoken=$(grep MOODLE_TOKEN .env | cut -d= -f2)&wsfunction=core_webservice_get_site_info&moodlewsrestformat=json" \
  | jq .
```

**3. Database State Check**
```bash
# Verify database configuration
docker exec -it moodleclaude_db mysql -u bn_moodle bitnami_moodle \
  -e "SELECT id, fullname FROM mdl_course ORDER BY id DESC LIMIT 5;"
```

## 🚀 Performance & Load Testing

### Response Time Testing
```bash
# Time API operations
time uv run python test_direct_moodle.py

# Measure section creation performance
time uv run python test_wsmanage_correct.py
```

### Load Testing
```bash
# Create multiple courses simultaneously
for i in {1..5}; do
    echo "Creating course $i..."
    uv run python -c "
import asyncio
from test_realistic_moodle import test_realistic_moodle
asyncio.run(test_realistic_moodle())
" &
done
wait
```

### Memory Usage Monitoring
```bash
# Monitor MCP server memory usage
top -pid $(pgrep -f "python.*mcp_server")

# Check Docker container resources
docker stats moodleclaude_app
```

## 🐛 Debugging & Troubleshooting

### Verbose Testing
```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG
uv run python mcp_server.py

# Run tests with maximum verbosity
uv run pytest tests/ -v -s --tb=long
```

### Network Debugging
```bash
# Test raw Moodle API
curl -v "http://localhost:8080/webservice/rest/server.php" \
  -d "wstoken=YOUR_TOKEN&wsfunction=core_webservice_get_site_info&moodlewsrestformat=json"

# Check container connectivity
docker exec moodleclaude_app curl -I http://mariadb:3306
```

### Common Issue Resolution

**1. Token Issues**
```bash
# Regenerate token via web interface
# Update .env file
# Restart MCP server
kill $(pgrep -f "python.*mcp_server")
uv run python mcp_server.py &
```

**2. Docker Issues**
```bash
# Reset Docker environment
docker-compose down
docker system prune -f
docker-compose up -d
```

**3. Python Dependencies**
```bash
# Reinstall dependencies
uv sync --reinstall
```

**4. Browser Issues (E2E)**
```bash
# Reinstall browsers
playwright install --force chromium
```

## 📊 Test Reports & Coverage

### Generate Reports
```bash
# HTML test report
uv run pytest tests/ --html=reports/test_report.html --self-contained-html

# Coverage report
uv run pytest tests/ --cov=. --cov-report=html --cov-report=term

# E2E specific report
./scripts/run_e2e_tests.sh --html-report
```

### View Reports
```bash
# Open generated reports
open reports/test_report.html      # General test results
open htmlcov/index.html           # Coverage report
open reports/e2e_report.html      # E2E test results
```

## 🎯 Test Scenarios & Workflows

### Complete Integration Test
```bash
# 1. Environment setup
docker-compose up -d
./scripts/setup_webservice_functions_docker.sh

# 2. Basic functionality
uv run python test_direct_moodle.py

# 3. Advanced features
uv run python test_enhanced_moodle.py

# 4. MCP integration
uv run python mcp_server.py &
uv run python test_mcp_connection.py

# 5. E2E workflow
./scripts/run_e2e_tests.sh
```

### Development Workflow
```bash
# Quick feedback during development
make test-unit

# Integration check before commit
make test-integration

# Full validation before release
make test-coverage
./scripts/run_e2e_tests.sh
```

### CI/CD Pipeline Simulation
```bash
# Stage 1: Fast feedback
./scripts/run_tests.sh unit -v

# Stage 2: Integration validation
./scripts/run_tests.sh integration -v

# Stage 3: E2E validation
./scripts/run_e2e_tests.sh --headless
```

## 🎉 Success Criteria

### Automated Tests
- ✅ **Unit Tests**: 95%+ pass rate, <2 seconds execution
- ✅ **Integration Tests**: All core functions work, <30 seconds execution
- ✅ **E2E Tests**: Complete workflows succeed, <5 minutes execution

### Manual Tests
- ✅ **Moodle Connection**: API calls return expected data
- ✅ **Course Creation**: Courses appear in Moodle with correct structure
- ✅ **Section Management**: Sections created and positioned correctly
- ✅ **MCP Integration**: Tools available and responsive in Claude Desktop

### Performance Benchmarks
- ✅ **Course Creation**: <5 seconds per course
- ✅ **Section Operations**: <2 seconds per section
- ✅ **API Response**: <1 second for most operations
- ✅ **Memory Usage**: <100MB for MCP server

### Quality Indicators
- ✅ **Error Handling**: Graceful failure and recovery
- ✅ **Documentation**: Tests pass with documented parameters
- ✅ **Reliability**: Consistent results across multiple runs
- ✅ **Maintainability**: Tests are readable and well-organized

## 🔧 Test Environment Configuration

### Required Environment Variables
```bash
# Core configuration
MOODLE_URL=http://localhost:8080
MOODLE_TOKEN=your_32_character_token
MOODLE_USERNAME=simon

# Test-specific settings
LOG_LEVEL=INFO
HEADLESS=true
BROWSER=chromium

# Optional performance settings
API_TIMEOUT=30
MAX_CONCURRENT_TESTS=5
```

### Docker Test Setup
```bash
# Ensure test environment is ready
docker-compose ps | grep healthy
docker exec moodleclaude_app curl -s http://localhost:8080/admin | grep -q "Administration"
```

---

**Complete testing coverage ensures MoodleClaude is reliable, performant, and ready for production use!** 🧪✨

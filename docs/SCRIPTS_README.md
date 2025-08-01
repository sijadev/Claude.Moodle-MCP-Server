# MoodleClaude Scripts

This folder contains all the shell scripts for the MoodleClaude project.

## 📋 Script Index

### Testing Scripts
- **[run_tests.sh](./run_tests.sh)** - Run unit and integration tests with coverage
- **[run_e2e_tests.sh](./run_e2e_tests.sh)** - Run end-to-end tests with browser automation

### Setup Scripts
- **[setup_webservice_functions.sh](./setup_webservice_functions.sh)** - Configure Moodle web services and functions

## 🚀 Usage

### Testing
```bash
# Run all tests with coverage
./scripts/run_tests.sh

# Run tests with HTML report
./scripts/run_tests.sh --html

# Run e2e tests
./scripts/run_e2e_tests.sh

# Run e2e tests with specific browser
./scripts/run_e2e_tests.sh --browser firefox
```

### Setup
```bash
# Setup Moodle web services
./scripts/setup_webservice_functions.sh
```

## 📝 Script Details

### run_tests.sh
**Purpose**: Execute unit and integration tests with comprehensive reporting

**Features**:
- Coverage reporting (HTML and terminal)
- JUnit XML output for CI/CD
- Parallel test execution support
- Optional HTML test reports
- Environment validation

**Usage**:
```bash
./scripts/run_tests.sh [--html] [--coverage] [--parallel]
```

### run_e2e_tests.sh
**Purpose**: Execute end-to-end tests using Playwright browser automation

**Features**:
- Multi-browser support (Chromium, Firefox, Safari)
- Headless and headed mode options
- Test reporting and screenshots
- Configurable Moodle URL and credentials
- Retry mechanism for flaky tests

**Usage**:
```bash
./scripts/run_e2e_tests.sh [--browser BROWSER] [--headed] [--url URL]
```

**Environment Variables**:
- `MOODLE_URL` - Moodle instance URL
- `MOODLE_USERNAME` - Test user credentials
- `MOODLE_PASSWORD` - Test user password

### setup_webservice_functions.sh
**Purpose**: Configure Moodle web services and enable required functions

**Features**:
- Database connection validation
- Web service enablement
- Function capability setup
- Token generation assistance
- Configuration verification

**Prerequisites**:
- MySQL/MariaDB access to Moodle database
- Moodle admin credentials
- Direct database access permissions

**Usage**:
```bash
./scripts/setup_webservice_functions.sh
```

**Environment Variables**:
- `MOODLE_DB_HOST` - Database host (default: localhost)
- `MOODLE_DB_USER` - Database username
- `MOODLE_DB_PASS` - Database password
- `MOODLE_DB_NAME` - Database name
- `MOODLE_URL` - Moodle site URL

## 🔧 Permissions

Make sure scripts are executable:
```bash
chmod +x scripts/*.sh
```

## 🔗 Related Documentation

See the [readme/](../readme/) folder for detailed documentation:
- [TESTING_GUIDE.md](../readme/TESTING_GUIDE.md) - Comprehensive testing procedures
- [E2E_TESTING.md](../readme/E2E_TESTING.md) - End-to-end testing setup
- [MOODLE_SETUP.md](../readme/MOODLE_SETUP.md) - Moodle environment configuration

---

*Last updated: July 29, 2025*

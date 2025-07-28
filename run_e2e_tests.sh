#!/bin/bash

# MoodleClaude E2E Test Runner Script
# This script sets up the environment and runs end-to-end tests

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_DIR="$PROJECT_ROOT/venv_e2e"
REPORTS_DIR="$PROJECT_ROOT/reports"

# Default values
MOODLE_URL="http://localhost"
ADMIN_USERNAME="simon"
ADMIN_PASSWORD="Pwd1234!"
HEADLESS="true"
CATEGORY_ID="1"
TIMEOUT="30000"
BROWSER="chromium"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [options]

Options:
    -u, --url URL           Moodle URL (default: http://localhost)
    -n, --username USER     Admin username (default: simon)
    -p, --password PASS     Admin password (default: Pwd1234!)
    -c, --category ID       Course category ID (default: 1)
    -t, --timeout MS        Timeout in milliseconds (default: 30000)
    -b, --browser BROWSER   Browser to use (default: chromium)
    --headless              Run in headless mode (default)
    --headed                Run with browser UI visible
    --setup-only            Only setup environment, don't run tests
    --clean                 Clean up previous test artifacts
    --help                  Show this help message

Examples:
    $0                                          # Run with default settings
    $0 --url http://moodle.local --headed       # Run against local Moodle with UI
    $0 --setup-only                            # Only setup the environment
    $0 --clean                                 # Clean up and exit

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)
            MOODLE_URL="$2"
            shift 2
            ;;
        -n|--username)
            ADMIN_USERNAME="$2"
            shift 2
            ;;
        -p|--password)
            ADMIN_PASSWORD="$2"
            shift 2
            ;;
        -c|--category)
            CATEGORY_ID="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -b|--browser)
            BROWSER="$2"
            shift 2
            ;;
        --headless)
            HEADLESS="true"
            shift
            ;;
        --headed)
            HEADLESS="false"
            shift
            ;;
        --setup-only)
            SETUP_ONLY="true"
            shift
            ;;
        --clean)
            CLEAN_ONLY="true"
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Function to clean up previous test artifacts
cleanup_previous_runs() {
    print_status "Cleaning up previous test artifacts..."
    
    # Remove old reports
    if [ -d "$REPORTS_DIR" ]; then
        rm -rf "$REPORTS_DIR"
        print_status "Removed old reports directory"
    fi
    
    # Remove test data directory
    if [ -d "$PROJECT_ROOT/test_data" ]; then
        rm -rf "$PROJECT_ROOT/test_data"
        print_status "Removed old test data"
    fi
    
    # Remove pytest cache
    if [ -d "$PROJECT_ROOT/.pytest_cache" ]; then
        rm -rf "$PROJECT_ROOT/.pytest_cache"
        print_status "Removed pytest cache"
    fi
    
    # Remove __pycache__ directories
    find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Function to setup Python virtual environment
setup_virtual_environment() {
    print_status "Setting up Python virtual environment..."
    
    # Check if Python 3.8+ is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_status "Found Python version: $PYTHON_VERSION"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Virtual environment ready"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing E2E test dependencies..."
    
    # Install requirements
    if [ -f "$PROJECT_ROOT/requirements-e2e.txt" ]; then
        pip install -r "$PROJECT_ROOT/requirements-e2e.txt"
    else
        print_warning "requirements-e2e.txt not found, installing basic dependencies"
        pip install pytest pytest-asyncio playwright pytest-html
    fi
    
    # Install Playwright browsers
    print_status "Installing Playwright browsers..."
    playwright install "$BROWSER"
    
    print_success "Dependencies installed"
}

# Function to verify Moodle connectivity
verify_moodle_connectivity() {
    print_status "Verifying Moodle connectivity..."
    
    # Simple connectivity check
    if command -v curl &> /dev/null; then
        if curl -s --head "$MOODLE_URL" | head -n 1 | grep -q "200 OK"; then
            print_success "Moodle is accessible at $MOODLE_URL"
        else
            print_warning "Could not verify Moodle connectivity (this may be normal)"
        fi
    else
        print_warning "curl not available, skipping connectivity check"
    fi
}

# Function to create reports directory
setup_reports_directory() {
    print_status "Setting up reports directory..."
    mkdir -p "$REPORTS_DIR"
    print_success "Reports directory created: $REPORTS_DIR"
}

# Function to run E2E tests
run_e2e_tests() {
    print_status "Running E2E tests..."
    
    # Set environment variables
    export MOODLE_URL="$MOODLE_URL"
    export ADMIN_USERNAME="$ADMIN_USERNAME"
    export ADMIN_PASSWORD="$ADMIN_PASSWORD"
    export HEADLESS="$HEADLESS"
    export CATEGORY_ID="$CATEGORY_ID"
    export TIMEOUT="$TIMEOUT"
    export BROWSER="$BROWSER"
    
    # Create pytest arguments
    PYTEST_ARGS=(
        "tests/e2e/test_e2e_moodle_claude.py"
        "-v"
        "--tb=short"
        "--html=$REPORTS_DIR/e2e_report.html"
        "--self-contained-html"
        "--json-report"
        "--json-report-file=$REPORTS_DIR/e2e_report.json"
    )
    
    # Add browser-specific arguments
    if [ "$HEADLESS" = "true" ]; then
        PYTEST_ARGS+=("--browser-arg=--headless")
    fi
    
    # Run tests
    cd "$PROJECT_ROOT"
    
    print_status "Starting test execution..."
    print_status "Moodle URL: $MOODLE_URL"
    print_status "Admin Username: $ADMIN_USERNAME"
    print_status "Headless Mode: $HEADLESS"
    print_status "Browser: $BROWSER"
    print_status "Timeout: ${TIMEOUT}ms"
    
    echo "========================================================================================"
    
    if python -m pytest "${PYTEST_ARGS[@]}"; then
        print_success "All E2E tests passed!"
        TEST_SUCCESS=true
    else
        print_error "Some E2E tests failed"
        TEST_SUCCESS=false
    fi
    
    echo "========================================================================================"
    
    # Generate additional reports if the Python script has that functionality
    if [ -f "tests/e2e/test_e2e_moodle_claude.py" ]; then
        print_status "Generating additional reports..."
        python tests/e2e/test_e2e_moodle_claude.py \
            --url "$MOODLE_URL" \
            --username "$ADMIN_USERNAME" \
            --password "$ADMIN_PASSWORD" \
            --category "$CATEGORY_ID" \
            --timeout "$TIMEOUT" \
            --report "$REPORTS_DIR/comprehensive_report.html" \
            --headless > /dev/null 2>&1 || true
    fi
    
    print_status "Test reports generated in: $REPORTS_DIR"
    
    # List generated reports
    if [ -d "$REPORTS_DIR" ]; then
        print_status "Generated reports:"
        ls -la "$REPORTS_DIR"
    fi
    
    return $([[ "$TEST_SUCCESS" == "true" ]] && echo 0 || echo 1)
}

# Main execution
main() {
    print_status "Starting MoodleClaude E2E Test Runner"
    print_status "Project Root: $PROJECT_ROOT"
    
    # Clean up if requested
    if [ "$CLEAN_ONLY" = "true" ]; then
        cleanup_previous_runs
        print_success "Cleanup completed"
        exit 0
    fi
    
    # Setup phase
    cleanup_previous_runs
    setup_virtual_environment
    install_dependencies
    setup_reports_directory
    verify_moodle_connectivity
    
    # Exit if setup-only requested
    if [ "$SETUP_ONLY" = "true" ]; then
        print_success "Environment setup completed"
        print_status "To run tests manually:"
        print_status "  source $VENV_DIR/bin/activate"
        print_status "  python tests/e2e/test_e2e_moodle_claude.py --url $MOODLE_URL"
        exit 0
    fi
    
    # Run tests
    if run_e2e_tests; then
        print_success "E2E test execution completed successfully"
        exit 0
    else
        print_error "E2E test execution failed"
        exit 1
    fi
}

# Trap errors and cleanup
trap 'print_error "Script failed at line $LINENO"' ERR

# Run main function
main "$@"
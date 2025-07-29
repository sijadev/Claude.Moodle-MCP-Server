#!/bin/bash

# MoodleClaude Comprehensive Test Runner
# Runs unit, integration, and E2E tests

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
REPORTS_DIR="$PROJECT_ROOT/reports"

# Default values
TEST_TYPE="all"
VERBOSE=false
COVERAGE=false
HTML_REPORT=false
PARALLEL=false
FAIL_FAST=false

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

print_header() {
    echo -e "${PURPLE}[HEADER]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [options]

Test Types:
    unit              Run only unit tests
    integration       Run only integration tests  
    e2e               Run only end-to-end tests
    all               Run all tests (default)

Options:
    -v, --verbose     Verbose output
    -c, --coverage    Generate coverage report
    -h, --html        Generate HTML report
    -p, --parallel    Run tests in parallel
    -f, --fail-fast   Stop on first failure
    --clean           Clean previous reports and cache
    --setup           Setup test environment
    --help            Show this help message

Examples:
    $0                          # Run all tests
    $0 unit -v                  # Run unit tests with verbose output
    $0 integration -c           # Run integration tests with coverage
    $0 e2e --html              # Run E2E tests and generate HTML report
    $0 all -v -c --html        # Run all tests with all options

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        unit|integration|e2e|all)
            TEST_TYPE="$1"
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -h|--html)
            HTML_REPORT=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -f|--fail-fast)
            FAIL_FAST=true
            shift
            ;;
        --clean)
            CLEAN_ONLY=true
            shift
            ;;
        --setup)
            SETUP_ONLY=true
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
    fi
    
    # Remove pytest cache
    find "$PROJECT_ROOT" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    
    # Remove __pycache__ directories
    find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # Remove coverage files
    find "$PROJECT_ROOT" -name ".coverage*" -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Function to setup test environment
setup_test_environment() {
    print_status "Setting up test environment..."
    
    # Create reports directory
    mkdir -p "$REPORTS_DIR"
    
    # Check if pytest is installed
    if ! python3 -c "import pytest" &> /dev/null; then
        print_error "pytest is not installed. Please install with: pip3 install pytest"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_status "Python version: $PYTHON_VERSION"
    
    # Install basic test dependencies if not present
    if ! python3 -c "import pytest_cov" &> /dev/null && [ "$COVERAGE" = true ]; then
        print_warning "pytest-cov not found, installing..."
        pip3 install pytest-cov
    fi
    
    if ! python3 -c "import pytest_html" &> /dev/null && [ "$HTML_REPORT" = true ]; then
        print_warning "pytest-html not found, installing..."
        pip3 install pytest-html
    fi
    
    if ! python3 -c "import pytest_xdist" &> /dev/null && [ "$PARALLEL" = true ]; then
        print_warning "pytest-xdist not found, installing..."
        pip3 install pytest-xdist
    fi
    
    print_success "Test environment ready"
}

# Function to build pytest arguments
build_pytest_args() {
    local test_path="$1"
    local args=()
    
    # Base arguments
    args+=("$test_path")
    
    # Verbose output
    if [ "$VERBOSE" = true ]; then
        args+=("-v")
    fi
    
    # Fail fast
    if [ "$FAIL_FAST" = true ]; then
        args+=("-x")
    fi
    
    # Coverage
    if [ "$COVERAGE" = true ]; then
        args+=("--cov=.")
        args+=("--cov-report=term-missing")
        args+=("--cov-report=html:$REPORTS_DIR/htmlcov")
    fi
    
    # HTML report
    if [ "$HTML_REPORT" = true ]; then
        args+=("--html=$REPORTS_DIR/report.html")
        args+=("--self-contained-html")
    fi
    
    # Parallel execution
    if [ "$PARALLEL" = true ]; then
        args+=("-n" "auto")
    fi
    
    # JUnit XML for CI
    args+=("--junitxml=$REPORTS_DIR/junit.xml")
    
    echo "${args[@]}"
}

# Function to run unit tests
run_unit_tests() {
    print_header "Running Unit Tests"
    print_status "Testing individual components and functions..."
    
    local pytest_args=($(build_pytest_args "tests/unit/"))
    
    cd "$PROJECT_ROOT"
    if python3 -m pytest "${pytest_args[@]}"; then
        print_success "Unit tests passed!"
        return 0
    else
        print_error "Unit tests failed!"
        return 1
    fi
}

# Function to run integration tests  
run_integration_tests() {
    print_header "Running Integration Tests"
    print_status "Testing component interactions and API integrations..."
    
    local pytest_args=($(build_pytest_args "tests/integration/"))
    
    cd "$PROJECT_ROOT"
    if python3 -m pytest "${pytest_args[@]}"; then
        print_success "Integration tests passed!"
        return 0
    else
        print_error "Integration tests failed!"
        return 1
    fi
}

# Function to run E2E tests
run_e2e_tests() {
    print_header "Running End-to-End Tests"
    print_status "Testing complete user workflows with browser automation..."
    
    # Check if playwright is available
    if ! command -v playwright &> /dev/null; then
        print_warning "Playwright not found. Installing..."
        pip3 install playwright
        playwright install chromium
    fi
    
    # Use the dedicated E2E script if available
    if [ -f "$PROJECT_ROOT/run_e2e_tests.sh" ]; then
        print_status "Using dedicated E2E test runner..."
        if [ "$HTML_REPORT" = true ]; then
            "$PROJECT_ROOT/run_e2e_tests.sh" --report "$REPORTS_DIR/e2e_report.html"
        else
            "$PROJECT_ROOT/run_e2e_tests.sh"
        fi
        return $?
    else
        # Fallback to pytest
        local pytest_args=($(build_pytest_args "tests/e2e/"))
        
        cd "$PROJECT_ROOT" 
        if python3 -m pytest "${pytest_args[@]}"; then
            print_success "E2E tests passed!" 
            return 0
        else
            print_error "E2E tests failed!"
            return 1
        fi
    fi
}

# Function to run all tests
run_all_tests() {
    print_header "Running Complete Test Suite"
    
    local unit_result=0
    local integration_result=0
    local e2e_result=0
    
    # Run unit tests
    if ! run_unit_tests; then
        unit_result=1
        if [ "$FAIL_FAST" = true ]; then
            return 1
        fi
    fi
    
    # Run integration tests
    if ! run_integration_tests; then
        integration_result=1
        if [ "$FAIL_FAST" = true ]; then
            return 1
        fi
    fi
    
    # Run E2E tests
    if ! run_e2e_tests; then
        e2e_result=1
        if [ "$FAIL_FAST" = true ]; then
            return 1
        fi
    fi
    
    # Summary
    echo ""
    print_header "Test Suite Summary"
    echo "=================================="
    
    if [ $unit_result -eq 0 ]; then
        print_success "✅ Unit Tests: PASSED"
    else
        print_error "❌ Unit Tests: FAILED"
    fi
    
    if [ $integration_result -eq 0 ]; then
        print_success "✅ Integration Tests: PASSED"
    else
        print_error "❌ Integration Tests: FAILED"
    fi
    
    if [ $e2e_result -eq 0 ]; then
        print_success "✅ E2E Tests: PASSED"
    else
        print_error "❌ E2E Tests: FAILED"
    fi
    
    echo "=================================="
    
    local total_failures=$((unit_result + integration_result + e2e_result))
    if [ $total_failures -eq 0 ]; then
        print_success "🎉 All tests passed!"
        return 0
    else
        print_error "💥 $total_failures test suite(s) failed"
        return 1
    fi
}

# Function to generate summary report
generate_summary_report() {
    if [ -d "$REPORTS_DIR" ]; then
        print_status "Test reports generated in: $REPORTS_DIR"
        
        echo ""
        print_status "Generated files:"
        ls -la "$REPORTS_DIR" 2>/dev/null || print_warning "No report files found"
        
        # Show coverage summary if available
        if [ -f "$REPORTS_DIR/htmlcov/index.html" ]; then
            print_status "Coverage report: $REPORTS_DIR/htmlcov/index.html"
        fi
        
        # Show HTML report if available
        if [ -f "$REPORTS_DIR/report.html" ]; then
            print_status "HTML test report: $REPORTS_DIR/report.html"
        fi
        
        # Show E2E report if available
        if [ -f "$REPORTS_DIR/e2e_report.html" ]; then
            print_status "E2E test report: $REPORTS_DIR/e2e_report.html"
        fi
    fi
}

# Main execution
main() {
    print_header "MoodleClaude Test Runner"
    print_status "Test Type: $TEST_TYPE"
    print_status "Project Root: $PROJECT_ROOT"
    
    # Clean up if requested
    if [ "$CLEAN_ONLY" = true ]; then
        cleanup_previous_runs
        print_success "Cleanup completed"
        exit 0
    fi
    
    # Setup phase
    cleanup_previous_runs
    setup_test_environment
    
    # Exit if setup-only requested
    if [ "$SETUP_ONLY" = true ]; then
        print_success "Test environment setup completed"
        exit 0
    fi
    
    # Run tests based on type
    local test_result=0
    
    case $TEST_TYPE in
        unit)
            run_unit_tests || test_result=1
            ;;
        integration)
            run_integration_tests || test_result=1
            ;;
        e2e)
            run_e2e_tests || test_result=1
            ;;
        all)
            run_all_tests || test_result=1
            ;;
        *)
            print_error "Unknown test type: $TEST_TYPE"
            show_usage
            exit 1
            ;;
    esac
    
    # Generate summary report
    generate_summary_report
    
    # Exit with appropriate code
    if [ $test_result -eq 0 ]; then
        print_success "Test execution completed successfully! 🎉"
        exit 0
    else
        print_error "Test execution failed! 💥"
        exit 1
    fi
}

# Trap errors and cleanup
trap 'print_error "Script failed at line $LINENO"' ERR

# Run main function
main "$@"
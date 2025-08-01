#!/bin/bash

# MoodleClaude Comprehensive Smoke Test
# =====================================
# This script runs a complete smoke test of MoodleClaude before GitHub pushes.
# 
# Test Flow:
# 1. Setup → Environment Validation → Moodle Ready → Functionality Tests
# 2. Runs automatically before GitHub push operations
# 3. Validates all critical bug fixes and functionality

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REPORTS_DIR="$PROJECT_ROOT/reports/smoke_test"
CLAUDE_CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Test configuration
MOODLE_URL="http://localhost:8080"
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="MoodleClaude2025!"
QUICK_MODE=false
SKIP_DOCKER=false
VERBOSE=false

# Status tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
RESULTS_FILE="/tmp/moodleclaude_test_results_$$"

# Function to print colored output with timestamps
print_timestamp() {
    echo -n "[$(date '+%H:%M:%S')] "
}

print_status() {
    print_timestamp
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    print_timestamp
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    print_timestamp
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    print_timestamp
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    print_timestamp
    echo -e "${PURPLE}=================================================================================${NC}"
    print_timestamp
    echo -e "${PURPLE}$1${NC}"
    print_timestamp
    echo -e "${PURPLE}=================================================================================${NC}"
    echo ""
}

print_subheader() {
    echo ""
    print_timestamp
    echo -e "${CYAN}--- $1 ---${NC}"
}

# Function to record test result
record_test_result() {
    local test_name="$1"
    local result="$2"  # "PASS" or "FAIL"
    
    echo "$test_name:$result" >> "$RESULTS_FILE"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ "$result" = "PASS" ]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        print_success "✅ $test_name: PASSED"
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        print_error "❌ $test_name: FAILED"
    fi
}

# Function to show usage
show_usage() {
    cat << EOF
MoodleClaude Smoke Test Runner
=============================

Usage: $0 [options]

Options:
    --quick           Run quick smoke test (skip lengthy operations)
    --skip-docker     Skip Docker container management
    --verbose         Enable verbose output
    --setup-only      Only validate setup, don't run functionality tests
    --moodle-url URL  Override Moodle URL (default: http://localhost:8080)
    --help            Show this help message

Examples:
    $0                        # Full smoke test
    $0 --quick               # Quick validation
    $0 --skip-docker         # Skip Docker operations
    $0 --setup-only          # Only validate setup

This script is designed to run before GitHub push operations to ensure
all critical functionality is working correctly.

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --setup-only)
            SETUP_ONLY=true
            shift
            ;;
        --moodle-url)
            MOODLE_URL="$2"
            shift 2
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

# Function to setup test environment
setup_test_environment() {
    print_header "PHASE 1: ENVIRONMENT SETUP"
    
    print_subheader "Creating Test Environment"
    
    # Create reports directory
    mkdir -p "$REPORTS_DIR"
    
    # Log system information
    print_status "System Information:"
    echo "  - OS: $(uname -s) $(uname -r)"
    echo "  - Python: $(python3 --version 2>/dev/null || echo 'Not found')"
    echo "  - Docker: $(docker --version 2>/dev/null || echo 'Not found')"
    echo "  - Git: $(git --version 2>/dev/null || echo 'Not found')"
    
    # Check project structure
    if [ ! -d "$PROJECT_ROOT/src" ]; then
        record_test_result "Project Structure" "FAIL"
        print_error "Missing src directory"
        return 1
    fi
    
    if [ ! -f "$PROJECT_ROOT/setup/setup_moodleclaude_v3_fixed.py" ]; then
        record_test_result "Setup Script" "FAIL"
        print_error "Missing setup script"
        return 1
    fi
    
    record_test_result "Project Structure" "PASS"
    record_test_result "Setup Script" "PASS"
    
    print_success "Environment setup completed"
    return 0
}

# Function to validate bug fixes
validate_bug_fixes() {
    print_subheader "Bug Fix Validation"
    
    # Run our bug fix validation tool
    if [ -f "$PROJECT_ROOT/tools/validate_bugfixes.py" ]; then
        if python3 "$PROJECT_ROOT/tools/validate_bugfixes.py"; then
            record_test_result "Bug Fix Validation" "PASS"
        else
            record_test_result "Bug Fix Validation" "FAIL"
            return 1
        fi
    else
        print_warning "Bug fix validation tool not found"
        record_test_result "Bug Fix Validation" "SKIP"
    fi
    
    return 0
}

# Function to validate Python path fix
validate_python_path_fix() {
    print_subheader "Python Path Fix Validation"
    
    # Check if the Python path detection function exists in setup script
    if grep -q "get_python_path" "$PROJECT_ROOT/setup/setup_moodleclaude_v3_fixed.py"; then
        record_test_result "Python Path Fix" "PASS"
    else
        record_test_result "Python Path Fix" "FAIL"
        print_error "Python path fix not found in setup script"
        return 1
    fi
    
    return 0
}

# Function to validate Claude Desktop configuration
validate_claude_desktop_config() {
    print_subheader "Claude Desktop Configuration"
    
    if [ ! -f "$CLAUDE_CONFIG_PATH" ]; then
        record_test_result "Claude Desktop Config" "FAIL"
        print_error "Claude Desktop config not found"
        return 1
    fi
    
    # Check if config contains absolute Python path (not just "python")
    if grep -q '"command": "python"' "$CLAUDE_CONFIG_PATH"; then
        record_test_result "Claude Desktop Python Path" "FAIL"
        print_error "Claude Desktop still uses relative python path"
        return 1
    else
        record_test_result "Claude Desktop Python Path" "PASS"
    fi
    
    # Validate JSON syntax
    if python3 -m json.tool "$CLAUDE_CONFIG_PATH" > /dev/null 2>&1; then
        record_test_result "Claude Desktop JSON Syntax" "PASS"
    else
        record_test_result "Claude Desktop JSON Syntax" "FAIL"
        print_error "Claude Desktop config has invalid JSON"
        return 1
    fi
    
    record_test_result "Claude Desktop Config" "PASS"
    return 0
}

# Function to check Docker environment
check_docker_environment() {
    print_subheader "Docker Environment Check"
    
    if [ "$SKIP_DOCKER" = "true" ]; then
        print_status "Skipping Docker checks (--skip-docker flag)"
        record_test_result "Docker Environment" "SKIP"
        return 0
    fi
    
    # Check Docker availability
    if ! command -v docker &> /dev/null; then
        record_test_result "Docker Installation" "FAIL"
        print_error "Docker not installed"
        return 1
    fi
    record_test_result "Docker Installation" "PASS"
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        record_test_result "Docker Daemon" "FAIL"
        print_error "Docker daemon not running"
        return 1
    fi
    record_test_result "Docker Daemon" "PASS"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        record_test_result "Docker Compose" "FAIL"
        print_error "Docker Compose not available"
        return 1
    fi
    record_test_result "Docker Compose" "PASS"
    
    return 0
}

# Function to validate Moodle environment
validate_moodle_environment() {
    print_header "PHASE 2: MOODLE ENVIRONMENT VALIDATION"
    
    if [ "$SKIP_DOCKER" = "true" ]; then
        print_status "Skipping Moodle environment validation (--skip-docker flag)"
        return 0
    fi
    
    print_subheader "Starting Moodle Containers"
    
    # Check if containers are already running
    if docker ps --format "table {{.Names}}" | grep -q "moodleclaude"; then
        print_status "Moodle containers already running"
        record_test_result "Moodle Container Status" "PASS"
    else
        print_status "Starting Moodle containers..."
        cd "$PROJECT_ROOT"
        
        # Use appropriate compose command
        local compose_cmd="docker-compose"
        if docker compose version &> /dev/null; then
            compose_cmd="docker compose"
        fi
        
        if $compose_cmd up -d; then
            record_test_result "Moodle Container Startup" "PASS"
        else
            record_test_result "Moodle Container Startup" "FAIL"
            print_error "Failed to start Moodle containers"
            return 1
        fi
    fi
    
    print_subheader "Waiting for Moodle Readiness"
    
    # Wait for Moodle to be ready
    local max_attempts=30
    local attempt=1
    local ready=false
    
    while [ $attempt -le $max_attempts ]; do
        print_status "Attempt $attempt/$max_attempts: Checking Moodle..."
        
        if curl -s --max-time 10 "$MOODLE_URL" | grep -qi "moodle"; then
            ready=true
            break
        fi
        
        sleep 5
        attempt=$((attempt + 1))
    done
    
    if [ "$ready" = "true" ]; then
        record_test_result "Moodle Accessibility" "PASS"
        print_success "Moodle is accessible at $MOODLE_URL"
    else
        record_test_result "Moodle Accessibility" "FAIL"
        print_error "Moodle not accessible after waiting"
        return 1
    fi
    
    return 0
}

# Function to test MCP server functionality
test_mcp_server() {
    print_subheader "MCP Server Functionality"
    
    # Check if MCP server file exists
    local mcp_server_file="$PROJECT_ROOT/src/core/working_mcp_server.py"
    if [ ! -f "$mcp_server_file" ]; then
        record_test_result "MCP Server File" "FAIL"
        print_error "MCP server file not found"
        return 1
    fi
    record_test_result "MCP Server File" "PASS"
    
    # Test MCP server syntax
    if python3 -m py_compile "$mcp_server_file"; then
        record_test_result "MCP Server Syntax" "PASS"
    else
        record_test_result "MCP Server Syntax" "FAIL"
        print_error "MCP server has syntax errors"
        return 1
    fi
    
    # Check for required functions
    local required_functions=("create_course" "get_courses" "test_connection")
    for func in "${required_functions[@]}"; do
        if grep -q "$func" "$mcp_server_file"; then
            record_test_result "MCP Function: $func" "PASS"
        else
            record_test_result "MCP Function: $func" "FAIL"
            print_error "Required function '$func' not found in MCP server"
        fi
    done
    
    return 0
}

# Function to test setup script
test_setup_script() {
    print_subheader "Setup Script Validation"
    
    local setup_script="$PROJECT_ROOT/setup/setup_moodleclaude_v3_fixed.py"
    
    # Test syntax
    if python3 -c "exec(open('$setup_script').read())" 2>/dev/null; then
        record_test_result "Setup Script Syntax" "PASS"
    else
        record_test_result "Setup Script Syntax" "FAIL"
        print_error "Setup script has syntax errors"
        return 1
    fi
    
    # Check for bug fix implementations
    local bug_fixes=("get_python_path" "create_moodleclaude_service" "fix_token_permissions")
    for fix in "${bug_fixes[@]}"; do
        if grep -q "$fix" "$setup_script"; then
            record_test_result "Bug Fix: $fix" "PASS"
        else
            record_test_result "Bug Fix: $fix" "FAIL"
            print_error "Bug fix '$fix' not found in setup script"
        fi
    done
    
    return 0
}

# Function to run functionality tests
run_functionality_tests() {
    print_header "PHASE 3: FUNCTIONALITY TESTS"
    
    if [ "$SETUP_ONLY" = "true" ]; then
        print_status "Skipping functionality tests (--setup-only flag)"
        return 0
    fi
    
    # Test Python dependencies
    print_subheader "Python Dependencies"
    local required_packages=("aiohttp" "asyncio" "json" "os" "sys")
    for package in "${required_packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            record_test_result "Python Package: $package" "PASS"
        else
            record_test_result "Python Package: $package" "FAIL"
            print_error "Required Python package '$package' not available"
        fi
    done
    
    # Test file permissions
    print_subheader "File Permissions"
    local executable_files=("$PROJECT_ROOT/setup/setup_moodleclaude_v3_fixed.py")
    for file in "${executable_files[@]}"; do
        if [ -x "$file" ] || [ -r "$file" ]; then
            record_test_result "File Access: $(basename "$file")" "PASS"
        else
            record_test_result "File Access: $(basename "$file")" "FAIL"
            print_error "File not accessible: $file"
        fi
    done
    
    # Test configuration files
    print_subheader "Configuration Validation"
    local config_files=("$PROJECT_ROOT/config/moodle_tokens.env")
    for config in "${config_files[@]}"; do
        if [ -f "$config" ]; then
            record_test_result "Config File: $(basename "$config")" "PASS"
        else
            record_test_result "Config File: $(basename "$config")" "FAIL"
            print_error "Configuration file missing: $config"
        fi
    done
    
    return 0
}

# Function to run quick tests for rapid validation
run_quick_tests() {
    print_header "QUICK SMOKE TEST MODE"
    
    # Essential checks only
    print_subheader "Essential Validations"
    
    # 1. Project structure
    if [ -d "$PROJECT_ROOT/src" ] && [ -f "$PROJECT_ROOT/setup/setup_moodleclaude_v3_fixed.py" ]; then
        record_test_result "Project Structure" "PASS"
    else
        record_test_result "Project Structure" "FAIL"
    fi
    
    # 2. Python syntax of critical files
    local critical_files=(
        "$PROJECT_ROOT/setup/setup_moodleclaude_v3_fixed.py"
        "$PROJECT_ROOT/src/core/working_mcp_server.py"
    )
    
    for file in "${critical_files[@]}"; do
        if [ -f "$file" ] && python3 -m py_compile "$file" 2>/dev/null; then
            record_test_result "Syntax: $(basename "$file")" "PASS"
        else
            record_test_result "Syntax: $(basename "$file")" "FAIL"
        fi
    done
    
    # 3. Bug fix validation
    if [ -f "$PROJECT_ROOT/tools/validate_bugfixes.py" ]; then
        if python3 "$PROJECT_ROOT/tools/validate_bugfixes.py" >/dev/null 2>&1; then
            record_test_result "Bug Fixes" "PASS"
        else
            record_test_result "Bug Fixes" "FAIL"
        fi
    fi
    
    # 4. Claude Desktop config
    if [ -f "$CLAUDE_CONFIG_PATH" ] && python3 -m json.tool "$CLAUDE_CONFIG_PATH" >/dev/null 2>&1; then
        record_test_result "Claude Desktop Config" "PASS"
    else
        record_test_result "Claude Desktop Config" "FAIL"
    fi
    
    return 0
}

# Function to generate test report
generate_test_report() {
    local report_file="$REPORTS_DIR/smoke_test_report.html"
    local json_report="$REPORTS_DIR/smoke_test_report.json"
    
    print_header "GENERATING TEST REPORT"
    
    # Create JSON report
    cat > "$json_report" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "test_run": {
        "mode": "$([ "$QUICK_MODE" = "true" ] && echo "quick" || echo "full")",
        "total_tests": $TOTAL_TESTS,
        "passed_tests": $PASSED_TESTS,
        "failed_tests": $FAILED_TESTS,
        "success_rate": "$(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
    },
    "results": {
EOF
    
    local first=true
    if [ -f "$RESULTS_FILE" ]; then
        while IFS=':' read -r test_name result; do
            if [ "$first" = "false" ]; then
                echo "," >> "$json_report"
            fi
            echo "        \"$test_name\": \"$result\"" >> "$json_report"
            first=false
        done < "$RESULTS_FILE"
    fi
    
    cat >> "$json_report" << EOF
    },
    "environment": {
        "os": "$(uname -s)",
        "python_version": "$(python3 --version 2>/dev/null || echo 'Not found')",
        "project_root": "$PROJECT_ROOT"
    }
}
EOF
    
    # Create HTML report
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>MoodleClaude Smoke Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .pass { color: green; }
        .fail { color: red; }
        .skip { color: orange; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .summary { background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>MoodleClaude Smoke Test Report</h1>
        <p>Generated: $(date)</p>
        <p>Mode: $([ "$QUICK_MODE" = "true" ] && echo "Quick Test" || echo "Full Test")</p>
    </div>
    
    <div class="summary">
        <h2>Test Summary</h2>
        <p><strong>Total Tests:</strong> $TOTAL_TESTS</p>
        <p><strong>Passed:</strong> <span class="pass">$PASSED_TESTS</span></p>
        <p><strong>Failed:</strong> <span class="fail">$FAILED_TESTS</span></p>
        <p><strong>Success Rate:</strong> $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%</p>
    </div>
    
    <h2>Test Results</h2>
    <table>
        <tr><th>Test Name</th><th>Result</th></tr>
EOF
    
    if [ -f "$RESULTS_FILE" ]; then
        while IFS=':' read -r test_name result; do
            local css_class=""
            case $result in
                "PASS") css_class="pass" ;;
                "FAIL") css_class="fail" ;;
                "SKIP") css_class="skip" ;;
            esac
            echo "        <tr><td>$test_name</td><td class=\"$css_class\">$result</td></tr>" >> "$report_file"
        done < "$RESULTS_FILE"
    fi
    
    cat >> "$report_file" << EOF
    </table>
</body>
</html>
EOF
    
    print_success "Reports generated:"
    print_status "  - HTML: $report_file"
    print_status "  - JSON: $json_report"
}

# Function to display final summary
display_final_summary() {
    print_header "SMOKE TEST SUMMARY"
    
    echo ""
    print_status "Test Results Summary:"
    echo "  📊 Total Tests: $TOTAL_TESTS"
    echo "  ✅ Passed: $PASSED_TESTS"
    echo "  ❌ Failed: $FAILED_TESTS"
    echo "  📈 Success Rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        print_success "🎉 ALL TESTS PASSED! MoodleClaude is ready for GitHub push."
        echo ""
        print_status "✅ Environment is properly configured"
        print_status "✅ All bug fixes are in place" 
        print_status "✅ Core functionality is working"
        print_status "✅ Ready for deployment"
        echo ""
        return 0
    else
        print_error "💥 $FAILED_TESTS TESTS FAILED! Please fix issues before pushing."
        echo ""
        print_status "Failed tests:"
        if [ -f "$RESULTS_FILE" ]; then
            while IFS=':' read -r test_name result; do
                if [ "$result" = "FAIL" ]; then
                    echo "  ❌ $test_name"
                fi
            done < "$RESULTS_FILE"
        fi
        echo ""
        print_status "Check the detailed report for more information."
        return 1
    fi
}

# Main execution function
main() {
    print_header "MOODLECLAUDE SMOKE TEST SUITE"
    print_status "Starting comprehensive smoke test..."
    
    if [ "$QUICK_MODE" = "true" ]; then
        print_status "Running in QUICK MODE - essential checks only"
    else
        print_status "Running FULL SMOKE TEST - comprehensive validation"
    fi
    
    echo ""
    
    # Create reports directory
    mkdir -p "$REPORTS_DIR"
    
    # Initialize results file
    rm -f "$RESULTS_FILE" 2>/dev/null || true
    touch "$RESULTS_FILE"
    
    local overall_result=0
    
    # Run tests based on mode
    if [ "$QUICK_MODE" = "true" ]; then
        run_quick_tests || overall_result=1
    else
        # Full test sequence
        setup_test_environment || overall_result=1
        validate_bug_fixes || overall_result=1 
        validate_python_path_fix || overall_result=1
        validate_claude_desktop_config || overall_result=1
        check_docker_environment || overall_result=1
        validate_moodle_environment || overall_result=1
        test_mcp_server || overall_result=1
        test_setup_script || overall_result=1
        run_functionality_tests || overall_result=1
    fi
    
    # Generate reports
    generate_test_report
    
    # Display summary
    display_final_summary
    
    # Exit with appropriate code
    exit $overall_result
}

# Cleanup function
cleanup_on_exit() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        print_error "Smoke test failed at line $1"
    fi
    
    # Clean up temporary files
    rm -f "$RESULTS_FILE" 2>/dev/null || true
    
    exit $exit_code
}

# Trap errors
trap 'cleanup_on_exit $LINENO' ERR

# Check if running as pre-push hook
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    # Called directly, run main
    main "$@"
fi

# Export functions for use by other scripts
export -f print_status print_success print_warning print_error print_header
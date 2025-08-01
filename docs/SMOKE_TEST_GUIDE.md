# MoodleClaude Smoke Test Guide

## 🚀 Overview

The MoodleClaude smoke test system provides comprehensive validation of your development environment and core functionality before GitHub pushes. It consolidates all test scripts into a unified, efficient testing pipeline.

## 📋 Test Flow

The smoke test follows this logical sequence:

1. **Setup Phase** → Environment validation and configuration
2. **Moodle Environment** → Container readiness and connectivity  
3. **Functionality Tests** → Core MCP server and bug fix validation

## 🛠️ Installation

### Install Git Hooks (Recommended)

```bash
# Install pre-push hook that runs smoke tests automatically
./scripts/setup_git_hooks.sh
```

This installs a pre-push Git hook that automatically runs smoke tests before every push, preventing broken code from reaching the repository.

## 🎯 Usage

### Quick Smoke Test (Pre-Push)

```bash
# Fast validation - essential checks only
./scripts/smoke_test.sh --quick --skip-docker
```

**Use Cases:**
- Pre-push validation
- Rapid development cycles
- CI/CD pipeline entry point

**What it validates:**
- ✅ Project structure integrity
- ✅ Python syntax of critical files
- ✅ Bug fix implementations
- ✅ Claude Desktop configuration
- ✅ Core functionality availability

### Full Smoke Test

```bash
# Comprehensive validation with Docker environment
./scripts/smoke_test.sh
```

**Use Cases:**
- Pre-deployment validation
- Weekly comprehensive checks
- Post-setup verification

**What it includes:**
- All quick test validations
- Docker environment setup
- Moodle container readiness
- MCP server functionality tests
- Complete integration validation

### Custom Options

```bash
# Available options
./scripts/smoke_test.sh --help

# Examples
./scripts/smoke_test.sh --quick           # Fast mode
./scripts/smoke_test.sh --skip-docker     # No Docker operations
./scripts/smoke_test.sh --setup-only      # Only validate setup
./scripts/smoke_test.sh --moodle-url http://custom-moodle.local
```

## 📊 Test Reports

After each run, detailed reports are generated:

### HTML Report
```bash
open reports/smoke_test/smoke_test_report.html
```
- Visual test results with color coding
- Summary statistics and success rates
- Environment information

### JSON Report
```bash
cat reports/smoke_test/smoke_test_report.json
```
- Machine-readable test results
- Integration with CI/CD systems
- Detailed test breakdown

### Example Report Output
```json
{
    "timestamp": "2025-08-01T16:13:01Z",
    "test_run": {
        "mode": "quick",
        "total_tests": 5,
        "passed_tests": 5,
        "failed_tests": 0,
        "success_rate": "100%"
    },
    "results": {
        "Project Structure": "PASS",
        "Bug Fixes": "PASS",
        "Claude Desktop Config": "PASS"
    }
}
```

## 🔧 Integration with Development Workflow

### Automatic Pre-Push Validation

When Git hooks are installed:

1. **Developer runs:** `git push`
2. **Hook triggers:** Quick smoke test automatically
3. **On success:** Push continues normally
4. **On failure:** Push is blocked with detailed error report

```bash
# Example blocked push output
❌ Smoke test failed! Push is blocked.
💥 Please fix the failing tests before pushing.

📋 To check what failed:
   ./scripts/smoke_test.sh --quick

🔧 To push without running tests (not recommended):
   git push --no-verify
```

### GitHub Actions Integration

The smoke test is integrated into GitHub workflows:

- **CI Pipeline:** Runs on every push to main branches
- **PR Validation:** Validates pull requests before merge
- **Nightly Builds:** Comprehensive validation on schedule

## 🐛 Validated Bug Fixes

The smoke test validates all critical bug fixes:

### ✅ Verified Fixes
- **MCP Server "Server disconnected" error**
  - Root cause: `spawn python ENOENT`
  - Fix: Absolute Python path in Claude Desktop config

- **Course creation "Access control exception"**
  - Root cause: Insufficient token permissions
  - Fix: MoodleClaude web service with proper roles

- **Python path detection**
  - Root cause: Environment-specific Python locations
  - Fix: Automatic Python path detection in setup

- **Token permissions**
  - Root cause: Limited web service capabilities
  - Fix: Comprehensive role and capability assignment

## 🎨 Test Categories

### 🔍 Essential Validations (Quick Mode)
- Project structure integrity
- Critical file syntax validation
- Bug fix implementation verification
- Configuration file validation

### 🐳 Environment Tests (Full Mode)
- Docker availability and health
- Container startup and readiness
- Moodle accessibility and connectivity
- Network configuration validation

### ⚙️ Functionality Tests (Full Mode)
- MCP server functionality
- Python dependency validation
- File permission checks
- Integration point testing

## 📈 Success Criteria

### ✅ Ready for Push (100% Pass Rate)
```
🎉 ALL TESTS PASSED! MoodleClaude is ready for GitHub push.

✅ Environment is properly configured
✅ All bug fixes are in place
✅ Core functionality is working
✅ Ready for deployment
```

### ❌ Issues Detected
```
💥 X TESTS FAILED! Please fix issues before pushing.

Failed tests:
  ❌ Test Name 1
  ❌ Test Name 2

Check the detailed report for more information.
```

## 🔧 Troubleshooting

### Common Issues

1. **"Docker not available"**
   ```bash
   # Solution: Use skip-docker flag for non-Docker environments
   ./scripts/smoke_test.sh --quick --skip-docker
   ```

2. **"Bug fixes not integrated"**
   ```bash
   # Solution: Run the bug fix validation tool directly
   python3 tools/validate_bugfixes.py
   ```

3. **"Claude Desktop config invalid"**
   ```bash
   # Solution: Check JSON syntax and Python path
   python3 -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

### Manual Debugging

```bash
# Run individual validation components
python3 tools/validate_bugfixes.py
python3 setup_moodleclaude_v3_fixed.py --validate-only

# Check specific files
python3 -m py_compile src/core/working_mcp_server.py
python3 -c "exec(open('setup_moodleclaude_v3_fixed.py').read())"
```

## 🚀 Best Practices

### For Developers
1. **Always run quick smoke test** before committing major changes
2. **Install Git hooks** for automatic validation
3. **Review test reports** when failures occur
4. **Use `--skip-docker`** in development environments without Docker

### For CI/CD
1. **Use quick mode** for fast feedback loops
2. **Use full mode** for deployment validation
3. **Archive test reports** as artifacts
4. **Block deployments** on test failures

### For Teams
1. **Standardize on smoke test** as quality gate
2. **Document custom test configurations** for specific environments
3. **Review test results** in code reviews
4. **Keep smoke test updated** with new features

## 📚 Related Documentation

- [Bug Fix Documentation](../BUGFIX_DOCUMENTATION.md) - Detailed fix descriptions
- [GitHub Workflows](../.github/workflows/) - CI/CD integration
- [Pre-commit Hooks](../.pre-commit-config.yaml) - Code quality checks
- [Setup Guide](../README.md) - Initial project setup

---

**💡 Pro Tip:** The smoke test is designed to be fast and comprehensive. In quick mode, it completes in under 10 seconds, making it perfect for pre-push validation without slowing down your development workflow.
#!/bin/bash

# MoodleClaude Git Hooks Setup
# ============================
# Installs Git hooks for pre-push smoke testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Get repository root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)")
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"
GITHOOKS_SOURCE_DIR="$REPO_ROOT/.githooks"

echo -e "${BLUE}🔧 MoodleClaude Git Hooks Setup${NC}"
echo ""

# Check if we're in a Git repository
if [ ! -d "$REPO_ROOT/.git" ]; then
    print_error "Not in a Git repository. Please run this from within the MoodleClaude repository."
    exit 1
fi

print_status "Repository root: $REPO_ROOT"
print_status "Git hooks directory: $GIT_HOOKS_DIR"

# Create git hooks directory if it doesn't exist
if [ ! -d "$GIT_HOOKS_DIR" ]; then
    print_error "Git hooks directory not found. This might not be a valid Git repository."
    exit 1
fi

# Check if source hooks directory exists
if [ ! -d "$GITHOOKS_SOURCE_DIR" ]; then
    print_error "Source hooks directory not found: $GITHOOKS_SOURCE_DIR"
    exit 1
fi

# Function to install a hook
install_hook() {
    local hook_name="$1"
    local source_hook="$GITHOOKS_SOURCE_DIR/$hook_name"
    local target_hook="$GIT_HOOKS_DIR/$hook_name"
    
    if [ ! -f "$source_hook" ]; then
        print_warning "Source hook not found: $source_hook"
        return 1
    fi
    
    # Backup existing hook if it exists
    if [ -f "$target_hook" ]; then
        print_status "Backing up existing $hook_name hook"
        mv "$target_hook" "$target_hook.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Copy the hook
    cp "$source_hook" "$target_hook"
    chmod +x "$target_hook"
    
    print_success "Installed $hook_name hook"
    return 0
}

# Install hooks
print_status "Installing Git hooks..."

# Install pre-push hook
if install_hook "pre-push"; then
    print_success "Pre-push hook installed successfully"
    print_status "This hook will run smoke tests before each push"
else
    print_error "Failed to install pre-push hook"
    exit 1
fi

# Verify smoke test script exists
SMOKE_TEST_SCRIPT="$REPO_ROOT/scripts/smoke_test.sh"
if [ ! -f "$SMOKE_TEST_SCRIPT" ]; then
    print_error "Smoke test script not found: $SMOKE_TEST_SCRIPT"
    print_error "Please ensure the smoke test script is properly installed"
    exit 1
fi

# Make smoke test script executable
chmod +x "$SMOKE_TEST_SCRIPT"
print_success "Smoke test script is ready"

echo ""
print_success "🎉 Git hooks setup completed!"
echo ""
print_status "What happens now:"
echo "  • Pre-push hook will run smoke tests before each 'git push'"
echo "  • If smoke tests fail, the push will be blocked"
echo "  • You can bypass with 'git push --no-verify' (not recommended)"
echo ""
print_status "To test the hook:"
echo "  git add . && git commit -m 'test commit' && git push"
echo ""
print_status "To run smoke test manually:"
echo "  ./scripts/smoke_test.sh --quick"
echo ""
print_status "To view test reports:"
echo "  open reports/smoke_test/smoke_test_report.html"
echo ""
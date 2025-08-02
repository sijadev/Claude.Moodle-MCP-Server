#!/bin/bash
# 🤖 Claude Code - Quick Git Operations
# Uses the professional tools/claude_code_git.py

cd /Users/simonjanke/Projects/MoodleClaude

echo "🤖 Claude Code - Using Professional Git Tool"
echo "============================================"

# Check if Python tool exists
if [ ! -f "tools/claude_code_git.py" ]; then
    echo "❌ Git tool not found: tools/claude_code_git.py"
    exit 1
fi

# Make sure it's executable
chmod +x tools/claude_code_git.py

# Run full workflow with the professional tool
echo "🚀 Executing Claude Code Git Workflow..."
python3 tools/claude_code_git.py full

echo ""
echo "✨ Claude Code Git Operations Complete!"

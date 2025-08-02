#!/bin/bash
# 🤖 Claude Code - Git Operations Script
# Label: "Claude Code" für automatisierte Code-Verbesserungen

cd /Users/simonjanke/Projects/MoodleClaude

echo "🤖 Claude Code - Git Operations"
echo "==============================="

# Check current status
echo "📊 Current Git Status:"
git status --short

echo ""
echo "🌿 Current Branch: $(git branch --show-current)"

# Add all changes  
echo ""
echo "📝 Adding all changes to staging..."
git add .

# Show what will be committed
echo ""
echo "📋 Files to be committed:"
git diff --cached --name-only

# Commit with the prepared message
echo ""
echo "💾 Creating commit with 'Claude Code' label..."
git commit -F CLAUDE_CODE_COMMIT_MESSAGE.txt

# Create a git tag for this Claude Code session
echo ""
echo "🏷️ Creating 'claude-code' tag..."
git tag -a "claude-code-$(date +%Y%m%d-%H%M)" -m "Claude Code automated improvements - $(date)"

# Push changes and tags
echo ""
echo "🚀 Pushing to GitHub..."
git push origin $(git branch --show-current)
git push origin --tags

echo ""
echo "✅ Claude Code Git Operations Completed!"
echo "🔗 Repository: https://github.com/sijadev/MoodleClaude"
echo "🏷️ Tagged with: claude-code-$(date +%Y%m%d-%H%M)"
echo "📅 Completed: $(date)"

# Final status
echo ""
echo "📊 Final Status:"
git log --oneline -n 5

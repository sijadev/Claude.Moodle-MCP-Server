#!/bin/bash
# Restore MoodleClaude to Default Setup State

echo "🔄 Restoring MoodleClaude to Default Setup State..."
echo "=================================================="

DEFAULT_BACKUP=$(readlink backups/default_setup_latest 2>/dev/null)

if [ -z "$DEFAULT_BACKUP" ]; then
    echo "❌ No default setup backup found!"
    echo "Create one by running: ./setup_fresh_moodleclaude_complete.sh"
    exit 1
fi

echo "📦 Restoring from: $DEFAULT_BACKUP"
./restore_moodleclaude.sh "$DEFAULT_BACKUP"

echo "✅ MoodleClaude restored to fresh setup state!"
echo "🌐 Access: http://localhost:8080"
echo "🔑 Credentials: Check config/moodle_fresh_complete.env"
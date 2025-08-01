#!/bin/bash
# Automated MoodleClaude Backup with Rotation

BACKUP_DIR="./backups"
MAX_BACKUPS=10
LOG_FILE="./logs/automated_backup.log"

mkdir -p logs

echo "$(date): Starting automated backup" >> "$LOG_FILE"

# Create backup
./backup_moodleclaude.sh >> "$LOG_FILE" 2>&1

# Cleanup old backups (keep last MAX_BACKUPS)
OLD_BACKUPS=$(ls -1t "$BACKUP_DIR" | grep "moodleclaude_" | tail -n +$((MAX_BACKUPS + 1)))

if [ -n "$OLD_BACKUPS" ]; then
    echo "$(date): Cleaning up old backups" >> "$LOG_FILE"
    for backup in $OLD_BACKUPS; do
        rm -rf "$BACKUP_DIR/$backup"
        echo "$(date): Removed $backup" >> "$LOG_FILE"
    done
fi

echo "$(date): Automated backup completed" >> "$LOG_FILE"

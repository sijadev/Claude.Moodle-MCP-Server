#!/bin/bash
# MoodleClaude v3.0 - Backup Management System
# Listet alle verfügbaren Backups und deren Details

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_header() { echo -e "${BLUE}=== $1 ===${NC}"; }

BACKUP_DIR="./backups"

echo "📦 MoodleClaude Backup Management"
echo "================================="

# Check if backups directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    print_warning "No backups directory found!"
    echo "Create your first backup with: ./backup_moodleclaude.sh"
    exit 0
fi

# Get list of backups
BACKUPS=$(ls -1 "$BACKUP_DIR" 2>/dev/null | grep "^moodleclaude_" | sort -r)

if [ -z "$BACKUPS" ]; then
    print_warning "No MoodleClaude backups found!"
    echo "Create your first backup with: ./backup_moodleclaude.sh"
    exit 0
fi

print_header "Available Backups"

# Counter for numbering
counter=1

# Display backup information
for backup in $BACKUPS; do
    backup_path="$BACKUP_DIR/$backup"
    
    # Extract timestamp from backup name
    timestamp=$(echo "$backup" | sed 's/moodleclaude_//' | sed 's/_/ /' | sed 's/\(..\)\(..\)\(..\)/20\1-\2-\3 /')
    
    # Get backup size
    size=$(du -sh "$backup_path" 2>/dev/null | cut -f1 || echo "Unknown")
    
    # Get setup type if available
    setup_type="Unknown"
    if [ -f "$backup_path/container_info.json" ]; then
        setup_type=$(python3 -c "import json; print(json.load(open('$backup_path/container_info.json'))['setup_type'])" 2>/dev/null || echo "Unknown")
    fi
    
    # Get creation date
    creation_date=$(stat -c %y "$backup_path" 2>/dev/null | cut -d' ' -f1 || date +%Y-%m-%d)
    
    echo
    echo "${BLUE}[$counter]${NC} $backup"
    echo "    📅 Created: $creation_date"
    echo "    ⏰ Timestamp: $timestamp"
    echo "    📊 Size: $size"
    echo "    🎯 Type: $setup_type"
    
    # Show backup contents if manifest exists
    if [ -f "$backup_path/backup_manifest.txt" ]; then
        file_count=$(grep -c "\.tar\.gz\|\.sql" "$backup_path/backup_manifest.txt" 2>/dev/null || echo "0")
        echo "    📋 Files: $file_count backup files"
    fi
    
    # Show database info if available
    if [ -f "$backup_path/container_info.json" ]; then
        db_name=$(python3 -c "import json; print(json.load(open('$backup_path/container_info.json'))['database']['name'])" 2>/dev/null || echo "")
        if [ -n "$db_name" ]; then
            echo "    🗄️  Database: $db_name"
        fi
    fi
    
    echo "    🔄 Restore: ./restore_moodleclaude.sh $backup"
    
    ((counter++))
done

print_header "Backup Statistics"

# Calculate total backup size
total_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo "Unknown")
backup_count=$(echo "$BACKUPS" | wc -l)

echo
print_status "Total Backups: $backup_count"
print_status "Total Size: $total_size"
print_status "Backup Directory: $BACKUP_DIR"

# Show disk usage if available
if command -v df >/dev/null 2>&1; then
    disk_usage=$(df -h . | tail -1 | awk '{print $4}')
    print_status "Available Disk Space: $disk_usage"
fi

print_header "Management Commands"

echo
echo "📋 Available Commands:"
echo "  🔄 Create Backup:    ./backup_moodleclaude.sh"
echo "  📦 Restore Backup:   ./restore_moodleclaude.sh <backup_name>"
echo "  📋 List Backups:     ./list_backups.sh"
echo "  🗑️  Delete Backup:    rm -rf $BACKUP_DIR/<backup_name>"
echo

# Show recent backups (last 3)
if [ $backup_count -gt 3 ]; then
    print_header "Recent Backups (Last 3)"
    echo "$BACKUPS" | head -3 | while read -r backup; do
        creation_date=$(stat -c %y "$BACKUP_DIR/$backup" 2>/dev/null | cut -d' ' -f1 || date +%Y-%m-%d)
        size=$(du -sh "$BACKUP_DIR/$backup" 2>/dev/null | cut -f1 || echo "Unknown")
        echo "  📦 $backup ($creation_date, $size)"
    done
    echo
fi

# Cleanup suggestions
if [ $backup_count -gt 10 ]; then
    print_warning "You have $backup_count backups. Consider cleaning up old ones:"
    echo "$BACKUPS" | tail -n +11 | while read -r old_backup; do
        creation_date=$(stat -c %y "$BACKUP_DIR/$old_backup" 2>/dev/null | cut -d' ' -f1 || date +%Y-%m-%d)
        echo "  🗑️  rm -rf $BACKUP_DIR/$old_backup  # Created: $creation_date"
    done
fi

echo
print_status "Use backup numbers [1], [2], etc. or full backup names for restore"
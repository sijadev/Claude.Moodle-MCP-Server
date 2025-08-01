#!/bin/bash
# MoodleClaude v3.0 - Repository Management System
# Verwaltet lokales Git Repository für Backups und Code

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

echo "🗃️  MoodleClaude Repository Management"
echo "======================================"

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    print_error "Not a git repository!"
    echo "Initialize git repository first:"
    echo "  git init"
    echo "  git add ."
    echo "  git commit -m 'Initial commit'"
    exit 1
fi

COMMAND=${1:-"status"}

case $COMMAND in
    "init")
        print_header "Initializing Repository for Backups"
        
        # Create .gitignore for backup management
        if [ ! -f .gitignore ]; then
            cat > .gitignore << 'EOF'
# MoodleClaude - Large files and temporary data
*.tar.gz
*.sql
backups/*/database_dump.sql
backups/*/moodle_files.tar.gz
backups/*/moodle_data.tar.gz
backups/*/plugin_files.tar.gz
backups/*/*.tar.gz

# Docker volumes and logs
logs/*.log
*.log

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
venv_e2e/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
.temp/
EOF
            print_status "Created .gitignore for backup management"
        fi
        
        # Create backup tracking file
        cat > .backup_tracking << 'EOF'
# MoodleClaude Backup Tracking
# This file tracks which backups are stored in git vs external storage

# Format: backup_name:storage_type:size:checksum
# storage_types: git, external, lfs, compressed
EOF
        
        print_status "Repository initialized for backup management"
        ;;
        
    "backup-commit")
        print_header "Committing Current State with Backup"
        
        # Create backup first
        print_status "Creating backup..."
        ./backup_moodleclaude.sh
        
        # Get latest backup name
        LATEST_BACKUP=$(ls -1 backups/ | grep "moodleclaude_" | sort -r | head -1)
        
        if [ -n "$LATEST_BACKUP" ]; then
            # Add backup metadata to git (not the large files)
            git add backups/"$LATEST_BACKUP"/container_info.json
            git add backups/"$LATEST_BACKUP"/backup_manifest.txt
            git add backups/"$LATEST_BACKUP"/environment_snapshot.txt
            git add backups/"$LATEST_BACKUP"/docker-compose.yml
            git add backups/"$LATEST_BACKUP"/config/ 2>/dev/null || true
            
            # Record backup in tracking file
            BACKUP_SIZE=$(du -sh backups/"$LATEST_BACKUP" | cut -f1)
            echo "$LATEST_BACKUP:external:$BACKUP_SIZE:$(date)" >> .backup_tracking
            
            # Commit everything
            git add .
            git commit -m "🔄 Backup: $LATEST_BACKUP

- Created MoodleClaude backup with full container state
- Database dump and files stored externally
- Metadata and configs tracked in git
- Size: $BACKUP_SIZE

📋 Backup Contents:
- Container configuration
- Database schema and data
- Moodle application files
- Plugin files and configuration
- Environment snapshot

🔄 To restore: ./restore_moodleclaude.sh $LATEST_BACKUP"

            print_status "✅ Committed code and backup metadata to git"
            print_status "📦 Backup files stored externally: $BACKUP_SIZE"
        else
            print_error "No backup created!"
            exit 1
        fi
        ;;
        
    "save-snapshot")
        print_header "Saving Development Snapshot"
        
        # Create lightweight commit for development progress
        git add .
        
        # Generate commit message based on recent changes
        CHANGED_FILES=$(git diff --cached --name-only | wc -l)
        TIMESTAMP=$(date +"%Y-%m-%d %H:%M")
        
        git commit -m "💾 Development Snapshot - $TIMESTAMP

Updated $CHANGED_FILES files
Auto-generated snapshot for development progress

🛠️ Recent changes:
$(git diff --cached --name-only | head -10 | sed 's/^/- /')
$(if [ $(git diff --cached --name-only | wc -l) -gt 10 ]; then echo "- ... and more"; fi)

📝 Use 'git log --oneline' to see recent commits"

        print_status "✅ Development snapshot saved"
        ;;
        
    "clean-old-backups")
        print_header "Cleaning Old Backups"
        
        # Keep last 5 backups, remove older ones
        OLD_BACKUPS=$(ls -1 backups/ | grep "moodleclaude_" | sort -r | tail -n +6)
        
        if [ -n "$OLD_BACKUPS" ]; then
            echo "Old backups to remove:"
            for backup in $OLD_BACKUPS; do
                backup_size=$(du -sh backups/"$backup" | cut -f1)
                echo "  🗑️  $backup ($backup_size)"
            done
            
            read -p "Remove these old backups? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                for backup in $OLD_BACKUPS; do
                    rm -rf backups/"$backup"
                    print_status "Removed $backup"
                done
                
                # Update tracking file
                cp .backup_tracking .backup_tracking.bak
                for backup in $OLD_BACKUPS; do
                    grep -v "^$backup:" .backup_tracking.bak > .backup_tracking || true
                done
                rm .backup_tracking.bak
                
                print_status "✅ Cleaned up old backups"
            else
                print_status "Backup cleanup cancelled"
            fi
        else
            print_status "No old backups to clean"
        fi
        ;;
        
    "sync-remote")
        print_header "Syncing with Remote Repository"
        
        # Check if remote exists
        if git remote | grep -q origin; then
            print_status "Pushing to remote repository..."
            git push origin main 2>/dev/null || git push origin master 2>/dev/null || {
                print_warning "Failed to push to remote. Checking remote status..."
                git remote -v
            }
        else
            print_warning "No remote repository configured"
            echo "To add remote:"
            echo "  git remote add origin <repository-url>"
            echo "  git push -u origin main"
        fi
        ;;
        
    "status")
        print_header "Repository Status"
        
        # Git status
        print_status "Git Status:"
        git status --porcelain | head -10
        
        if [ $(git status --porcelain | wc -l) -gt 10 ]; then
            echo "... and $(expr $(git status --porcelain | wc -l) - 10) more files"
        fi
        
        echo
        
        # Recent commits
        print_status "Recent Commits:"
        git log --oneline -5
        
        echo
        
        # Backup status
        if [ -d backups ]; then
            BACKUP_COUNT=$(ls -1 backups/ | grep "moodleclaude_" | wc -l)
            TOTAL_BACKUP_SIZE=$(du -sh backups/ 2>/dev/null | cut -f1 || echo "0")
            print_status "Backups: $BACKUP_COUNT total, $TOTAL_BACKUP_SIZE"
            
            # Show latest backup
            LATEST_BACKUP=$(ls -1 backups/ | grep "moodleclaude_" | sort -r | head -1)
            if [ -n "$LATEST_BACKUP" ]; then
                LATEST_SIZE=$(du -sh backups/"$LATEST_BACKUP" | cut -f1)
                print_status "Latest: $LATEST_BACKUP ($LATEST_SIZE)"
            fi
        else
            print_status "No backups directory found"
        fi
        
        echo
        
        # Repository size
        REPO_SIZE=$(du -sh . | cut -f1)
        print_status "Repository Size: $REPO_SIZE"
        
        # Remote status
        if git remote | grep -q origin; then
            REMOTE_URL=$(git remote get-url origin)
            print_status "Remote: $REMOTE_URL"
        else
            print_warning "No remote repository configured"
        fi
        ;;
        
    "help"|*)
        print_header "Usage"
        echo
        echo "Repository Management Commands:"
        echo "  ./manage_repository.sh init                 - Initialize repo for backup management"
        echo "  ./manage_repository.sh backup-commit        - Create backup and commit to git"
        echo "  ./manage_repository.sh save-snapshot        - Quick development snapshot"
        echo "  ./manage_repository.sh clean-old-backups    - Remove old backup files"
        echo "  ./manage_repository.sh sync-remote          - Push to remote repository"
        echo "  ./manage_repository.sh status               - Show repository status"
        echo
        echo "Workflow Examples:"
        echo "  # Regular development"
        echo "  ./manage_repository.sh save-snapshot"
        echo
        echo "  # Before major changes"
        echo "  ./manage_repository.sh backup-commit"
        echo
        echo "  # Maintenance"
        echo "  ./manage_repository.sh clean-old-backups"
        echo "  ./manage_repository.sh sync-remote"
        ;;
esac
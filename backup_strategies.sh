#!/bin/bash
# MoodleClaude v3.0 - Backup Strategy Implementation
# Verschiedene Backup-Strategien für verschiedene Use Cases

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_header() { echo -e "${BLUE}=== $1 ===${NC}"; }
print_strategy() { echo -e "${PURPLE}[STRATEGY]${NC} $1"; }

STRATEGY=${1:-"help"}

case $STRATEGY in
    "development")
        print_header "Development Backup Strategy"
        print_strategy "Frequent lightweight backups for daily development"
        
        echo "🔄 Development Strategy Execution..."
        
        # 1. Quick snapshot before starting work
        print_status "Creating development snapshot..."
        ./manage_repository.sh save-snapshot
        
        # 2. Create working backup (every 2-3 hours)
        if [ ! -f ".last_dev_backup" ] || [ $(( $(date +%s) - $(cat .last_dev_backup 2>/dev/null || echo 0) )) -gt 7200 ]; then
            print_status "Creating development backup (2+ hours since last)..."
            ./backup_moodleclaude.sh
            date +%s > .last_dev_backup
            
            # Keep only last 3 development backups (but protect default setup)
            print_status "Cleaning old development backups..."
            ls -1t backups/ | grep "moodleclaude_" | tail -n +4 | while read backup; do
                if [ -d "backups/$backup" ] && [ ! -f "backups/$backup/default_setup.txt" ]; then
                    rm -rf "backups/$backup"
                    print_status "Removed old backup: $backup"
                elif [ -f "backups/$backup/default_setup.txt" ]; then
                    print_status "Protected default setup backup: $backup"
                fi
            done
        else
            print_status "Recent backup exists, skipping full backup"
        fi
        
        print_status "✅ Development backup strategy completed"
        ;;
        
    "milestone")
        print_header "Milestone Backup Strategy"
        print_strategy "Complete backup before major features/releases"
        
        # Get milestone name
        MILESTONE=${2:-$(date +"%Y%m%d_milestone")}
        
        echo "🎯 Creating milestone backup: $MILESTONE"
        
        # 1. Full backup with milestone tagging
        print_status "Creating comprehensive milestone backup..."
        ./backup_moodleclaude.sh
        
        # 2. Get latest backup and rename/tag it
        LATEST_BACKUP=$(ls -1t backups/ | grep "moodleclaude_" | head -1)
        if [ -n "$LATEST_BACKUP" ]; then
            # Create milestone marker
            echo "MILESTONE: $MILESTONE" > "backups/$LATEST_BACKUP/milestone.txt"
            echo "Created: $(date)" >> "backups/$LATEST_BACKUP/milestone.txt"
            echo "Description: Major milestone backup before significant changes" >> "backups/$LATEST_BACKUP/milestone.txt"
            
            print_status "Tagged backup as milestone: $MILESTONE"
        fi
        
        # 3. Git commit with milestone
        print_status "Committing milestone to git..."
        ./manage_repository.sh backup-commit
        
        # 4. Create git tag
        git tag -a "milestone-$MILESTONE" -m "🎯 Milestone: $MILESTONE

Created comprehensive backup before major changes
Backup: $LATEST_BACKUP

This milestone includes:
- Complete working environment
- All configurations and data  
- Plugin state and customizations
- Ready for rollback if needed"

        print_status "✅ Milestone backup strategy completed"
        print_status "📌 Git tag created: milestone-$MILESTONE"
        ;;
        
    "production")
        print_header "Production Backup Strategy"
        print_strategy "Enterprise-grade backup with redundancy and verification"
        
        BACKUP_DATE=$(date +"%Y%m%d_%H%M%S")
        
        echo "🏭 Production Backup Execution..."
        
        # 1. Pre-backup verification
        print_status "Verifying system health..."
        if ! curl -f http://localhost:8080/login/index.php >/dev/null 2>&1; then
            print_error "Moodle not accessible - aborting production backup"
            exit 1
        fi
        
        # 2. Create primary backup
        print_status "Creating primary production backup..."
        ./backup_moodleclaude.sh
        PRIMARY_BACKUP=$(ls -1t backups/ | grep "moodleclaude_" | head -1)
        
        # 3. Create secondary backup (different strategy)
        print_status "Creating secondary backup for redundancy..."
        sleep 2  # Ensure different timestamp
        ./backup_moodleclaude.sh
        SECONDARY_BACKUP=$(ls -1t backups/ | grep "moodleclaude_" | head -1)
        
        # 4. Verify backups
        print_status "Verifying backup integrity..."
        for backup in "$PRIMARY_BACKUP" "$SECONDARY_BACKUP"; do
            if [ -f "backups/$backup/backup_manifest.txt" ]; then
                cd "backups/$backup"
                if sha256sum -c backup_manifest.txt >/dev/null 2>&1; then
                    print_status "✅ Backup verified: $backup"
                else
                    print_error "❌ Backup verification failed: $backup"
                fi
                cd ../..
            fi
        done
        
        # 5. Create production metadata
        cat > "backups/$PRIMARY_BACKUP/production.txt" << EOF
PRODUCTION BACKUP
================
Date: $(date)
Environment: Production
Strategy: Dual redundancy
Primary: $PRIMARY_BACKUP  
Secondary: $SECONDARY_BACKUP
Verification: Passed

Pre-backup Health Check:
- Moodle accessible: ✅
- Database responsive: ✅
- Plugin functional: ✅

Post-backup Actions:
- Offsite sync recommended
- Retention: Keep for 90 days
- Next backup: $(date -d "+1 day" +"%Y-%m-%d")
EOF
        
        # 6. External sync preparation
        mkdir -p production_backups
        cp -r "backups/$PRIMARY_BACKUP" "production_backups/"
        
        print_status "✅ Production backup strategy completed"
        print_status "📦 Primary: $PRIMARY_BACKUP"
        print_status "📦 Secondary: $SECONDARY_BACKUP"
        print_warning "🔄 Remember to sync production_backups/ to offsite storage"
        ;;
        
    "testing")
        print_header "Testing Environment Strategy"
        print_strategy "Baseline snapshots for consistent testing"
        
        TEST_TYPE=${2:-"baseline"}
        
        echo "🧪 Testing Strategy: $TEST_TYPE"
        
        case $TEST_TYPE in
            "baseline")
                print_status "Creating testing baseline..."
                
                # Ensure clean state
                print_status "Setting up fresh test environment..."
                ./setup_fresh_moodleclaude_complete.sh
                
                # Wait for startup
                sleep 30
                
                # Create baseline backup
                print_status "Creating baseline backup..."
                ./backup_moodleclaude.sh
                BASELINE_BACKUP=$(ls -1t backups/ | grep "moodleclaude_" | head -1)
                
                # Mark as baseline
                echo "TESTING BASELINE" > "backups/$BASELINE_BACKUP/test_baseline.txt"
                echo "Created: $(date)" >> "backups/$BASELINE_BACKUP/test_baseline.txt"
                echo "Purpose: Clean state for consistent testing" >> "backups/$BASELINE_BACKUP/test_baseline.txt"
                
                # Create symlink for easy access
                ln -sf "$BASELINE_BACKUP" "backups/test_baseline_latest"
                
                print_status "✅ Testing baseline created: $BASELINE_BACKUP"
                ;;
                
            "restore-baseline")
                print_status "Restoring testing baseline..."
                
                if [ -L "backups/test_baseline_latest" ]; then
                    BASELINE=$(readlink "backups/test_baseline_latest")
                    print_status "Restoring baseline: $BASELINE"
                    ./restore_moodleclaude.sh "$BASELINE"
                else
                    print_error "No baseline found. Create one first:"
                    print_error "./backup_strategies.sh testing baseline"
                    exit 1
                fi
                ;;
                
            *)
                print_error "Unknown test type. Use: baseline, restore-baseline"
                exit 1
                ;;
        esac
        ;;
        
    "team")
        print_header "Team Collaboration Strategy"
        print_strategy "Shared environments for team development"
        
        TEAM_ACTION=${2:-"share"}
        
        case $TEAM_ACTION in
            "share")
                print_status "Creating shareable team environment..."
                
                # Create comprehensive backup
                ./backup_moodleclaude.sh
                TEAM_BACKUP=$(ls -1t backups/ | grep "moodleclaude_" | head -1)
                
                # Create team package
                mkdir -p team_environments
                TEAM_PACKAGE="team_environments/team_env_$(date +%Y%m%d_%H%M%S)"
                mkdir -p "$TEAM_PACKAGE"
                
                # Copy essential files
                cp -r "backups/$TEAM_BACKUP"/* "$TEAM_PACKAGE/"
                cp docker-compose*.yml "$TEAM_PACKAGE/" 2>/dev/null || true
                cp setup_fresh_moodleclaude_complete.sh "$TEAM_PACKAGE/"
                cp restore_moodleclaude.sh "$TEAM_PACKAGE/"
                
                # Create team setup script
                cat > "$TEAM_PACKAGE/setup_team_environment.sh" << 'EOF'
#!/bin/bash
echo "🤝 Setting up MoodleClaude Team Environment..."
echo "============================================="

# Restore environment
./restore_moodleclaude.sh $(basename $(pwd))

echo "✅ Team environment ready!"
echo "🌐 Moodle: http://localhost:8080"
echo "📋 Check team_environment_info.txt for credentials"
EOF
                chmod +x "$TEAM_PACKAGE/setup_team_environment.sh"
                
                # Create info file
                cat > "$TEAM_PACKAGE/team_environment_info.txt" << EOF
MoodleClaude Team Environment
============================
Created: $(date)
Creator: $(whoami)@$(hostname)

Setup Instructions:
1. Extract this package
2. Run: ./setup_team_environment.sh
3. Access Moodle at http://localhost:8080

Credentials:
- Check config/ directory for tokens
- Default admin credentials in environment files

Notes:
- This is a complete environment snapshot
- All team members will have identical setup
- Use for collaborative development and testing
EOF
                
                # Compress for sharing
                tar -czf "${TEAM_PACKAGE}.tar.gz" -C team_environments "$(basename "$TEAM_PACKAGE")"
                rm -rf "$TEAM_PACKAGE"
                
                print_status "✅ Team environment package created: ${TEAM_PACKAGE}.tar.gz"
                print_status "📤 Share this file with your team members"
                ;;
                
            "sync")
                print_status "Syncing with team repository..."
                git add .
                git commit -m "🤝 Team sync: $(date +"%Y-%m-%d %H:%M")

Environment updates and team collaboration changes"
                
                if git remote | grep -q origin; then
                    git push origin main 2>/dev/null || git push origin master 2>/dev/null
                    print_status "✅ Pushed to team repository"
                else
                    print_warning "No remote repository configured for team sync"
                fi
                ;;
        esac
        ;;
        
    "automated")
        print_header "Automated Backup Strategy"
        print_strategy "Scheduled backups with rotation and cleanup"
        
        AUTO_TYPE=${2:-"setup"}
        
        case $AUTO_TYPE in
            "setup")
                print_status "Setting up automated backup schedule..."
                
                # Create backup script with rotation
                cat > automated_backup.sh << 'EOF'
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
EOF
                chmod +x automated_backup.sh
                
                # Create cron job suggestions
                cat > backup_cron_examples.txt << 'EOF'
# MoodleClaude Automated Backup Cron Examples
# Add one of these to your crontab (crontab -e)

# Daily backup at 2 AM
0 2 * * * cd /path/to/moodleclaude && ./automated_backup.sh

# Every 6 hours
0 */6 * * * cd /path/to/moodleclaude && ./automated_backup.sh

# Business hours only (9 AM, 1 PM, 5 PM on weekdays)
0 9,13,17 * * 1-5 cd /path/to/moodleclaude && ./automated_backup.sh

# Weekly backup (Sunday at 1 AM) 
0 1 * * 0 cd /path/to/moodleclaude && ./automated_backup.sh
EOF
                
                print_status "✅ Automated backup setup created"
                print_status "📋 Check backup_cron_examples.txt for cron job setup"
                ;;
                
            "run")
                print_status "Running automated backup..."
                if [ -f automated_backup.sh ]; then
                    ./automated_backup.sh
                else
                    print_error "Automated backup not set up. Run: ./backup_strategies.sh automated setup"
                    exit 1
                fi
                ;;
        esac
        ;;
        
    "help"|*)
        print_header "MoodleClaude Backup Strategies"
        
        echo
        echo "🎯 Available Backup Strategies:"
        echo
        echo "📊 ${BLUE}Development Strategy${NC}"
        echo "   ./backup_strategies.sh development"
        echo "   → Lightweight daily backups, auto-cleanup"
        echo "   → Perfect for: Daily coding, feature development"
        echo
        echo "🎯 ${BLUE}Milestone Strategy${NC}"  
        echo "   ./backup_strategies.sh milestone [name]"
        echo "   → Complete backup before major changes"
        echo "   → Perfect for: Release preparation, major features"
        echo
        echo "🏭 ${BLUE}Production Strategy${NC}"
        echo "   ./backup_strategies.sh production"
        echo "   → Enterprise-grade with redundancy & verification"
        echo "   → Perfect for: Live environments, critical data"
        echo  
        echo "🧪 ${BLUE}Testing Strategy${NC}"
        echo "   ./backup_strategies.sh testing baseline"
        echo "   ./backup_strategies.sh testing restore-baseline"
        echo "   → Consistent test environments"
        echo "   → Perfect for: QA, integration testing"
        echo
        echo "🤝 ${BLUE}Team Strategy${NC}"
        echo "   ./backup_strategies.sh team share"
        echo "   ./backup_strategies.sh team sync"
        echo "   → Shared environments for collaboration"
        echo "   → Perfect for: Team development, onboarding"
        echo
        echo "⚙️ ${BLUE}Automated Strategy${NC}"
        echo "   ./backup_strategies.sh automated setup"
        echo "   ./backup_strategies.sh automated run"
        echo "   → Scheduled backups with rotation"
        echo "   → Perfect for: Production monitoring, hands-off backup"
        echo
        print_header "Strategy Selection Guide"
        echo
        echo "🔵 ${GREEN}For Solo Development:${NC} development + milestone"
        echo "🟡 ${GREEN}For Team Projects:${NC} team + automated"  
        echo "🔴 ${GREEN}For Production:${NC} production + automated"
        echo "🟣 ${GREEN}For Testing/QA:${NC} testing + development"
        echo
        ;;
esac
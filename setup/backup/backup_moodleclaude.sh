#!/bin/bash
# MoodleClaude v3.0 - Container Backup System
# Erstellt Backups von Docker Containern und Datenbanken

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

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="moodleclaude_${TIMESTAMP}"

# Container names (detect which setup is running)
if docker ps --format "table {{.Names}}" | grep -q "moodleclaude_app_fresh"; then
    SETUP_TYPE="fresh"
    MOODLE_CONTAINER="moodleclaude_app_fresh"
    POSTGRES_CONTAINER="moodleclaude_postgres_fresh"
    PGADMIN_CONTAINER="moodleclaude_pgadmin_fresh"
    DB_NAME="moodle_fresh"
    DB_USER="moodle"
    DB_PASSWORD="MoodleFresh2025!"
elif docker ps --format "table {{.Names}}" | grep -q "moodleclaude_app_v3"; then
    SETUP_TYPE="full"
    MOODLE_CONTAINER="moodleclaude_app_v3"
    POSTGRES_CONTAINER="moodleclaude_postgres_v3"
    PGADMIN_CONTAINER="moodleclaude_pgadmin_v3"
    DB_NAME="moodle"
    DB_USER="moodle" 
    DB_PASSWORD="MoodleClaude2025SecurePassword!"
elif docker ps --format "table {{.Names}}" | grep -q "moodleclaude_app_opt"; then
    SETUP_TYPE="optimized"
    MOODLE_CONTAINER="moodleclaude_app_opt"
    POSTGRES_CONTAINER="moodleclaude_db_opt"
    PGADMIN_CONTAINER=""
    DB_NAME="moodle"
    DB_USER="moodle"
    DB_PASSWORD="moodle123"
else
    print_error "No running MoodleClaude containers found!"
    echo "Please start MoodleClaude first:"
    echo "  ./setup_fresh_moodleclaude_complete.sh"
    exit 1
fi

echo "🔄 MoodleClaude Container Backup System"
echo "======================================"
print_status "Detected setup type: $SETUP_TYPE"
print_status "Backup name: $BACKUP_NAME"

# Create backup directory
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"
cd "$BACKUP_DIR/$BACKUP_NAME"

print_header "Step 1: Container Information"

# Save container information
print_status "Saving container metadata..."
cat > container_info.json << EOF
{
    "backup_timestamp": "$TIMESTAMP",
    "setup_type": "$SETUP_TYPE",
    "containers": {
        "moodle": "$MOODLE_CONTAINER",
        "postgres": "$POSTGRES_CONTAINER",
        "pgadmin": "$PGADMIN_CONTAINER"
    },
    "database": {
        "name": "$DB_NAME",
        "user": "$DB_USER"
    }
}
EOF

# Save docker-compose configuration
print_status "Saving Docker Compose configuration..."
if [ "$SETUP_TYPE" = "fresh" ]; then
    cp ../../docker-compose.fresh.yml ./docker-compose.yml
elif [ "$SETUP_TYPE" = "full" ]; then
    cp ../../docker-compose.new.yml ./docker-compose.yml
else
    cp ../../docker-compose.optimized.yml ./docker-compose.yml
fi

print_header "Step 2: Database Backup"

# PostgreSQL Database Dump
print_status "Creating PostgreSQL database dump..."
docker exec "$POSTGRES_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" --clean --create --if-exists > database_dump.sql

# Verify database dump
DB_SIZE=$(wc -l < database_dump.sql)
print_status "Database dump created: $DB_SIZE lines"

print_header "Step 3: Moodle Files Backup"

# Backup Moodle application files
print_status "Backing up Moodle application files..."
docker exec "$MOODLE_CONTAINER" tar -czf /tmp/moodle_files.tar.gz -C /opt/bitnami/moodle . 2>/dev/null
docker cp "$MOODLE_CONTAINER":/tmp/moodle_files.tar.gz ./moodle_files.tar.gz
docker exec "$MOODLE_CONTAINER" rm -f /tmp/moodle_files.tar.gz

# Backup Moodle data directory
print_status "Backing up Moodle data directory..."
docker exec "$MOODLE_CONTAINER" tar -czf /tmp/moodle_data.tar.gz -C /bitnami/moodledata . 2>/dev/null
docker cp "$MOODLE_CONTAINER":/tmp/moodle_data.tar.gz ./moodle_data.tar.gz
docker exec "$MOODLE_CONTAINER" rm -f /tmp/moodle_data.tar.gz

print_header "Step 4: Configuration Backup"

# Backup configuration files
print_status "Backing up configuration files..."
mkdir -p config
cp -r ../../config/* ./config/ 2>/dev/null || true

# Backup plugin files
print_status "Backing up MoodleClaude plugin..."
docker exec "$MOODLE_CONTAINER" tar -czf /tmp/plugin_files.tar.gz -C /opt/bitnami/moodle/local . 2>/dev/null
docker cp "$MOODLE_CONTAINER":/tmp/plugin_files.tar.gz ./plugin_files.tar.gz
docker exec "$MOODLE_CONTAINER" rm -f /tmp/plugin_files.tar.gz

print_header "Step 5: Container Images Backup"

# Save Docker images
print_status "Saving Docker images..."
docker save postgres:16-alpine | gzip > postgres_image.tar.gz
docker save bitnami/moodle:4.3 | gzip > moodle_image.tar.gz
if [ "$PGADMIN_CONTAINER" != "" ]; then
    docker save dpage/pgadmin4:latest | gzip > pgadmin_image.tar.gz
fi

print_header "Step 6: Environment Snapshot"

# Create environment snapshot
print_status "Creating environment snapshot..."
cat > environment_snapshot.txt << EOF
# MoodleClaude Environment Snapshot
# Created: $(date)

## System Information
Docker Version: $(docker --version)
Docker Compose Version: $(docker-compose --version)
Host OS: $(uname -a)

## Container Status
$(docker ps --filter name=moodleclaude --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}")

## Container Sizes
$(docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}")

## Setup Type: $SETUP_TYPE

## Database Info
Database: $DB_NAME
User: $DB_USER
Tables Count: $(docker exec "$POSTGRES_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ' || echo "N/A")

## Moodle Info
$(curl -s "http://localhost:8080" | grep -o '<title>.*</title>' || echo "Moodle Status: Not accessible")
EOF

print_header "Step 7: Backup Verification"

# Calculate backup sizes and create manifest
print_status "Creating backup manifest..."
cat > backup_manifest.txt << EOF
# MoodleClaude Backup Manifest
# Backup Name: $BACKUP_NAME
# Created: $(date)
# Setup Type: $SETUP_TYPE

## Files and Sizes:
$(ls -lh | tail -n +2)

## Total Backup Size:
$(du -sh . | cut -f1)

## Checksums:
$(find . -type f -name "*.sql" -o -name "*.tar.gz" -o -name "*.json" | xargs sha256sum)
EOF

# Return to project root
cd ../../

print_header "Backup Complete!"

BACKUP_SIZE=$(du -sh "$BACKUP_DIR/$BACKUP_NAME" | cut -f1)
print_status "✅ Backup created successfully!"
echo
echo "📦 Backup Information:"
echo "  📂 Location: $BACKUP_DIR/$BACKUP_NAME"
echo "  📊 Size: $BACKUP_SIZE"
echo "  🎯 Setup Type: $SETUP_TYPE"
echo "  🕐 Timestamp: $TIMESTAMP"
echo
echo "📋 Backup Contents:"
echo "  ✅ PostgreSQL Database ($DB_NAME)"
echo "  ✅ Moodle Application Files"
echo "  ✅ Moodle Data Directory"
echo "  ✅ MoodleClaude Plugin"
echo "  ✅ Configuration Files"
echo "  ✅ Docker Images"
echo "  ✅ Environment Snapshot"
echo
print_header "Usage"
echo "To restore this backup:"
echo "  ./restore_moodleclaude.sh $BACKUP_NAME"
echo
echo "To list all backups:"
echo "  ./list_backups.sh"
echo
print_status "Backup process completed! 🎉"
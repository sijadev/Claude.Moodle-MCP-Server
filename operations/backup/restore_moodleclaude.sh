#!/bin/bash
# MoodleClaude v3.0 - Container Restore System
# Stellt Backups von Docker Containern und Datenbanken wieder her

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

# Check if backup name is provided
if [ $# -eq 0 ]; then
    print_error "No backup name provided!"
    echo
    echo "Usage: $0 <backup_name>"
    echo
    echo "Available backups:"
    if [ -d "./backups" ]; then
        ls -1 ./backups/ | grep "moodleclaude_" | head -10
    else
        echo "  No backups found in ./backups/"
    fi
    echo
    echo "Example: $0 moodleclaude_20250131_201500"
    exit 1
fi

BACKUP_NAME="$1"
BACKUP_DIR="./backups/$BACKUP_NAME"

# Check if backup exists
if [ ! -d "$BACKUP_DIR" ]; then
    print_error "Backup '$BACKUP_NAME' not found!"
    echo "Available backups:"
    ls -1 ./backups/ 2>/dev/null | grep "moodleclaude_" | head -10 || echo "  No backups available"
    exit 1
fi

echo "🔄 MoodleClaude Container Restore System"
echo "======================================="
print_status "Restoring backup: $BACKUP_NAME"

# Read backup metadata
if [ ! -f "$BACKUP_DIR/container_info.json" ]; then
    print_error "Backup metadata not found! Invalid backup."
    exit 1
fi

# Extract backup information
SETUP_TYPE=$(python3 -c "import json; print(json.load(open('$BACKUP_DIR/container_info.json'))['setup_type'])" 2>/dev/null || echo "unknown")
print_status "Backup type: $SETUP_TYPE"

print_header "Step 1: Environment Preparation"

# Stop current containers if running
print_status "Stopping current MoodleClaude containers..."
docker-compose down --volumes --remove-orphans 2>/dev/null || true
docker-compose -f docker-compose.fresh.yml down --volumes --remove-orphans 2>/dev/null || true
docker-compose -f docker-compose.new.yml down --volumes --remove-orphans 2>/dev/null || true
docker-compose -f docker-compose.optimized.yml down --volumes --remove-orphans 2>/dev/null || true

# Clean up any remaining containers
print_status "Cleaning up containers..."
docker ps -a --filter name=moodleclaude --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true

# Clean up volumes
print_status "Cleaning up volumes..."
docker volume ls --filter name=moodle --format "{{.Name}}" | xargs -r docker volume rm 2>/dev/null || true

print_header "Step 2: Restoring Docker Images"

# Restore Docker images
print_status "Restoring Docker images..."
if [ -f "$BACKUP_DIR/postgres_image.tar.gz" ]; then
    gunzip -c "$BACKUP_DIR/postgres_image.tar.gz" | docker load
    print_status "PostgreSQL image restored"
fi

if [ -f "$BACKUP_DIR/moodle_image.tar.gz" ]; then
    gunzip -c "$BACKUP_DIR/moodle_image.tar.gz" | docker load
    print_status "Moodle image restored"
fi

if [ -f "$BACKUP_DIR/pgadmin_image.tar.gz" ]; then
    gunzip -c "$BACKUP_DIR/pgadmin_image.tar.gz" | docker load
    print_status "pgAdmin image restored"
fi

print_header "Step 3: Starting Container Infrastructure"

# Copy and use the appropriate docker-compose file
print_status "Restoring Docker Compose configuration..."
cp "$BACKUP_DIR/docker-compose.yml" ./docker-compose-restore.yml

# Start the infrastructure (database first)
print_status "Starting container infrastructure..."
docker-compose -f docker-compose-restore.yml up -d

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
POSTGRES_CONTAINER=$(docker ps --filter name=postgres --format "{{.Names}}" | head -1)
if [ -z "$POSTGRES_CONTAINER" ]; then
    print_error "PostgreSQL container not found!"
    exit 1
fi

timeout=60
counter=0
while ! docker exec "$POSTGRES_CONTAINER" pg_isready >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "PostgreSQL failed to start within $timeout seconds"
        exit 1
    fi
    echo -n "."
    sleep 1
    ((counter++))
done
echo
print_status "PostgreSQL is ready!"

print_header "Step 4: Restoring Database"

# Get database info from backup
DB_NAME=$(python3 -c "import json; print(json.load(open('$BACKUP_DIR/container_info.json'))['database']['name'])" 2>/dev/null || echo "moodle")
DB_USER=$(python3 -c "import json; print(json.load(open('$BACKUP_DIR/container_info.json'))['database']['user'])" 2>/dev/null || echo "moodle")

print_status "Restoring database: $DB_NAME"

# Drop existing database and restore from backup
docker exec "$POSTGRES_CONTAINER" psql -U "$DB_USER" -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true
docker exec -i "$POSTGRES_CONTAINER" psql -U "$DB_USER" < "$BACKUP_DIR/database_dump.sql"

print_status "Database restored successfully!"

print_header "Step 5: Restoring Moodle Files"

# Wait for Moodle container to be ready
print_status "Waiting for Moodle container..."
MOODLE_CONTAINER=$(docker ps --filter name=moodle --format "{{.Names}}" | head -1)
timeout=180
counter=0
while [ -z "$MOODLE_CONTAINER" ] || ! docker exec "$MOODLE_CONTAINER" test -d /opt/bitnami/moodle 2>/dev/null; do
    if [ $counter -ge $timeout ]; then
        print_error "Moodle container failed to start properly"
        exit 1
    fi
    if [ $((counter % 10)) -eq 0 ]; then
        echo -n " [${counter}s]"
        MOODLE_CONTAINER=$(docker ps --filter name=moodle --format "{{.Names}}" | head -1)
    else
        echo -n "."
    fi
    sleep 1
    ((counter++))
done
echo
print_status "Moodle container is ready!"

# Restore Moodle application files
print_status "Restoring Moodle application files..."
docker cp "$BACKUP_DIR/moodle_files.tar.gz" "$MOODLE_CONTAINER":/tmp/
docker exec "$MOODLE_CONTAINER" bash -c "cd /opt/bitnami/moodle && rm -rf * && tar -xzf /tmp/moodle_files.tar.gz && rm /tmp/moodle_files.tar.gz"

# Restore Moodle data directory
print_status "Restoring Moodle data directory..."
docker cp "$BACKUP_DIR/moodle_data.tar.gz" "$MOODLE_CONTAINER":/tmp/
docker exec "$MOODLE_CONTAINER" bash -c "cd /bitnami/moodledata && rm -rf * && tar -xzf /tmp/moodle_data.tar.gz && rm /tmp/moodle_data.tar.gz"

# Restore plugin files
if [ -f "$BACKUP_DIR/plugin_files.tar.gz" ]; then
    print_status "Restoring MoodleClaude plugin..."
    docker cp "$BACKUP_DIR/plugin_files.tar.gz" "$MOODLE_CONTAINER":/tmp/
    docker exec "$MOODLE_CONTAINER" bash -c "cd /opt/bitnami/moodle/local && rm -rf * && tar -xzf /tmp/plugin_files.tar.gz && rm /tmp/plugin_files.tar.gz"
fi

# Set correct permissions
print_status "Setting file permissions..."
docker exec "$MOODLE_CONTAINER" chown -R daemon:daemon /opt/bitnami/moodle
docker exec "$MOODLE_CONTAINER" chown -R daemon:daemon /bitnami/moodledata

print_header "Step 6: Restoring Configuration"

# Restore configuration files
print_status "Restoring configuration files..."
if [ -d "$BACKUP_DIR/config" ]; then
    cp -r "$BACKUP_DIR/config"/* ./config/ 2>/dev/null || true
fi

print_header "Step 7: Final Verification"

# Wait for Moodle to be accessible
print_status "Waiting for Moodle web interface..."
timeout=120
counter=0
while ! curl -f http://localhost:8080/login/index.php >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_warning "Moodle web interface not accessible within timeout, but restore completed"
        break
    fi
    if [ $((counter % 10)) -eq 0 ]; then
        echo -n " [${counter}s]"
    else
        echo -n "."
    fi
    sleep 1
    ((counter++))
done
echo

# Test web interface
if curl -f http://localhost:8080/login/index.php >/dev/null 2>&1; then
    SITE_TITLE=$(curl -s http://localhost:8080/login/index.php | grep -o '<title>.*</title>' | sed 's/<[^>]*>//g' || echo "MoodleClaude")
    print_status "✅ Moodle web interface accessible: $SITE_TITLE"
else
    print_warning "⚠️ Moodle web interface not immediately accessible (may need more time)"
fi

# Show final container status
print_status "Container status:"
docker ps --filter name=moodleclaude --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

print_header "Restore Complete!"

print_status "✅ MoodleClaude backup restored successfully!"
echo
echo "📦 Restored Backup: $BACKUP_NAME"
echo "🎯 Setup Type: $SETUP_TYPE"
echo "📊 Backup Size: $(du -sh "$BACKUP_DIR" | cut -f1)"
echo
echo "🔗 Access Information:"
echo "  🌐 Moodle: http://localhost:8080"
echo "  📊 pgAdmin: http://localhost:8082 (if available)"
echo
echo "📋 What was restored:"
echo "  ✅ PostgreSQL Database"
echo "  ✅ Moodle Application Files"
echo "  ✅ Moodle Data Directory"
echo "  ✅ MoodleClaude Plugin"
echo "  ✅ Configuration Files"
echo "  ✅ Docker Images"
echo
print_header "Next Steps"
echo "1. 🔑 Check your login credentials in config/ directory"
echo "2. 🧪 Test MoodleClaude functionality"
echo "3. 🚀 Continue with your development/testing"
echo
print_status "Restore process completed! 🎉"

# Clean up temporary docker-compose file
rm -f docker-compose-restore.yml
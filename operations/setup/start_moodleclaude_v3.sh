#!/bin/bash
# MoodleClaude v3.0 - Optimized Startup Script
# Verwendet das optimierte 2-Container Setup

set -e

echo "🚀 Starting MoodleClaude v3.0 Optimized Environment..."
echo "=================================================="

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

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Clean up any existing containers
print_header "Cleaning up existing environment"
if docker ps -a --format 'table {{.Names}}' | grep -E 'moodleclaude_' > /dev/null 2>&1; then
    print_warning "Found existing MoodleClaude containers. Stopping them..."
    docker-compose down --volumes --remove-orphans 2>/dev/null || true
fi

# Start optimized environment
print_header "Starting MoodleClaude v3.0 Optimized Services"
print_status "Configuration: PostgreSQL + Moodle (2 containers)"
print_status "Starting containers..."

docker-compose up -d

# Wait for services to be healthy
print_header "Waiting for services to start"

print_status "Waiting for PostgreSQL..."
timeout=30
counter=0
while ! docker exec moodleclaude_db_opt pg_isready -U moodle -d moodle >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "PostgreSQL failed to start within $timeout seconds"
        exit 1
    fi
    echo -n "."
    sleep 1
    ((counter++))
done
print_status "PostgreSQL is ready!"

print_status "Waiting for Moodle application (this may take 2-3 minutes)..."
timeout=180
counter=0
while ! curl -f http://localhost:8080/login/index.php >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Moodle failed to start within $timeout seconds"
        print_status "Check logs: docker-compose logs moodle"
        exit 1
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
print_status "Moodle is ready!"

# Display service information
print_header "Service Information"
echo
echo "🎯 Moodle Application:"
echo "   URL: http://localhost:8080"
echo "   Admin User: admin"
echo "   Admin Password: MoodleClaude2025Admin!"
echo "   Site Name: MoodleClaude v3.0 Optimized"
echo
echo "🗄️  Database (PostgreSQL):"
echo "   Host: localhost (internal)"
echo "   Database: moodle"
echo "   User: moodle"
echo "   Password: moodle123"
echo "   Note: Database is only accessible from within Docker network"
echo
echo "📊 Container Resources:"
echo "   PHP Memory: 384M"
echo "   Upload Limit: 64M"
echo "   Execution Time: 240s"
echo

print_header "Next Steps"
echo "1. 🌐 Open Moodle: http://localhost:8080"
echo "2. 🔑 Login with admin/MoodleClaude2025Admin!"
echo "3. 🔧 Configure Web Services for MCP integration"
echo "4. 🧪 Test MoodleClaude v3.0 architecture"
echo

print_header "Useful Commands"
echo "📋 View logs: docker-compose logs -f [service]"
echo "🛑 Stop services: docker-compose down"
echo "🔄 Restart service: docker-compose restart [service]"
echo "💽 Clean data: docker-compose down --volumes"
echo "📈 Container stats: docker stats"
echo

print_status "MoodleClaude v3.0 Optimized Environment is ready! 🎉"
echo "=================================================="
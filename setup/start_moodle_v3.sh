#!/bin/bash
# MoodleClaude v3.0 - Docker Environment Startup Script

set -e

echo "🚀 Starting MoodleClaude v3.0 Docker Environment..."
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function for colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1" 
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if old containers are running
print_header "Cleaning up old environment"
if docker ps -a --format 'table {{.Names}}' | grep -E 'moodleclaude_(db|app|phpmyadmin)' > /dev/null 2>&1; then
    print_warning "Found old MoodleClaude containers. Stopping them..."
    docker-compose -f docker-compose.yml down --volumes --remove-orphans 2>/dev/null || true
fi

# Start new environment
print_header "Starting MoodleClaude v3.0 Services"
print_status "Using docker-compose.new.yml configuration..."

docker-compose -f docker-compose.new.yml up -d

# Wait for services to be healthy
print_header "Waiting for services to start"

print_status "Waiting for PostgreSQL..."
timeout=60
counter=0
while ! docker exec moodleclaude_postgres_v3 pg_isready -U moodle -d moodle >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "PostgreSQL failed to start within $timeout seconds"
        exit 1
    fi
    echo -n "."
    sleep 1
    ((counter++))
done
print_status "PostgreSQL is ready!"

print_status "Waiting for Redis..."
timeout=30
counter=0
while ! docker exec moodleclaude_redis_v3 redis-cli ping >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Redis failed to start within $timeout seconds"
        exit 1
    fi
    echo -n "."
    sleep 1
    ((counter++))
done
print_status "Redis is ready!"

print_status "Waiting for Moodle application (this may take 2-3 minutes)..."
timeout=300
counter=0
while ! curl -f http://localhost:8080/login/index.php >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Moodle failed to start within $timeout seconds"
        print_status "Check logs: docker-compose -f docker-compose.new.yml logs moodle"
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
echo
echo "🗄️  Database (PostgreSQL):"
echo "   Host: localhost:5432"
echo "   Database: moodle"
echo "   User: moodle"
echo "   Password: MoodleClaude2025SecurePassword!"
echo
echo "🔧 Database Admin (pgAdmin):"
echo "   URL: http://localhost:8082"
echo "   Email: admin@moodleclaude.local"  
echo "   Password: MoodleClaude2025Admin!"
echo
echo "📧 Mail Testing (MailHog):"
echo "   SMTP: localhost:1025"
echo "   Web UI: http://localhost:8025"
echo
echo "🚀 Redis Cache:"
echo "   Host: localhost:6379"
echo "   Password: MoodleClaudeRedis2025!"
echo "   Web UI: http://localhost:8083"
echo

print_header "Next Steps"
echo "1. 🌐 Open Moodle: http://localhost:8080"
echo "2. 🔑 Login with admin/MoodleClaude2025Admin!"
echo "3. 🔧 Configure Web Services (see setup_webservices.sh)"
echo "4. 🧪 Test MoodleClaude integration"
echo

print_header "Useful Commands"
echo "📋 View logs: docker-compose -f docker-compose.new.yml logs -f [service]"
echo "🛑 Stop services: docker-compose -f docker-compose.new.yml down"
echo "🔄 Restart service: docker-compose -f docker-compose.new.yml restart [service]"
echo "💽 Clean volumes: docker-compose -f docker-compose.new.yml down --volumes"
echo

print_status "MoodleClaude v3.0 environment is ready! 🎉"
echo "=========================================="
#!/bin/bash

# MoodleClaude Custom Web Service Setup Script
# ============================================
# 
# This script automates the creation of a dedicated MoodleClaude web service
# instead of using the mobile app service that causes external_functions errors.
#
# Usage: ./create_custom_webservice.sh

set -e

echo "🚀 MoodleClaude Custom Web Service Setup"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Check if .env file exists
ENV_FILE="$PROJECT_ROOT/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    echo -e "${RED}❌ .env file not found: $ENV_FILE${NC}"
    echo "Please create a .env file with your Moodle configuration"
    exit 1
fi

echo -e "${GREEN}✅ Found .env file${NC}"

# Source environment variables
set -a
source "$ENV_FILE"
set +a

# Check required environment variables
if [[ -z "$MOODLE_URL" ]]; then
    echo -e "${RED}❌ MOODLE_URL not set in .env file${NC}"
    exit 1
fi

if [[ -z "$MOODLE_ADMIN_PASSWORD" ]]; then
    echo -e "${RED}❌ MOODLE_ADMIN_PASSWORD not set in .env file${NC}"
    echo "Please add MOODLE_ADMIN_PASSWORD to your .env file"
    exit 1
fi

echo -e "${GREEN}✅ Environment variables configured${NC}"
echo -e "${BLUE}   • Moodle URL: $MOODLE_URL${NC}"
echo -e "${BLUE}   • Admin User: ${MOODLE_ADMIN_USER:-admin}${NC}"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 available${NC}"

# Check if PHP is available (for direct execution)
PHP_AVAILABLE=false
if command -v php &> /dev/null; then
    PHP_AVAILABLE=true
    echo -e "${GREEN}✅ PHP available${NC}"
else
    echo -e "${YELLOW}⚠️  PHP not found locally - will try Docker approach${NC}"
fi

echo ""
echo -e "${BLUE}🔧 Starting web service creation...${NC}"
echo ""

# Method 1: Enhanced setup (preferred)
echo "📋 Method 1: Enhanced setup with dashboard reporting"
if python3 "$SCRIPT_DIR/enhanced_webservice_setup.py"; then
    echo ""
    echo -e "${GREEN}🎉 SUCCESS! Enhanced custom web service created successfully!${NC}"
    echo ""
    echo -e "${YELLOW}📊 Enhanced Features Activated:${NC}"
    echo "   • Dashboard-style progress reporting"
    echo "   • Function availability validation"
    echo "   • Performance testing and monitoring"
    echo "   • Comprehensive error logging"
    echo "   • Security validation"
    echo ""
    echo -e "${YELLOW}📝 Next steps:${NC}"
    echo "   1. Review the setup dashboard above"
    echo "   2. Check setup logs in tools/setup/setup_log.json"
    echo "   3. Restart your MCP server if it's running"
    echo "   4. Test with Claude Desktop"
    echo "   5. Use the 'diagnose_webservices' tool to verify"
    echo ""
    echo -e "${GREEN}✨ All MoodleClaude functions should now work without external_functions errors!${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}⚠️  Enhanced method failed, trying standard approach...${NC}"
echo ""

# Method 2: Standard Python execution (fallback)
echo "📋 Method 2: Standard setup via Python"
if python3 "$SCRIPT_DIR/setup_custom_webservice.py"; then
    echo ""
    echo -e "${GREEN}🎉 SUCCESS! Custom web service created successfully!${NC}"
    echo ""
    echo -e "${YELLOW}📝 Next steps:${NC}"
    echo "   1. Restart your MCP server if it's running"
    echo "   2. Test with Claude Desktop"
    echo "   3. Use the 'diagnose_webservices' tool to verify"
    echo ""
    echo -e "${GREEN}✨ All MoodleClaude functions should now work without external_functions errors!${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}⚠️  Python method failed, trying alternative approaches...${NC}"
echo ""

# Method 3: Direct PHP execution (if available)
if [[ "$PHP_AVAILABLE" == "true" ]]; then
    echo "📋 Method 3: Direct PHP execution"
    
    # Check if we're in a Moodle environment or need to use Docker
    PHP_SCRIPT="$SCRIPT_DIR/create_moodleclaude_webservice.php"
    
    if php "$PHP_SCRIPT"; then
        echo ""
        echo -e "${GREEN}🎉 SUCCESS! Custom web service created via PHP!${NC}"
        
        # Run Python script just for environment update and testing
        echo "🔧 Updating environment and testing..."
        if python3 -c "
import sys
sys.path.append('$SCRIPT_DIR')
from setup_custom_webservice import MoodleWebServiceSetup
setup = MoodleWebServiceSetup()
config = setup.load_config()
setup.update_environment(config)
setup.test_webservice(config)
setup.print_success_summary(config)
"; then
            echo -e "${GREEN}✅ Environment updated and tested${NC}"
        fi
        exit 0
    fi
fi

echo ""
echo -e "${YELLOW}⚠️  Direct execution failed, trying Docker approach...${NC}"
echo ""

# Method 4: Docker execution (fallback)
echo "📋 Method 4: Docker-based execution"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found - no more fallback options${NC}"
    echo ""
    echo -e "${YELLOW}🔧 Manual Setup Required:${NC}"
    echo "   1. Copy $SCRIPT_DIR/create_moodleclaude_webservice.php to your Moodle server"
    echo "   2. Run: php create_moodleclaude_webservice.php"
    echo "   3. Update your .env file with the generated token"
    echo "   4. Restart your MCP server"
    exit 1
fi

# Try to use existing Moodle container
MOODLE_CONTAINER=$(docker ps --format "table {{.Names}}" | grep -i moodle | head -1 || true)

if [[ -n "$MOODLE_CONTAINER" ]]; then
    echo -e "${BLUE}🐳 Found Moodle container: $MOODLE_CONTAINER${NC}"
    
    # Copy PHP script to container
    if docker cp "$SCRIPT_DIR/create_moodleclaude_webservice.php" "$MOODLE_CONTAINER:/tmp/"; then
        echo -e "${GREEN}✅ Copied script to container${NC}"
        
        # Execute in container
        if docker exec "$MOODLE_CONTAINER" php /tmp/create_moodleclaude_webservice.php; then
            echo ""
            echo -e "${GREEN}🎉 SUCCESS! Custom web service created via Docker!${NC}"
            
            # Get the config file from container
            docker cp "$MOODLE_CONTAINER:/tmp/moodleclaude_webservice_config.json" "$SCRIPT_DIR/"
            
            # Update environment
            echo "🔧 Updating environment..."
            python3 -c "
import sys
sys.path.append('$SCRIPT_DIR')
from setup_custom_webservice import MoodleWebServiceSetup
setup = MoodleWebServiceSetup()
config = setup.load_config()
setup.update_environment(config)
setup.test_webservice(config)
setup.print_success_summary(config)
"
            exit 0
        fi
    fi
fi

echo ""
echo -e "${RED}❌ All automated methods failed${NC}"
echo ""
echo -e "${YELLOW}🔧 Manual Setup Instructions:${NC}"
echo "   1. Access your Moodle server with admin rights"
echo "   2. Copy the PHP script to your server:"
echo "      $SCRIPT_DIR/create_moodleclaude_webservice.php"
echo "   3. Run: php create_moodleclaude_webservice.php"
echo "   4. Copy the generated token to your .env file:"
echo "      MOODLE_TOKEN_ENHANCED=\"your_token_here\""
echo "   5. Restart your MCP server and test"
echo ""
echo -e "${BLUE}💡 This will solve all external_functions database errors!${NC}"

exit 1
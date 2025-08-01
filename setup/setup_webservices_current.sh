#!/bin/bash
# MoodleClaude v3.0 - Web Services Setup for Current Environment

set -e

echo "🔧 Setting up Moodle Web Services for MoodleClaude v3.0..."
echo "====================================================="

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

# Check if Moodle is running
if ! curl -f http://localhost:8080/login/index.php >/dev/null 2>&1; then
    print_error "Moodle is not accessible at http://localhost:8080"
    print_status "Please ensure Moodle is running: docker-compose up -d"
    exit 1
fi

print_status "Moodle is accessible at http://localhost:8080"

# Moodle CLI commands via Docker (using correct container name)
MOODLE_CLI="docker exec moodleclaude_app php /opt/bitnami/moodle/admin/cli"

print_header "Enabling Web Services"

# Enable web services
print_status "Enabling web services..."
$MOODLE_CLI/cfg.php --name=enablewebservices --set=1

# Enable REST protocol
print_status "Enabling REST protocol..."
$MOODLE_CLI/cfg.php --name=webserviceprotocols --set=rest

# Enable mobile services
print_status "Enabling mobile web services..."
$MOODLE_CLI/cfg.php --name=enablemobilewebservice --set=1

print_header "Creating Web Service Users and Roles"

# Create web service user
print_status "Creating web service user 'wsuser'..."
$MOODLE_CLI/user.php --create --username=wsuser --password=MoodleClaudeWS2025! \
    --email=wsuser@moodleclaude.local --firstname=WebService --lastname=User \
    --idnumber=wsuser001 --city=Local --country=US || true

# Create web service role with necessary capabilities using MariaDB
print_status "Setting up web service role and capabilities..."
WS_ROLE_SQL="
INSERT INTO mdl_role (name, shortname, description, sortorder, archetype) 
VALUES ('MoodleClaude Web Service', 'moodleclaude_ws', 'Role for MoodleClaude web service access', 1, '') 
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- Get role ID and assign capabilities
INSERT INTO mdl_role_capabilities (roleid, contextid, capability, permission, timemodified, modifierid)
SELECT r.id, 1, 'webservice/rest:use', 1, UNIX_TIMESTAMP(), 2
FROM mdl_role r WHERE r.shortname = 'moodleclaude_ws'
ON DUPLICATE KEY UPDATE permission = 1;

INSERT INTO mdl_role_capabilities (roleid, contextid, capability, permission, timemodified, modifierid)
SELECT r.id, 1, 'moodle/course:create', 1, UNIX_TIMESTAMP(), 2
FROM mdl_role r WHERE r.shortname = 'moodleclaude_ws'
ON DUPLICATE KEY UPDATE permission = 1;

INSERT INTO mdl_role_capabilities (roleid, contextid, capability, permission, timemodified, modifierid)
SELECT r.id, 1, 'moodle/course:update', 1, UNIX_TIMESTAMP(), 2
FROM mdl_role r WHERE r.shortname = 'moodleclaude_ws'
ON DUPLICATE KEY UPDATE permission = 1;

INSERT INTO mdl_role_capabilities (roleid, contextid, capability, permission, timemodified, modifierid)
SELECT r.id, 1, 'moodle/course:view', 1, UNIX_TIMESTAMP(), 2
FROM mdl_role r WHERE r.shortname = 'moodleclaude_ws'
ON DUPLICATE KEY UPDATE permission = 1;

-- Assign role to wsuser
INSERT INTO mdl_role_assignments (roleid, contextid, userid, timemodified, modifierid, component, itemid, sortorder)
SELECT r.id, 1, u.id, UNIX_TIMESTAMP(), 2, '', 0, 0
FROM mdl_role r, mdl_user u 
WHERE r.shortname = 'moodleclaude_ws' AND u.username = 'wsuser'
ON DUPLICATE KEY UPDATE timemodified = UNIX_TIMESTAMP();
"

# Execute SQL via MariaDB
echo "$WS_ROLE_SQL" | docker exec -i moodleclaude_db mysql -u bn_moodle bitnami_moodle

print_header "Creating Web Service and Tokens"

# Create external service 
SERVICE_SQL="
INSERT INTO mdl_external_services (name, shortname, component, timecreated, timemodified, enabled, restrictedusers, downloadfiles, uploadfiles)
VALUES ('MoodleClaude Service', 'moodleclaude', '', UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 1, 1, 1, 1)
ON DUPLICATE KEY UPDATE 
    enabled = 1, 
    restrictedusers = 1, 
    downloadfiles = 1, 
    uploadfiles = 1,
    timemodified = UNIX_TIMESTAMP();
"

echo "$SERVICE_SQL" | docker exec -i moodleclaude_db mysql -u bn_moodle bitnami_moodle

# Add functions to external service
FUNCTIONS_SQL="
-- Core course functions
INSERT INTO mdl_external_services_functions (externalserviceid, functionname)
SELECT es.id, 'core_course_create_courses'
FROM mdl_external_services es WHERE es.shortname = 'moodleclaude'
ON DUPLICATE KEY UPDATE functionname = VALUES(functionname);

INSERT INTO mdl_external_services_functions (externalserviceid, functionname)
SELECT es.id, 'core_course_get_courses'
FROM mdl_external_services es WHERE es.shortname = 'moodleclaude'
ON DUPLICATE KEY UPDATE functionname = VALUES(functionname);

INSERT INTO mdl_external_services_functions (externalserviceid, functionname)
SELECT es.id, 'core_course_get_categories'
FROM mdl_external_services es WHERE es.shortname = 'moodleclaude'
ON DUPLICATE KEY UPDATE functionname = VALUES(functionname);

INSERT INTO mdl_external_services_functions (externalserviceid, functionname)
SELECT es.id, 'core_course_update_courses'
FROM mdl_external_services es WHERE es.shortname = 'moodleclaude'
ON DUPLICATE KEY UPDATE functionname = VALUES(functionname);

-- Section management
INSERT INTO mdl_external_services_functions (externalserviceid, functionname)
SELECT es.id, 'core_course_edit_section'
FROM mdl_external_services es WHERE es.shortname = 'moodleclaude'
ON DUPLICATE KEY UPDATE functionname = VALUES(functionname);

-- Web service info
INSERT INTO mdl_external_services_functions (externalserviceid, functionname)
SELECT es.id, 'core_webservice_get_site_info'
FROM mdl_external_services es WHERE es.shortname = 'moodleclaude'
ON DUPLICATE KEY UPDATE functionname = VALUES(functionname);

-- File management
INSERT INTO mdl_external_services_functions (externalserviceid, functionname)
SELECT es.id, 'core_files_upload'
FROM mdl_external_services es WHERE es.shortname = 'moodleclaude'
ON DUPLICATE KEY UPDATE functionname = VALUES(functionname);
"

echo "$FUNCTIONS_SQL" | docker exec -i moodleclaude_db mysql -u bn_moodle bitnami_moodle

# Create tokens
print_status "Creating web service tokens..."

# Generate tokens
BASIC_TOKEN=$(openssl rand -hex 16)
PLUGIN_TOKEN=$(openssl rand -hex 16)

TOKEN_SQL="
-- Basic token
INSERT INTO mdl_external_tokens (token, tokentype, userid, externalserviceid, contextid, creatorid, timecreated, validuntil)
SELECT '${BASIC_TOKEN}', 0, u.id, es.id, 1, 2, UNIX_TIMESTAMP(), 0
FROM mdl_user u, mdl_external_services es
WHERE u.username = 'wsuser' AND es.shortname = 'moodleclaude'
ON DUPLICATE KEY UPDATE 
    token = '${BASIC_TOKEN}',
    timecreated = UNIX_TIMESTAMP();

-- Plugin token (for extended functionality)
INSERT INTO mdl_external_tokens (token, tokentype, userid, externalserviceid, contextid, creatorid, timecreated, validuntil)  
SELECT '${PLUGIN_TOKEN}', 0, u.id, es.id, 1, 2, UNIX_TIMESTAMP(), 0
FROM mdl_user u, mdl_external_services es
WHERE u.username = 'simon' AND es.shortname = 'moodleclaude'
ON DUPLICATE KEY UPDATE
    token = '${PLUGIN_TOKEN}',
    timecreated = UNIX_TIMESTAMP();
"

echo "$TOKEN_SQL" | docker exec -i moodleclaude_db mysql -u bn_moodle bitnami_moodle

print_header "Web Service Setup Complete"

echo
print_status "Web Services Configuration:"
echo "  📡 REST Protocol: ✅ Enabled"  
echo "  🔧 External Service: ✅ moodleclaude"
echo "  👤 WS User: wsuser / MoodleClaudeWS2025!"
echo "  🔑 Basic Token: ${BASIC_TOKEN}"
echo "  🔑 Plugin Token: ${PLUGIN_TOKEN}"
echo

print_header "Updating MoodleClaude Configuration"

# Create config directory if it doesn't exist
mkdir -p config

# Update configuration files
print_status "Updating token configuration..."

# Create new configuration
cat > config/moodle_tokens_current.env << EOF
# MoodleClaude v3.0 - Generated Tokens (Current Environment)
MOODLE_URL=http://localhost:8080
MOODLE_BASIC_TOKEN=${BASIC_TOKEN}
MOODLE_PLUGIN_TOKEN=${PLUGIN_TOKEN}
MOODLE_USERNAME=wsuser
MOODLE_WS_USER=wsuser
MOODLE_WS_PASSWORD=MoodleClaudeWS2025!
MOODLE_ADMIN_USER=simon
MOODLE_ADMIN_PASSWORD=Pwd1234!

# Database Connection (MariaDB)
MARIADB_HOST=localhost
MARIADB_PORT=3306
MARIADB_DB=bitnami_moodle
MARIADB_USER=bn_moodle
MARIADB_PASSWORD=
EOF

print_status "Configuration saved to: config/moodle_tokens_current.env"

print_header "Testing Web Service Access"

# Test basic connectivity
print_status "Testing web service connectivity..."
WS_TEST_URL="http://localhost:8080/webservice/rest/server.php?wstoken=${BASIC_TOKEN}&wsfunction=core_webservice_get_site_info&moodlewsrestformat=json"

if curl -s "$WS_TEST_URL" | grep -q '"sitename"'; then
    print_status "✅ Web service test successful!"
    SITE_NAME=$(curl -s "$WS_TEST_URL" | python3 -c "import sys, json; print(json.load(sys.stdin).get('sitename', 'Unknown'))" 2>/dev/null || echo "MoodleClaude Test Environment")
    echo "    Site: $SITE_NAME"
else
    print_warning "⚠️ Web service test failed - may need manual verification"
fi

print_header "Next Steps"
echo "1. 🔄 Update Claude Desktop configuration with these tokens"
echo "2. 🧪 Test MoodleClaude integration with the new architecture"
echo "3. 🚀 Use MCP tools in Claude Desktop"
echo

print_status "Web Services setup complete! 🎉" 
echo "====================================================="
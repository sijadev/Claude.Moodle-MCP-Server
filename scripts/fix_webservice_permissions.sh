#!/bin/bash
#
# Fix web service permissions to allow token creation
#

set -e

MOODLE_NETWORK="moodleclaude_moodle_network"
MOODLE_DB_HOST="mariadb"
MOODLE_DB_NAME="bitnami_moodle"
MOODLE_DB_USER="bn_moodle"

echo "🔧 Fixing Moodle Web Service Permissions"
echo "========================================"

# Execute MySQL command via Docker
mysql_exec() {
    local sql="$1"
    docker run --rm --network "$MOODLE_NETWORK" mysql:8.0 mysql -h"$MOODLE_DB_HOST" -u"$MOODLE_DB_USER" "$MOODLE_DB_NAME" -e "$sql"
}

# Fix restrictedusers setting for our custom service
echo "🔓 Setting restrictedusers = 0 for MoodleClaude API..."
mysql_exec "UPDATE mdl_external_services SET restrictedusers = 0 WHERE shortname = 'moodleclaude_api';"

# Add all required capabilities to Manager role
echo "👑 Adding web service capabilities to Manager role..."

# Get the Manager role ID
MANAGER_ROLE_ID=$(mysql_exec "SELECT id FROM mdl_role WHERE shortname = 'manager';" | tail -n 1)

if [ -n "$MANAGER_ROLE_ID" ]; then
    echo "   Manager role ID: $MANAGER_ROLE_ID"
    
    # Add web service capabilities
    CAPABILITIES=(
        "webservice/rest:use"
        "moodle/webservice:createtoken"
        "moodle/site:config"
        "moodle/course:create"
        "moodle/course:manageactivities"
        "moodle/course:activityvisibility"
        "moodle/course:sectionvisibility"
        "mod/page:addinstance"
        "mod/label:addinstance"
    )
    
    for capability in "${CAPABILITIES[@]}"; do
        echo "   Adding capability: $capability"
        mysql_exec "INSERT IGNORE INTO mdl_role_capabilities (roleid, capability, permission, contextid, component, timecreated, timemodified) VALUES ($MANAGER_ROLE_ID, '$capability', 1, 1, '', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());"
    done
else
    echo "❌ Manager role not found"
fi

# Ensure user has manager role in system context
echo "👤 Ensuring user has manager role..."
USER_ID=$(mysql_exec "SELECT id FROM mdl_user WHERE username = 'simon';" | tail -n 1)

if [ -n "$USER_ID" ] && [ -n "$MANAGER_ROLE_ID" ]; then
    mysql_exec "INSERT IGNORE INTO mdl_role_assignments (roleid, contextid, userid, component, itemid, timecreated, timemodified) VALUES ($MANAGER_ROLE_ID, 1, $USER_ID, '', 0, UNIX_TIMESTAMP(), UNIX_TIMESTAMP());"
    echo "✅ User assigned manager role"
fi

# Create a working token for the custom service
echo "🔑 Creating functional token..."
TOKEN=$(openssl rand -hex 16)

mysql_exec "DELETE FROM mdl_external_tokens WHERE userid = $USER_ID AND externalserviceid = 2;"
mysql_exec "INSERT INTO mdl_external_tokens (token, tokentype, externalserviceid, userid, contextid, creatorid, timecreated, validuntil) VALUES ('$TOKEN', 0, 2, $USER_ID, 1, $USER_ID, UNIX_TIMESTAMP(), 0);"

echo "✅ New token created: $TOKEN"

# Update .env file
if [ -f ".env" ]; then
    sed -i.bak "s/MOODLE_TOKEN=.*/MOODLE_TOKEN=$TOKEN/" .env
    echo "✅ .env file updated"
fi

echo ""
echo "🧪 Testing token..."
RESPONSE=$(curl -s -w "%{http_code}" "http://localhost:8080/webservice/rest/server.php" -d "wstoken=$TOKEN&wsfunction=core_webservice_get_site_info&moodlewsrestformat=json")

if [[ "$RESPONSE" == *"200" ]]; then
    echo "✅ Token is working!"
else
    echo "❌ Token test failed (HTTP: ${RESPONSE: -3})"
fi

echo ""
echo "📊 Final verification..."
mysql_exec "SELECT 'Services:' as info, COUNT(*) as count FROM mdl_external_services WHERE enabled = 1 UNION ALL SELECT 'Functions:', COUNT(*) FROM mdl_external_services_functions esf JOIN mdl_external_services es ON esf.externalserviceid = es.id WHERE es.shortname = 'moodleclaude_api' UNION ALL SELECT 'Tokens:', COUNT(*) FROM mdl_external_tokens et JOIN mdl_external_services es ON et.externalserviceid = es.id WHERE es.shortname = 'moodleclaude_api';"

echo ""
echo "🎉 Web service permissions fixed!"
echo "📋 Now you can create tokens via:"
echo "   Site Administration → Server → Web services → Manage tokens"
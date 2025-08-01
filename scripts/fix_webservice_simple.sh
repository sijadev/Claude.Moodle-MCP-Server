#!/bin/bash
#
# Simple fix for web service permissions
#

set -e

MOODLE_NETWORK="moodleclaude_moodle_network"

echo "🔧 Simple Web Service Fix"
echo "========================"

# Execute MySQL command via Docker
mysql_exec() {
    local sql="$1"
    docker run --rm --network "$MOODLE_NETWORK" mysql:8.0 mysql -h mariadb -u bn_moodle bitnami_moodle -e "$sql"
}

# Fix the main issue: restrictedusers
echo "🔓 Making MoodleClaude API unrestricted..."
mysql_exec "UPDATE mdl_external_services SET restrictedusers = 0 WHERE shortname = 'moodleclaude_api';"

# Get IDs
MANAGER_ROLE_ID=$(mysql_exec "SELECT id FROM mdl_role WHERE shortname = 'manager';" | tail -n 1)
USER_ID=$(mysql_exec "SELECT id FROM mdl_user WHERE username = 'simon';" | tail -n 1)

echo "Manager Role ID: $MANAGER_ROLE_ID"
echo "User ID: $USER_ID"

# Add essential capabilities (simplified)
echo "👑 Adding essential capabilities..."
mysql_exec "INSERT IGNORE INTO mdl_role_capabilities (contextid, roleid, capability, permission, timemodified, modifierid) VALUES (1, $MANAGER_ROLE_ID, 'webservice/rest:use', 1, UNIX_TIMESTAMP(), $USER_ID);"
mysql_exec "INSERT IGNORE INTO mdl_role_capabilities (contextid, roleid, capability, permission, timemodified, modifierid) VALUES (1, $MANAGER_ROLE_ID, 'moodle/webservice:createtoken', 1, UNIX_TIMESTAMP(), $USER_ID);"

# Ensure user has manager role in system context
echo "👤 Ensuring proper role assignment..."
mysql_exec "INSERT IGNORE INTO mdl_role_assignments (roleid, contextid, userid, timecreated, timemodified) VALUES ($MANAGER_ROLE_ID, 1, $USER_ID, UNIX_TIMESTAMP(), UNIX_TIMESTAMP());"

# Create working token
echo "🔑 Creating new token..."
TOKEN=$(openssl rand -hex 16)
mysql_exec "DELETE FROM mdl_external_tokens WHERE userid = $USER_ID;"
mysql_exec "INSERT INTO mdl_external_tokens (token, tokentype, externalserviceid, userid, contextid, creatorid, timecreated, validuntil) VALUES ('$TOKEN', 0, 2, $USER_ID, 1, $USER_ID, UNIX_TIMESTAMP(), 0);"

echo "✅ Token: $TOKEN"

# Update .env
if [ -f ".env" ]; then
    sed -i.bak "s/MOODLE_TOKEN=.*/MOODLE_TOKEN=$TOKEN/" .env
    echo "✅ .env updated"
fi

# Test token
echo "🧪 Testing..."
HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null "http://localhost:8080/webservice/rest/server.php" -d "wstoken=$TOKEN&wsfunction=core_webservice_get_site_info&moodlewsrestformat=json")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ SUCCESS! Token is working"
    echo ""
    echo "🎉 You can now:"
    echo "   1. Restart MCP server: kill \$(pgrep -f 'python.*mcp_server'); uv run python mcp_server.py &"
    echo "   2. Test: uv run python test_direct_moodle.py"
    echo "   3. Use MCP tools in Claude Desktop!"
else
    echo "❌ Token test failed (HTTP: $HTTP_CODE)"
    echo "🔧 Try creating token manually via web interface:"
    echo "   http://localhost:8080/admin → Web services → Manage tokens"
fi

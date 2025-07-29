#!/bin/bash
#
# Script to enable Moodle web service functions and configure enrollment using MySQL Docker container
# This version uses the MySQL Docker image to connect to the MariaDB container
#
# Features:
# - Enables Moodle web services and REST protocol
# - Creates external web service (not mobile) with WSManageSections functions
# - Configures course enrollment for better visibility
# - Enrolls admin user in all courses so they appear in "My Courses"
#

set -e

MOODLE_DB_HOST="mariadb"
MOODLE_DB_NAME="bitnami_moodle"
MOODLE_DB_USER="bn_moodle"
MOODLE_NETWORK="moodleclaude_moodle_network"

echo "🚀 Moodle Web Service Function Enabler (Docker Version)"
echo "======================================================"
echo "🐳 Using MySQL Docker container to connect to MariaDB"
echo ""

# Functions that need to be enabled
FUNCTIONS=(
    # Core course functions
    "core_course_create_courses"
    "core_course_get_courses"
    "core_course_get_categories"
    "core_course_get_contents"
    "core_course_edit_section"
    "core_files_upload"
    "core_webservice_get_site_info"
    # Page and label modules
    "mod_page_get_pages_by_courses"
    "mod_page_view_page"
    "mod_label_get_labels_by_courses"
    # WSManageSections plugin functions (ESSENTIAL!)
    "local_wsmanagesections_create_sections"
    "local_wsmanagesections_get_sections"
    "local_wsmanagesections_update_sections"
    # Enrollment functions (for course visibility)
    "core_enrol_get_course_enrolment_methods"
    "enrol_self_enrol_user"
    "core_enrol_get_users_courses"
)

# Test MySQL connection via Docker
test_mysql_connection() {
    echo "🔍 Testing MySQL connection via Docker..."
    if docker run --rm --network "$MOODLE_NETWORK" mysql:8.0 mysql -h"$MOODLE_DB_HOST" -u"$MOODLE_DB_USER" -e "USE $MOODLE_DB_NAME; SELECT 1;" >/dev/null 2>&1; then
        echo "✅ Database connection successful"
        return 0
    else
        echo "❌ Cannot connect to database"
        return 1
    fi
}

# Execute MySQL command via Docker
mysql_exec() {
    local sql="$1"
    docker run --rm --network "$MOODLE_NETWORK" mysql:8.0 mysql -h"$MOODLE_DB_HOST" -u"$MOODLE_DB_USER" "$MOODLE_DB_NAME" -e "$sql"
}

# Enable web services globally
enable_web_services() {
    echo "🌐 Enabling web services globally..."
    mysql_exec "UPDATE mdl_config SET value = '1' WHERE name = 'enablewebservices';"
    echo "✅ Web services enabled"
}

# Enable REST protocol
enable_rest_protocol() {
    echo "🔗 Enabling REST protocol..."
    mysql_exec "UPDATE mdl_config_plugins SET value = '1' WHERE plugin = 'webservice_rest' AND name = 'enabled';"
    echo "✅ REST protocol enabled"
}

# Create custom external service (not mobile service)
create_custom_service() {
    echo "🔧 Creating custom MoodleClaude external service..."
    
    # First, remove any existing service to start fresh
    mysql_exec "DELETE FROM mdl_external_services_functions WHERE externalserviceid IN (SELECT id FROM mdl_external_services WHERE shortname = 'moodleclaude_api');"
    mysql_exec "DELETE FROM mdl_external_services_users WHERE externalserviceid IN (SELECT id FROM mdl_external_services WHERE shortname = 'moodleclaude_api');"
    mysql_exec "DELETE FROM mdl_external_tokens WHERE externalserviceid IN (SELECT id FROM mdl_external_services WHERE shortname = 'moodleclaude_api');"
    mysql_exec "DELETE FROM mdl_external_services WHERE shortname = 'moodleclaude_api';"
    
    # Create new external service (restrictedusers=0 for external, not mobile)
    mysql_exec "INSERT INTO mdl_external_services (name, shortname, enabled, requiredcapability, restrictedusers, downloadfiles, uploadfiles, timecreated, timemodified) VALUES ('MoodleClaude API', 'moodleclaude_api', 1, '', 0, 1, 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP());"
    
    echo "✅ External service created (not mobile service)"
}

# Add functions to the custom service
add_functions_to_service() {
    echo "⚙️ Adding functions to MoodleClaude service..."
    
    for func in "${FUNCTIONS[@]}"; do
        echo "   Adding: $func"
        mysql_exec "INSERT IGNORE INTO mdl_external_services_functions (externalserviceid, functionname) SELECT id, '$func' FROM mdl_external_services WHERE shortname = 'moodleclaude_api' AND NOT EXISTS (SELECT 1 FROM mdl_external_services_functions esf2 WHERE esf2.externalserviceid = mdl_external_services.id AND esf2.functionname = '$func');"
    done
    
    echo "✅ Functions added to service"
}

# Create token for admin user
create_token() {
    echo "🔑 Creating web service token..."
    
    # Get user ID for admin (simon)
    USER_ID=$(mysql_exec "SELECT id FROM mdl_user WHERE username = 'simon';" | tail -n 1)
    SERVICE_ID=$(mysql_exec "SELECT id FROM mdl_external_services WHERE shortname = 'moodleclaude_api';" | tail -n 1)
    
    if [ -n "$USER_ID" ] && [ -n "$SERVICE_ID" ]; then
        # Generate a random token
        TOKEN=$(openssl rand -hex 16)
        
        # Insert token
        mysql_exec "INSERT IGNORE INTO mdl_external_tokens (token, externalserviceid, userid, contextid, creatorid, timecreated, validuntil) VALUES ('$TOKEN', $SERVICE_ID, $USER_ID, 1, $USER_ID, UNIX_TIMESTAMP(), 0);"
        
        echo "✅ Token created: $TOKEN"
        echo ""
        echo "📋 Update your .env file:"
        echo "MOODLE_TOKEN=$TOKEN"
        echo ""
        
        # Update .env file automatically
        if [ -f ".env" ]; then
            sed -i.bak "s/MOODLE_TOKEN=.*/MOODLE_TOKEN=$TOKEN/" .env
            echo "✅ .env file updated automatically"
        fi
    else
        echo "❌ Could not find user or service ID"
    fi
}

# Add user to authorized users
authorize_user() {
    echo "👤 Authorizing user for service..."
    
    USER_ID=$(mysql_exec "SELECT id FROM mdl_user WHERE username = 'simon';" | tail -n 1)
    SERVICE_ID=$(mysql_exec "SELECT id FROM mdl_external_services WHERE shortname = 'moodleclaude_api';" | tail -n 1)
    
    if [ -n "$USER_ID" ] && [ -n "$SERVICE_ID" ]; then
        mysql_exec "INSERT IGNORE INTO mdl_external_services_users (externalserviceid, userid) VALUES ($SERVICE_ID, $USER_ID);"
        echo "✅ User authorized for service"
    fi
}

# Configure course enrollment for visibility
configure_enrollment() {
    echo "📚 Configuring course enrollment for better visibility..."
    
    # Enable self-enrollment for all existing courses (except site course)
    echo "   Enabling self-enrollment for all courses..."
    mysql_exec "
        INSERT IGNORE INTO mdl_enrol (enrol, status, courseid, sortorder, name, enrolperiod, enrolstartdate, enrolenddate, expirynotify, expirythreshold, notifyall, password, cost, currency, roleid, customint1, customint2, customint3, customint4, customint5, customint6, customdec1, customdec2, customchar1, customchar2, customchar3, customtext1, customtext2, customtext3, customtext4, timecreated, timemodified)
        SELECT 'self', 0, c.id, 0, NULL, 0, 0, 0, 0, 86400, 0, NULL, NULL, NULL, 5, NULL, NULL, NULL, NULL, NULL, NULL, 0.000000, 0.000000, NULL, NULL, NULL, NULL, NULL, NULL, NULL, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()
        FROM mdl_course c 
        WHERE c.id > 1 
        AND NOT EXISTS (SELECT 1 FROM mdl_enrol e WHERE e.courseid = c.id AND e.enrol = 'self');
    "
    
    # Enable any existing disabled self-enrollment methods
    echo "   Enabling disabled self-enrollment methods..."
    mysql_exec "UPDATE mdl_enrol SET status = 0 WHERE enrol = 'self' AND status = 1;"
    
    # Enroll the admin user in all courses for immediate visibility
    echo "   Enrolling admin user in all courses..."
    USER_ID=$(mysql_exec "SELECT id FROM mdl_user WHERE username = 'simon';" | tail -n 1)
    if [ -n "$USER_ID" ]; then
        mysql_exec "
            INSERT IGNORE INTO mdl_user_enrolments (status, enrolid, userid, timestart, timeend, modifierid, timecreated, timemodified)
            SELECT 0, e.id, $USER_ID, 0, 0, $USER_ID, UNIX_TIMESTAMP(), UNIX_TIMESTAMP()
            FROM mdl_enrol e
            JOIN mdl_course c ON e.courseid = c.id
            WHERE c.id > 1 
            AND e.enrol = 'self'
            AND e.status = 0
            AND NOT EXISTS (SELECT 1 FROM mdl_user_enrolments ue WHERE ue.enrolid = e.id AND ue.userid = $USER_ID);
        "
    fi
    
    # Show enrollment statistics
    TOTAL_COURSES=$(mysql_exec "SELECT COUNT(*) FROM mdl_course WHERE id > 1;" | tail -n 1)
    SELF_ENROL_ENABLED=$(mysql_exec "SELECT COUNT(*) FROM mdl_enrol WHERE enrol = 'self' AND status = 0;" | tail -n 1)
    USER_ENROLLED=$(mysql_exec "SELECT COUNT(DISTINCT e.courseid) FROM mdl_user_enrolments ue JOIN mdl_enrol e ON ue.enrolid = e.id WHERE ue.userid = $USER_ID AND e.courseid > 1;" | tail -n 1)
    
    echo "📊 Enrollment Configuration Results:"
    echo "   Total courses: $TOTAL_COURSES"
    echo "   Self-enrollment enabled: $SELF_ENROL_ENABLED"
    echo "   User enrolled in: $USER_ENROLLED courses"
    echo "✅ Enrollment configuration completed"
}

# Verify setup
verify_setup() {
    echo "🧪 Verifying setup..."
    
    SERVICE_COUNT=$(mysql_exec "SELECT COUNT(*) FROM mdl_external_services WHERE shortname = 'moodleclaude_api';" | tail -n 1)
    FUNCTION_COUNT=$(mysql_exec "SELECT COUNT(*) FROM mdl_external_services_functions esf JOIN mdl_external_services es ON esf.externalserviceid = es.id WHERE es.shortname = 'moodleclaude_api';" | tail -n 1)
    TOKEN_COUNT=$(mysql_exec "SELECT COUNT(*) FROM mdl_external_tokens et JOIN mdl_external_services es ON et.externalserviceid = es.id WHERE es.shortname = 'moodleclaude_api';" | tail -n 1)
    
    echo "📊 Setup Results:"
    echo "   Services: $SERVICE_COUNT"
    echo "   Functions: $FUNCTION_COUNT"
    echo "   Tokens: $TOKEN_COUNT"
    
    if [ "$SERVICE_COUNT" -eq 1 ] && [ "$FUNCTION_COUNT" -gt 0 ] && [ "$TOKEN_COUNT" -gt 0 ]; then
        echo "✅ Setup completed successfully!"
        return 0
    else
        echo "❌ Setup incomplete"
        return 1
    fi
}

# Main execution
main() {
    if ! test_mysql_connection; then
        echo "❌ Cannot connect to Moodle database"
        echo "🔧 Make sure the Moodle containers are running:"
        echo "   docker-compose up -d"
        exit 1
    fi
    
    echo ""
    echo "🤔 This will configure Moodle web services automatically."
    read -p "Continue? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        enable_web_services
        enable_rest_protocol
        create_custom_service
        add_functions_to_service
        create_token
        authorize_user
        configure_enrollment
        
        echo ""
        if verify_setup; then
            echo ""
            echo "🎉 Moodle Web Services are now configured!"
            echo "✅ Enrollment is configured - courses will appear in 'My Courses'"
            echo "🔄 You may want to restart the MCP server:"
            echo "   kill \$(pgrep -f 'python.*mcp_server')"
            echo "   uv run python mcp_server.py &"
            echo ""
            echo "🧪 Test with:"
            echo "   uv run python test_mcp_connection.py"
        fi
    else
        echo "❌ Setup cancelled"
    fi
}

main "$@"
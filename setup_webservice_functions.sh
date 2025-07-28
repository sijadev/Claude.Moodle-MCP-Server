#!/bin/bash
#
# Script to enable Moodle web service functions via direct database access or CLI
# WARNING: This modifies the Moodle database directly - use with caution!
#

set -e

MOODLE_URL="${MOODLE_URL:-http://localhost:8080}"
MOODLE_DB_HOST="${MOODLE_DB_HOST:-localhost}"
MOODLE_DB_NAME="${MOODLE_DB_NAME:-moodle}"
MOODLE_DB_USER="${MOODLE_DB_USER:-moodle}"
MOODLE_DB_PASS="${MOODLE_DB_PASS:-moodle}"

echo "🚀 Moodle Web Service Function Enabler"
echo "======================================"
echo "⚠️  WARNING: This script modifies the Moodle database directly!"
echo "📋 Make sure you have a backup before proceeding."
echo ""

# Functions that need to be enabled
FUNCTIONS=(
    "core_course_create_sections"
    "core_course_edit_section"
    "core_course_update_sections"
    "core_course_create_activities"
    "core_course_create_modules"
    "mod_page_create_page"
    "mod_label_add_label"
    "core_files_upload"
    "core_webservice_get_site_info"
)

# Check if we can connect to the database
check_db_connection() {
    echo "🔍 Checking database connection..."
    if command -v mysql >/dev/null 2>&1; then
        if mysql -h"$MOODLE_DB_HOST" -u"$MOODLE_DB_USER" -p"$MOODLE_DB_PASS" -e "USE $MOODLE_DB_NAME; SELECT 1;" >/dev/null 2>&1; then
            echo "✅ Database connection successful"
            return 0
        else
            echo "❌ Cannot connect to database"
            return 1
        fi
    else
        echo "❌ MySQL client not found"
        return 1
    fi
}

# Enable functions in default mobile service
enable_functions_mobile_service() {
    echo "📱 Adding functions to Moodle Mobile service..."
    
    for func in "${FUNCTIONS[@]}"; do
        echo "   Adding: $func"
        mysql -h"$MOODLE_DB_HOST" -u"$MOODLE_DB_USER" -p"$MOODLE_DB_PASS" "$MOODLE_DB_NAME" << EOF
INSERT IGNORE INTO mdl_external_services_functions (externalserviceid, functionname)
SELECT id, '$func' FROM mdl_external_services WHERE shortname = 'moodle_mobile_app'
AND NOT EXISTS (
    SELECT 1 FROM mdl_external_services_functions esf2 
    WHERE esf2.externalserviceid = mdl_external_services.id 
    AND esf2.functionname = '$func'
);
EOF
    done
}

# Create custom service if needed
create_custom_service() {
    echo "🔧 Creating custom MoodleClaude service..."
    
    mysql -h"$MOODLE_DB_HOST" -u"$MOODLE_DB_USER" -p"$MOODLE_DB_PASS" "$MOODLE_DB_NAME" << EOF
INSERT IGNORE INTO mdl_external_services (name, shortname, enabled, requiredcapability, restrictedusers, downloadfiles, uploadfiles, timecreated, timemodified)
VALUES ('MoodleClaude API', 'moodleclaude_api', 1, '', 0, 1, 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP());
EOF

    # Add functions to the custom service
    for func in "${FUNCTIONS[@]}"; do
        echo "   Adding $func to custom service..."
        mysql -h"$MOODLE_DB_HOST" -u"$MOODLE_DB_USER" -p"$MOODLE_DB_PASS" "$MOODLE_DB_NAME" << EOF
INSERT IGNORE INTO mdl_external_services_functions (externalserviceid, functionname)
SELECT id, '$func' FROM mdl_external_services WHERE shortname = 'moodleclaude_api'
AND NOT EXISTS (
    SELECT 1 FROM mdl_external_services_functions esf2 
    WHERE esf2.externalserviceid = mdl_external_services.id 
    AND esf2.functionname = '$func'
);
EOF
    done
}

# Main execution
main() {
    if ! check_db_connection; then
        echo ""
        echo "❌ Cannot connect to database directly"
        echo "📖 Please use the manual method:"
        echo "   1. Access $MOODLE_URL/admin"
        echo "   2. Go to Site Administration → Server → Web services"
        echo "   3. Follow the instructions from enable_webservices.py"
        exit 1
    fi
    
    echo ""
    read -p "🤔 Do you want to proceed with database modifications? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        enable_functions_mobile_service
        create_custom_service
        
        echo ""
        echo "✅ Web service functions have been enabled!"
        echo "🔄 You may need to purge Moodle caches:"
        echo "   • Admin → Development → Purge all caches"
        echo ""
        echo "🧪 Test with: python demos/check_webservices.py"
    else
        echo "❌ Operation cancelled"
        echo "📖 Use manual method with enable_webservices.py"
    fi
}

main "$@"
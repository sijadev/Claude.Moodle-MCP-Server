#!/bin/bash
#
# Clean up web service functions - remove non-existent ones and add real ones
#

set -e

MOODLE_NETWORK="moodleclaude_moodle_network"

echo "🧹 Cleaning Up Web Service Functions"
echo "===================================="

# Execute MySQL command via Docker
mysql_exec() {
    local sql="$1"
    docker run --rm --network "$MOODLE_NETWORK" mysql:8.0 mysql -h mariadb -u bn_moodle bitnami_moodle -e "$sql"
}

# Remove non-existent functions from our service
echo "🗑️ Removing non-existent functions..."
NON_EXISTENT_FUNCTIONS=(
    "core_course_create_sections"
    "core_course_update_sections"
    "mod_page_add_page"
    "mod_label_add_label"
    "local_wsmanagesections_create_sections"
    "local_wsmanagesections_delete_sections"
    "local_wsmanagesections_get_sections"
    "local_wsmanagesections_move_section"
    "local_wsmanagesections_update_sections"
    "mod_label_get_labels_by_courses"
    "mod_page_get_pages_by_courses"
    "mod_page_view_page"
    "core_files_get_files"
)

for func in "${NON_EXISTENT_FUNCTIONS[@]}"; do
    echo "   Removing: $func"
    mysql_exec "DELETE FROM mdl_external_services_functions WHERE functionname = '$func' AND externalserviceid = (SELECT id FROM mdl_external_services WHERE shortname = 'moodleclaude_api');"
done

# Add actually available functions
echo "✅ Adding available functions..."
AVAILABLE_FUNCTIONS=(
    "core_course_create_courses"
    "core_course_get_courses"
    "core_course_get_categories"
    "core_course_get_contents"
    "core_course_edit_section"
    "core_files_upload"
    "core_webservice_get_site_info"
    "mod_page_get_pages_by_courses"
    "mod_page_view_page"
    "mod_label_get_labels_by_courses"
)

for func in "${AVAILABLE_FUNCTIONS[@]}"; do
    echo "   Adding: $func"
    mysql_exec "INSERT IGNORE INTO mdl_external_services_functions (externalserviceid, functionname) SELECT id, '$func' FROM mdl_external_services WHERE shortname = 'moodleclaude_api' AND NOT EXISTS (SELECT 1 FROM mdl_external_services_functions esf2 WHERE esf2.externalserviceid = mdl_external_services.id AND esf2.functionname = '$func');"
done

echo ""
echo "📊 Current functions in MoodleClaude API service:"
mysql_exec "SELECT functionname FROM mdl_external_services_functions esf JOIN mdl_external_services es ON esf.externalserviceid = es.id WHERE es.shortname = 'moodleclaude_api' ORDER BY functionname;"

echo ""
echo "✅ Web service functions cleaned up!"
echo "🔄 You may want to restart the MCP server to apply changes."
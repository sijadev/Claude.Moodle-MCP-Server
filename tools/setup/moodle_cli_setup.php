#!/usr/bin/env php
<?php
/**
 * MoodleClaude Enhanced Web Service CLI Setup
 * ===========================================
 * 
 * CLI-compatible script for setting up MoodleClaude web services
 * Designed to run inside Moodle containers with proper CLI context
 */

// Ensure we're in CLI mode
define('CLI_SCRIPT', true);

// Set up Moodle environment
require_once('/bitnami/moodle/config.php');
require_once($CFG->libdir.'/clilib.php');
require_once($CFG->libdir.'/adminlib.php');

// CLI options
list($options, $unrecognized) = cli_get_params(
    array(
        'help' => false,
        'verbose' => false
    ),
    array(
        'h' => 'help',
        'v' => 'verbose'
    )
);

if ($options['help']) {
    echo "MoodleClaude Enhanced Web Service Setup

Usage: php moodle_cli_setup.php [options]

Options:
-h, --help      Print out this help
-v, --verbose   Verbose output

Example:
\$ php moodle_cli_setup.php --verbose
";
    exit(0);
}

echo "🚀 MoodleClaude Enhanced Web Service CLI Setup\n";
echo "===============================================\n\n";

try {
    // Get admin user for proper context
    $admin = get_admin();
    if (!$admin) {
        throw new Exception("No admin user found");
    }
    
    // Set up admin session for CLI
    \core\session\manager::set_user($admin);
    echo "✅ Admin context established (User: {$admin->username})\n";

    // Step 1: Enable web services
    echo "\n🌐 Step 1: Enabling web services...\n";
    set_config('enablewebservices', 1);
    echo "✅ Web services enabled\n";

    // Step 2: Enable REST protocol
    echo "\n🔌 Step 2: Enabling REST protocol...\n";
    $protocols = get_config('core', 'webserviceprotocols');
    if (empty($protocols)) {
        $protocols = 'rest';
    } else {
        $protocols_array = explode(',', $protocols);
        if (!in_array('rest', $protocols_array)) {
            $protocols_array[] = 'rest';
            $protocols = implode(',', $protocols_array);
        }
    }
    set_config('webserviceprotocols', $protocols);
    echo "✅ REST protocol enabled\n";

    // Step 3: Create or update MoodleClaude enhanced web service
    echo "\n⚙️  Step 3: Creating MoodleClaude enhanced web service...\n";
    
    $service_shortname = 'moodleclaude_service';
    $existing_service = $DB->get_record('external_services', array('shortname' => $service_shortname));
    
    if ($existing_service) {
        echo "📝 Updating existing MoodleClaude service (ID: {$existing_service->id})\n";
        $service = $existing_service;
        $service->name = 'MoodleClaude AI Enhanced Web Service';
        $service->enabled = 1;
        $service->restrictedusers = 0;
        $service->downloadfiles = 1;
        $service->uploadfiles = 1;
        $service->timemodified = time();
        $DB->update_record('external_services', $service);
    } else {
        echo "🆕 Creating new MoodleClaude enhanced service\n";
        $service = new stdClass();
        $service->name = 'MoodleClaude AI Enhanced Web Service';
        $service->shortname = $service_shortname;
        $service->component = 'core';
        $service->timecreated = time();
        $service->timemodified = time();
        $service->enabled = 1;
        $service->restrictedusers = 0;
        $service->downloadfiles = 1;
        $service->uploadfiles = 1;
        $service->id = $DB->insert_record('external_services', $service);
    }
    
    echo "✅ MoodleClaude enhanced service ready (ID: {$service->id})\n";

    // Step 4: Enhanced function set
    echo "\n🔧 Step 4: Adding enhanced function set...\n";
    
    $required_functions = [
        // Core essential functions (7)
        'core_webservice_get_site_info',
        'core_course_get_courses',
        'core_course_create_courses',
        'core_course_delete_courses', 
        'core_course_get_contents',
        'core_course_get_categories',
        'core_course_update_courses',
        
        // Content management (6) - Updated with available functions
        'core_course_delete_modules',
        'core_course_get_course_module',
        'core_course_get_course_module_by_instance',
        'core_course_get_module',
        'core_course_edit_module',
        'core_course_edit_section',
        
        // User management (4)
        'core_user_get_users',
        'core_user_create_users',
        'core_enrol_get_enrolled_users',
        'core_enrol_get_users_courses',
        
        // File management (2)
        'core_files_upload',
        'core_files_get_files',
        
        // Assessment tools (6) - Enhanced with available assign functions
        'mod_assign_get_assignments',
        'mod_assign_get_submissions',
        'mod_assign_save_submission',
        'mod_assign_get_grades',
        'mod_assign_save_grade',
        'mod_assign_view_assign',
        
        // Communication (2)
        'mod_forum_get_forums_by_courses',
        'mod_forum_get_forum_discussions',
        
        // Role management (2)
        'core_role_assign_roles',
        'core_role_unassign_roles',
        
        // Completion tracking (1)
        'core_completion_get_course_completion_status',
    ];

    $added_count = 0;
    $skipped_count = 0;
    $missing_count = 0;

    foreach ($required_functions as $function_name) {
        // Check if function exists in Moodle
        $function_exists = $DB->get_record('external_functions', array('name' => $function_name));
        
        if (!$function_exists) {
            if ($options['verbose']) {
                echo "⚠️  Function not available: {$function_name}\n";
            }
            $missing_count++;
            continue;
        }
        
        // Check if already added to service
        $service_function_exists = $DB->get_record('external_services_functions', [
            'externalserviceid' => $service->id,
            'functionname' => $function_name
        ]);
        
        if ($service_function_exists) {
            $skipped_count++;
            continue;
        }
        
        // Add function to service
        $service_function = new stdClass();
        $service_function->externalserviceid = $service->id;
        $service_function->functionname = $function_name;
        $DB->insert_record('external_services_functions', $service_function);
        
        if ($options['verbose']) {
            echo "✅ Added: {$function_name}\n";
        }
        $added_count++;
    }

    echo "\n📊 Enhanced Function Summary:\n";
    echo "   • Added: {$added_count}\n";
    echo "   • Skipped (already exists): {$skipped_count}\n";  
    echo "   • Missing/Unavailable: {$missing_count}\n";
    
    // Calculate coverage
    $total_functions = count($required_functions);
    $available_functions = $added_count + $skipped_count;
    $coverage = round(($available_functions / $total_functions) * 100, 1);
    echo "   • Coverage: {$coverage}%\n";

    // Step 5: Create/Update enhanced service user and token
    echo "\n👤 Step 5: Setting up enhanced service user and token...\n";
    
    // Check for existing MoodleClaude service user
    $service_user = $DB->get_record('user', array('username' => 'moodleclaude_enhanced'));
    
    if (!$service_user) {
        echo "🆕 Creating MoodleClaude enhanced service user\n";
        $service_user = new stdClass();
        $service_user->username = 'moodleclaude_enhanced';
        $service_user->password = hash_internal_user_password('MoodleClaude_Enhanced_' . time() . '_Service!');
        $service_user->firstname = 'MoodleClaude';
        $service_user->lastname = 'Enhanced Service Account';
        $service_user->email = 'moodleclaude-enhanced@' . parse_url($CFG->wwwroot, PHP_URL_HOST);
        $service_user->confirmed = 1;
        $service_user->mnethostid = $CFG->mnet_localhost_id;
        $service_user->timecreated = time();
        $service_user->timemodified = time();
        $service_user->id = $DB->insert_record('user', $service_user);
    } else {
        echo "📝 Using existing MoodleClaude enhanced service user (ID: {$service_user->id})\n";
    }

    // Assign Manager role to service user at system level
    $context_system = context_system::instance();
    $manager_role = $DB->get_record('role', array('shortname' => 'manager'));
    
    if ($manager_role) {
        $existing_assignment = $DB->get_record('role_assignments', [
            'roleid' => $manager_role->id,
            'userid' => $service_user->id,
            'contextid' => $context_system->id
        ]);
        
        if (!$existing_assignment) {
            $role_assignment = new stdClass();
            $role_assignment->roleid = $manager_role->id;
            $role_assignment->contextid = $context_system->id;
            $role_assignment->userid = $service_user->id;
            $role_assignment->timemodified = time();
            $role_assignment->modifierid = $admin->id;
            $role_assignment->component = '';
            $role_assignment->itemid = 0;
            $role_assignment->sortorder = 0;
            $DB->insert_record('role_assignments', $role_assignment);
            echo "✅ Assigned Manager role to enhanced service user\n";
        } else {
            echo "✅ Enhanced service user already has Manager role\n";
        }
    }

    // Create or update token
    $existing_token = $DB->get_record('external_tokens', [
        'userid' => $service_user->id,
        'externalserviceid' => $service->id
    ]);
    
    if ($existing_token) {
        echo "🔑 Using existing enhanced token: " . substr($existing_token->token, 0, 8) . "...\n";
        $token = $existing_token->token;
    } else {
        echo "🆕 Creating new enhanced token\n";
        
        // Generate token manually since external_generate_token might not be available
        $token = md5(uniqid(rand(), true));
        
        $tokenrecord = new stdClass();
        $tokenrecord->token = $token;
        $tokenrecord->userid = $service_user->id;
        $tokenrecord->tokentype = EXTERNAL_TOKEN_PERMANENT;
        $tokenrecord->contextid = $context_system->id;
        $tokenrecord->creatorid = $admin->id;
        $tokenrecord->externalserviceid = $service->id;
        $tokenrecord->timecreated = time();
        $tokenrecord->validuntil = null;
        $tokenrecord->iprestriction = null;
        $tokenrecord->privatetoken = null;
        
        $DB->insert_record('external_tokens', $tokenrecord);
        echo "🔑 New enhanced token created: " . substr($token, 0, 8) . "...\n";
    }

    // Step 6: Enhanced capabilities
    echo "\n🔐 Step 6: Setting up enhanced capabilities...\n";
    
    $required_capabilities = [
        'webservice/rest:use',
        'moodle/course:create',
        'moodle/course:update', 
        'moodle/course:delete',
        'moodle/course:view',
        'moodle/course:managefiles',
        'moodle/course:manageactivities',
        'moodle/course:activityvisibility',
        'moodle/course:sectionvisibility',
        'moodle/site:config',
        'moodle/user:create',
        'moodle/user:viewdetails',
        'moodle/role:assign',
        'moodle/course:viewhiddensections',
    ];

    $caps_added = 0;
    foreach ($required_capabilities as $capability) {
        $role_capability = $DB->get_record('role_capabilities', [
            'roleid' => $manager_role->id,
            'capability' => $capability,
            'contextid' => $context_system->id
        ]);
        
        if (!$role_capability) {
            $role_capability = new stdClass();
            $role_capability->contextid = $context_system->id;
            $role_capability->roleid = $manager_role->id;
            $role_capability->capability = $capability;
            $role_capability->permission = 1;
            $role_capability->timemodified = time();
            $role_capability->modifierid = $admin->id;
            $DB->insert_record('role_capabilities', $role_capability);
            $caps_added++;
            if ($options['verbose']) {
                echo "✅ Added capability: {$capability}\n";
            }
        }
    }
    
    if ($caps_added > 0) {
        echo "✅ Added {$caps_added} enhanced capabilities\n";
    } else {
        echo "✅ All enhanced capabilities already present\n";
    }

    // Final enhanced summary
    echo "\n🎉 SUCCESS! MoodleClaude Enhanced Web Service Created!\n";
    echo "====================================================\n\n";
    
    echo "📊 Enhanced Configuration Dashboard:\n";
    echo "   • Service Name: {$service->name}\n";
    echo "   • Service ID: {$service->id}\n";
    echo "   • Functions Added: {$added_count}\n";
    echo "   • Function Coverage: {$coverage}%\n";
    echo "   • Service User: {$service_user->username}\n";
    echo "   • Enhanced Token: " . substr($token, 0, 12) . "...\n";
    echo "   • Capabilities: " . count($required_capabilities) . " enhanced\n\n";
    
    echo "🔧 Enhanced Environment Variables:\n";
    echo "   export MOODLE_TOKEN_ENHANCED=\"{$token}\"\n";
    echo "   export MOODLE_WS_USER=\"{$service_user->username}\"\n";
    echo "   export MOODLE_SERVICE_ID=\"{$service->id}\"\n\n";
    
    echo "🌐 Enhanced Web Service URL:\n";
    echo "   {$CFG->wwwroot}/webservice/rest/server.php\n\n";
    
    echo "✨ Enhanced Next Steps:\n";
    echo "   1. Update your .env file with the enhanced token above\n";
    echo "   2. Test connection with enhanced setup validation\n";
    echo "   3. All {$available_functions} MoodleClaude functions ready!\n";
    echo "   4. Enhanced dashboard features activated\n\n";
    
    // Create enhanced config file
    $config_data = [
        'service_name' => $service->name,
        'service_id' => $service->id,
        'service_shortname' => $service->shortname,
        'token' => $token,
        'user' => $service_user->username,
        'user_id' => $service_user->id,
        'functions_added' => $added_count,
        'functions_total' => $total_functions,
        'functions_coverage' => $coverage,
        'capabilities_enhanced' => count($required_capabilities),
        'webservice_url' => $CFG->wwwroot . '/webservice/rest/server.php',
        'setup_type' => 'enhanced_cli',
        'created' => date('Y-m-d H:i:s'),
    ];
    
    $config_file = '/tmp/moodleclaude_enhanced_config.json';
    file_put_contents($config_file, json_encode($config_data, JSON_PRETTY_PRINT));
    echo "💾 Enhanced configuration saved to: {$config_file}\n";

} catch (Exception $e) {
    echo "❌ ERROR: " . $e->getMessage() . "\n";
    echo "\n🔧 Enhanced Troubleshooting:\n";
    echo "   • Ensure you have site administrator privileges\n";
    echo "   • Check that web services are enabled in Moodle\n";
    echo "   • Verify database connection is working\n";
    echo "   • Run from Moodle root directory with CLI context\n";
    exit(1);
}

echo "\n🚀 MoodleClaude Enhanced Web Service Setup Complete!\n";
echo "Enhanced features activated with dashboard-style management! ✨\n";
?>
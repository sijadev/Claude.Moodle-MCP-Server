<?php
// MoodleClaude Web Service Setup Script
define('CLI_SCRIPT', true);
require_once('/bitnami/moodle/config.php');
require_once($CFG->libdir.'/adminlib.php');

echo "🚀 MoodleClaude Web Service Setup\n";
echo "================================\n";

// Enable web services
echo "🌐 Enabling web services...\n";
set_config('enablewebservices', 1);

// Enable REST protocol
echo "🔌 Enabling REST protocol...\n";
$protocols = explode(',', get_config('core', 'webserviceprotocols'));
if (!in_array('rest', $protocols)) {
    $protocols[] = 'rest';
    set_config('webserviceprotocols', implode(',', $protocols));
}

// Create/update web service
echo "⚙️  Setting up web service...\n";
$webservice = $DB->get_record('external_services', array('shortname' => 'moodleclaude_ws'));

if (!$webservice) {
    $webservice = new stdClass();
    $webservice->name = 'MoodleClaude Web Service';
    $webservice->shortname = 'moodleclaude_ws';
    $webservice->component = 'core';
    $webservice->timecreated = time();
    $webservice->timemodified = time();
    $webservice->enabled = 1;
    $webservice->restrictedusers = 0;
    $webservice->downloadfiles = 1;
    $webservice->uploadfiles = 1;
    $webservice->id = $DB->insert_record('external_services', $webservice);
    echo "✅ Created new web service\n";
} else {
    $webservice->enabled = 1;
    $webservice->restrictedusers = 0;
    $webservice->downloadfiles = 1;
    $webservice->uploadfiles = 1;
    $webservice->timemodified = time();
    $DB->update_record('external_services', $webservice);
    echo "✅ Updated existing web service\n";
}

// Add functions to web service
echo "🔧 Adding functions to web service...\n";
$functions = [
    'core_webservice_get_site_info',
    'core_course_get_courses',
    'core_course_create_courses',
    'core_course_delete_courses',
    'core_course_get_contents',
    'core_user_get_users',
    'core_user_create_users',
    'core_enrol_get_enrolled_users',
    'core_course_get_categories'
];

foreach ($functions as $function) {
    $exists = $DB->get_record('external_services_functions', [
        'externalserviceid' => $webservice->id,
        'functionname' => $function
    ]);
    
    if (!$exists) {
        $service_function = new stdClass();
        $service_function->externalserviceid = $webservice->id;
        $service_function->functionname = $function;
        $DB->insert_record('external_services_functions', $service_function);
        echo "  ✅ Added function: $function\n";
    } else {
        echo "  ℹ️  Function already exists: $function\n";
    }
}

// Get or create admin user token
echo "🔑 Setting up admin token...\n";
$admin = $DB->get_record('user', array('username' => 'admin'));
if ($admin) {
    $existing_token = $DB->get_record('external_tokens', [
        'userid' => $admin->id,
        'externalserviceid' => $webservice->id
    ]);
    
    if (!$existing_token) {
        $token = new stdClass();
        $token->token = md5(uniqid(rand(), true));
        $token->userid = $admin->id;
        $token->externalserviceid = $webservice->id;
        $token->contextid = context_system::instance()->id;
        $token->creatorid = $admin->id;
        $token->timecreated = time();
        $token->validuntil = 0; // Never expires
        $DB->insert_record('external_tokens', $token);
        echo "✅ Created admin token: {$token->token}\n";
    } else {
        echo "✅ Admin token exists: {$existing_token->token}\n";
    }
}

// Get or create wsuser token
echo "🔑 Setting up wsuser token...\n";
$wsuser = $DB->get_record('user', array('username' => 'wsuser'));
if ($wsuser) {
    $existing_token = $DB->get_record('external_tokens', [
        'userid' => $wsuser->id,
        'externalserviceid' => $webservice->id
    ]);
    
    if (!$existing_token) {
        $token = new stdClass();
        $token->token = md5(uniqid(rand(), true));
        $token->userid = $wsuser->id;
        $token->externalserviceid = $webservice->id;
        $token->contextid = context_system::instance()->id;
        $token->creatorid = $admin->id ?? 2;
        $token->timecreated = time();
        $token->validuntil = 0; // Never expires
        $DB->insert_record('external_tokens', $token);
        echo "✅ Created wsuser token: {$token->token}\n";
    } else {
        echo "✅ WSUser token exists: {$existing_token->token}\n";
    }
}

// Assign course creation capability to Manager role
echo "🎓 Setting up course creation capabilities...\n";
$manager_role = $DB->get_record('role', array('shortname' => 'manager'));
$context_system = context_system::instance();

if ($manager_role) {
    // Assign course creation capability
    $capability = 'moodle/course:create';
    
    $existing = $DB->get_record('role_capabilities', [
        'roleid' => $manager_role->id,
        'capability' => $capability,
        'contextid' => $context_system->id
    ]);
    
    if (!$existing) {
        $role_capability = new stdClass();
        $role_capability->contextid = $context_system->id;
        $role_capability->roleid = $manager_role->id;
        $role_capability->capability = $capability;
        $role_capability->permission = 1; // Allow
        $role_capability->timemodified = time();
        $role_capability->modifierid = $admin->id ?? 2;
        $DB->insert_record('role_capabilities', $role_capability);
        echo "✅ Added course creation capability to Manager role\n";
    } else {
        if ($existing->permission != 1) {
            $existing->permission = 1;
            $existing->timemodified = time();
            $DB->update_record('role_capabilities', $existing);
            echo "✅ Updated course creation capability for Manager role\n";
        } else {
            echo "ℹ️  Course creation capability already exists for Manager role\n";
        }
    }
    
    // Assign Manager role to admin and wsuser in system context
    foreach (['admin', 'wsuser'] as $username) {
        $user = $DB->get_record('user', array('username' => $username));
        if ($user) {
            $existing_assignment = $DB->get_record('role_assignments', [
                'roleid' => $manager_role->id,
                'userid' => $user->id,
                'contextid' => $context_system->id
            ]);
            
            if (!$existing_assignment) {
                $role_assignment = new stdClass();
                $role_assignment->roleid = $manager_role->id;
                $role_assignment->contextid = $context_system->id;
                $role_assignment->userid = $user->id;
                $role_assignment->timemodified = time();
                $role_assignment->modifierid = $admin->id ?? 2;
                $role_assignment->component = '';
                $role_assignment->itemid = 0;
                $role_assignment->sortorder = 0;
                $DB->insert_record('role_assignments', $role_assignment);
                echo "✅ Assigned Manager role to $username\n";
            } else {
                echo "ℹ️  Manager role already assigned to $username\n";
            }
        }
    }
}

echo "\n🎯 Setup complete! Web services should now work properly.\n";
echo "🔄 Please restart your web server and test the course creation functionality.\n";
?>
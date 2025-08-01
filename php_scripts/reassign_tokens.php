<?php
// Reassign existing tokens to MoodleClaude web service
define('CLI_SCRIPT', true);
require_once('/bitnami/moodle/config.php');

echo "🔄 Reassigning tokens to MoodleClaude web service\n";
echo "===============================================\n";

// Get our web service
$moodleclaude_service = $DB->get_record('external_services', array('shortname' => 'moodleclaude_ws'));
$mobile_service = $DB->get_record('external_services', array('shortname' => 'moodle_mobile_app'));

if (!$moodleclaude_service) {
    echo "❌ MoodleClaude web service not found!\n";
    exit(1);
}

if (!$mobile_service) {
    echo "❌ Mobile app web service not found!\n";
    exit(1);
}

echo "✅ Found MoodleClaude web service (ID: {$moodleclaude_service->id})\n";
echo "✅ Found Mobile app web service (ID: {$mobile_service->id})\n";

// Get tokens for admin and wsuser from mobile service
$admin = $DB->get_record('user', array('username' => 'admin'));
$wsuser = $DB->get_record('user', array('username' => 'wsuser'));

$tokens_updated = 0;

if ($admin) {
    $admin_token = $DB->get_record('external_tokens', [
        'userid' => $admin->id,
        'externalserviceid' => $mobile_service->id
    ]);
    
    if ($admin_token) {
        // Update the token to use our service
        $admin_token->externalserviceid = $moodleclaude_service->id;
        $DB->update_record('external_tokens', $admin_token);
        echo "✅ Reassigned admin token ({$admin_token->token}) to MoodleClaude service\n";
        $tokens_updated++;
    }
}

if ($wsuser) {
    $wsuser_token = $DB->get_record('external_tokens', [
        'userid' => $wsuser->id,
        'externalserviceid' => $mobile_service->id
    ]);
    
    if ($wsuser_token) {
        // Update the token to use our service
        $wsuser_token->externalserviceid = $moodleclaude_service->id;
        $DB->update_record('external_tokens', $wsuser_token);
        echo "✅ Reassigned wsuser token ({$wsuser_token->token}) to MoodleClaude service\n";
        $tokens_updated++;
    }
}

echo "\n🎯 Reassigned {$tokens_updated} tokens to MoodleClaude web service!\n";
echo "🔄 Tokens should now have course creation permissions.\n";
?>
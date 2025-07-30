<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Web service definitions for local_moodleclaude plugin
 *
 * @package    local_moodleclaude
 * @copyright  2025 MoodleClaude Project
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$functions = [
    'local_moodleclaude_create_page_activity' => [
        'classname'   => 'local_moodleclaude\external\create_page_activity',
        'methodname'  => 'execute',
        'description' => 'Create a page activity with content in a course section',
        'type'        => 'write',
        'capabilities' => 'moodle/course:manageactivities',
        'ajax'        => true,
        'loginrequired' => true,
    ],
    
    'local_moodleclaude_create_label_activity' => [
        'classname'   => 'local_moodleclaude\external\create_label_activity',
        'methodname'  => 'execute',
        'description' => 'Create a label activity with content in a course section',
        'type'        => 'write',
        'capabilities' => 'moodle/course:manageactivities',
        'ajax'        => true,
        'loginrequired' => true,
    ],
    
    'local_moodleclaude_create_file_resource' => [
        'classname'   => 'local_moodleclaude\external\create_file_resource',
        'methodname'  => 'execute',
        'description' => 'Create a file resource with downloadable content',
        'type'        => 'write',
        'capabilities' => 'moodle/course:manageactivities',
        'ajax'        => true,
        'loginrequired' => true,
    ],
    
    'local_moodleclaude_update_section_content' => [
        'classname'   => 'local_moodleclaude\external\update_section_content',
        'methodname'  => 'execute',
        'description' => 'Update section name and summary content',
        'type'        => 'write',
        'capabilities' => 'moodle/course:update',
        'ajax'        => true,
        'loginrequired' => true,
    ],
    
    'local_moodleclaude_create_course_structure' => [
        'classname'   => 'local_moodleclaude\external\create_course_structure',
        'methodname'  => 'execute',
        'description' => 'Create complete course structure with sections and activities from chat content',
        'type'        => 'write',
        'capabilities' => 'moodle/course:create',
        'ajax'        => true,
        'loginrequired' => true,
    ],
];

// Define the services
$services = [
    'MoodleClaude Content Creation Service' => [
        'functions' => [
            // MoodleClaude custom functions
            'local_moodleclaude_create_page_activity',
            'local_moodleclaude_create_label_activity', 
            'local_moodleclaude_create_file_resource',
            'local_moodleclaude_update_section_content',
            'local_moodleclaude_create_course_structure',
            
            // Essential core functions for web service operation
            'core_webservice_get_site_info',        // Required for token validation
            'core_course_create_courses',           // Required for course creation
            'core_course_get_courses',              // Required for course listing
            'core_course_get_categories',           // Required for category access
        ],
        'restrictedusers' => 1,  // Enable "Authorised users only" capability
        'enabled' => 1,
        'shortname' => 'moodleclaude_service',
        'downloadfiles' => 1,
        'uploadfiles' => 1,
    ],
];
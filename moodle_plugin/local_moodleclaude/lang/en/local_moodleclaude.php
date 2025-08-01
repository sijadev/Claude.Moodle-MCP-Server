<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Language strings for local_moodleclaude plugin
 *
 * @package    local_moodleclaude
 * @copyright  2025 MoodleClaude Project
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$string['pluginname'] = 'MoodleClaude Content Creator';
$string['privacy:metadata'] = 'The MoodleClaude plugin does not store any personal data.';

// Capabilities
$string['moodleclaude:createcontent'] = 'Create content using MoodleClaude';
$string['moodleclaude:managecourses'] = 'Manage courses using MoodleClaude';

// General strings
$string['servicename'] = 'MoodleClaude Content Creation Service';
$string['servicedescription'] = 'Web service for creating course content from Claude chat conversations';

// Error messages
$string['error:nocourse'] = 'Course not found';
$string['error:nosection'] = 'Section not found';
$string['error:permission'] = 'You do not have permission to perform this action';
$string['error:createactivity'] = 'Failed to create activity';
$string['error:updatesection'] = 'Failed to update section';

// Success messages
$string['success:activitycreated'] = 'Activity created successfully';
$string['success:sectionupdated'] = 'Section updated successfully';
$string['success:structurecreated'] = 'Course structure created successfully';

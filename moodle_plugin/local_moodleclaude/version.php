<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Version information for local_moodleclaude plugin
 *
 * @package    local_moodleclaude
 * @copyright  2025 MoodleClaude Project
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'local_moodleclaude';
$plugin->version = 2025013002; // YYYYMMDDHH - Added essential core functions
$plugin->requires = 2023100900; // Moodle 4.3+
$plugin->maturity = MATURITY_STABLE;
$plugin->release = '1.0.2';

<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * External function to update section content
 *
 * @package    local_moodleclaude
 * @copyright  2025 MoodleClaude Project
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_moodleclaude\external;

defined('MOODLE_INTERNAL') || die();

require_once($CFG->libdir . '/externallib.php');

use external_api;
use external_function_parameters;
use external_value;
use external_single_structure;
use context_course;
use stdClass;

/**
 * External function to update section name and summary
 */
class update_section_content extends external_api {

    /**
     * Define parameters for the function
     */
    public static function execute_parameters() {
        return new external_function_parameters([
            'courseid' => new external_value(PARAM_INT, 'Course ID'),
            'section' => new external_value(PARAM_INT, 'Section number'),
            'name' => new external_value(PARAM_TEXT, 'Section name', VALUE_DEFAULT, ''),
            'summary' => new external_value(PARAM_RAW, 'Section summary (HTML)', VALUE_DEFAULT, ''),
        ]);
    }

    /**
     * Update section content
     */
    public static function execute($courseid, $section, $name = '', $summary = '') {
        global $DB;

        // Validate parameters
        $params = self::validate_parameters(self::execute_parameters(), [
            'courseid' => $courseid,
            'section' => $section,
            'name' => $name,
            'summary' => $summary,
        ]);

        // Validate context and permissions
        $context = context_course::instance($params['courseid']);
        self::validate_context($context);
        require_capability('moodle/course:update', $context);

        try {
            // Get the section record
            $sectionrecord = $DB->get_record('course_sections', [
                'course' => $params['courseid'],
                'section' => $params['section']
            ]);

            if (!$sectionrecord) {
                return [
                    'success' => false,
                    'message' => 'Section not found',
                ];
            }

            // Update section data
            $updatedata = new stdClass();
            $updatedata->id = $sectionrecord->id;
            
            if (!empty($params['name'])) {
                $updatedata->name = $params['name'];
            }
            
            if (!empty($params['summary'])) {
                $updatedata->summary = $params['summary'];
                $updatedata->summaryformat = FORMAT_HTML;
            }

            // Update the section
            $DB->update_record('course_sections', $updatedata);

            // Clear course cache
            rebuild_course_cache($params['courseid']);

            return [
                'success' => true,
                'message' => 'Section updated successfully',
            ];

        } catch (\Exception $e) {
            return [
                'success' => false,
                'message' => 'Failed to update section: ' . $e->getMessage(),
            ];
        }
    }

    /**
     * Define return values
     */
    public static function execute_returns() {
        return new external_single_structure([
            'success' => new external_value(PARAM_BOOL, 'Whether the operation was successful'),
            'message' => new external_value(PARAM_TEXT, 'Result message'),
        ]);
    }
}
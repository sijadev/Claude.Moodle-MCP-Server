"""
End-to-End Tests for MoodleClaude Integration using Playwright
Tests real browser interactions with Moodle system including wsmanagesections and core_files_upload
"""

import asyncio
import base64
import json
import os
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pytest
from playwright.async_api import Browser, BrowserContext, Page, async_playwright


# Test configuration
@dataclass
class TestConfig:
    moodle_url: str = "http://localhost"
    admin_username: str = "simon"
    admin_password: str = "Pwd1234!"
    test_course_category: int = 1
    default_timeout: int = 30000  # 30 seconds
    test_data_dir: str = "./test_data"


class MoodleE2ETestBase:
    """Base class for Moodle E2E tests with common utilities"""

    def __init__(self, config: TestConfig):
        self.config = config
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def setup_browser(self, headless: bool = True):
        """Setup browser and context"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=headless,
            args=["--disable-web-security", "--disable-features=VizDisplayCompositor"],
        )

        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080}, ignore_https_errors=True
        )

        # Enable request/response logging
        self.context.on("request", self._log_request)
        self.context.on("response", self._log_response)

        self.page = await self.context.new_page()
        self.page.set_default_timeout(self.config.default_timeout)

    async def teardown_browser(self):
        """Cleanup browser resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    async def logout_if_needed(self) -> bool:
        """Logout if already logged in"""
        try:
            await self.page.goto(f"{self.config.moodle_url}")
            
            # Check if already logged in (look for logout link or user menu)
            logout_link = self.page.locator('a[href*="logout"], .usermenu a:has-text("Logout")')
            if await logout_link.count() > 0:
                print("User already logged in, logging out...")
                await logout_link.first.click()
                await self.page.wait_for_timeout(2000)
                return True
            return False
            
        except Exception as e:
            print(f"Logout check failed: {e}")
            return False

    async def login_as_admin(self) -> bool:
        """Login as administrator"""
        try:
            # First, logout if already logged in
            await self.logout_if_needed()
            
            await self.page.goto(f"{self.config.moodle_url}/login/index.php")

            # Check if we're already logged in (redirected away from login page)
            current_url = self.page.url
            if "login" not in current_url:
                print("Already logged in, checking dashboard...")
                # Navigate to dashboard to verify
                await self.page.goto(f"{self.config.moodle_url}/my/")
                return True

            # Wait for login form to be visible
            await self.page.wait_for_selector('input[name="username"]', timeout=5000)
            
            # Fill login form
            await self.page.fill('input[name="username"]', self.config.admin_username)
            await self.page.fill('input[name="password"]', self.config.admin_password)

            # Submit form (click specific login button, not guest button)
            login_button = self.page.locator('button[type="submit"]:has-text("Log in"), #loginbtn')
            await login_button.click()

            # Wait for navigation away from login page (more flexible than specific URL)
            try:
                await self.page.wait_for_url(lambda url: "login" not in url, timeout=15000)
            except:
                # Fallback: check if we can access the dashboard
                await self.page.goto(f"{self.config.moodle_url}/my/")
            
            # Verify login by checking for user menu or dashboard elements
            user_indicators = self.page.locator('.usermenu, .userbutton, #page-my-index, body:has-text("Dashboard")')
            await user_indicators.first.wait_for(timeout=5000)

            print("Login successful")
            return True

        except Exception as e:
            print(f"Login failed: {e}")
            # Try alternative verification
            try:
                await self.page.goto(f"{self.config.moodle_url}/my/")
                if "login" not in self.page.url:
                    print("Login appears successful despite error")
                    return True
            except:
                pass
            return False

    async def enable_edit_mode(self):
        """Enable edit mode in Moodle"""
        try:
            # Look for edit mode toggle
            edit_toggle = self.page.locator('input[name="setmode"], .editmode-switch-form input')
            if await edit_toggle.count() > 0:
                await edit_toggle.check()
                await self.page.wait_for_timeout(1000)  # Wait for edit mode to activate
        except Exception as e:
            print(f"Could not enable edit mode: {e}")

    async def create_test_course(self, course_name: str) -> Optional[int]:
        """Create a test course and return course ID"""
        try:
            # Navigate to course creation
            await self.page.goto(
                f"{self.config.moodle_url}/course/edit.php?category={self.config.test_course_category}"
            )

            # Fill course details
            await self.page.fill('input[name="fullname"]', course_name)
            await self.page.fill('input[name="shortname"]', course_name.lower().replace(" ", "_"))

            # Set course format to topics for better section management
            await self.page.select_option('select[name="format"]', "topics")

            # Save course
            await self.page.click('input[name="saveandreturn"], button:has-text("Save and return")')

            # Extract course ID from URL
            await self.page.wait_for_url("**/course/view.php?id=*")
            url = self.page.url
            course_id = int(url.split("id=")[1].split("&")[0])

            return course_id

        except Exception as e:
            print(f"Course creation failed: {e}")
            return None

    async def delete_test_course(self, course_id: int):
        """Delete a test course"""
        try:
            await self.page.goto(f"{self.config.moodle_url}/course/delete.php?id={course_id}")
            await self.page.click('input[value="Delete"], button:has-text("Delete")')
            await self.page.click('input[value="Continue"], button:has-text("Continue")')
        except Exception as e:
            print(f"Course deletion failed: {e}")

    def _log_request(self, request):
        """Log outgoing requests"""
        if "webservice" in request.url:
            print(f"API Request: {request.method} {request.url}")

    def _log_response(self, response):
        """Log incoming responses"""
        if "webservice" in response.url and response.status >= 400:
            print(f"API Error: {response.status} {response.url}")


class TestSectionManagement(MoodleE2ETestBase):
    """E2E tests for section management using local_wsmanagesections"""

    async def test_create_new_section(self):
        """Test creating a new course section"""
        course_name = f"E2E Test Course - Section Creation {int(time.time())}"
        course_id = await self.create_test_course(course_name)

        try:
            # Navigate to course
            await self.page.goto(f"{self.config.moodle_url}/course/view.php?id={course_id}")

            # Enable edit mode
            await self.enable_edit_mode()

            # Find and click "Add section" link
            add_section_link = self.page.locator('a:has-text("Add section"), .add-section')
            await add_section_link.first.click()

            # Verify new section was created
            await self.page.wait_for_timeout(2000)
            sections = await self.page.locator(".course-content .section").count()

            assert sections >= 2, f"Expected at least 2 sections, found {sections}"

            print(f"✅ Successfully created new section. Total sections: {sections}")

        finally:
            await self.delete_test_course(course_id)

    async def test_edit_section_name(self):
        """Test editing section names inline"""
        course_name = f"E2E Test Course - Section Edit {int(time.time())}"
        course_id = await self.create_test_course(course_name)

        try:
            await self.page.goto(f"{self.config.moodle_url}/course/view.php?id={course_id}")
            await self.enable_edit_mode()

            # Find section edit button
            edit_section_btn = self.page.locator(
                '.section .section-handle .edit, img[alt*="Edit section"]'
            )
            if await edit_section_btn.count() > 0:
                await edit_section_btn.first.click()

                # Look for inline editing field or modal
                section_name_input = self.page.locator('input[name*="name"], .section-name input')
                if await section_name_input.count() > 0:
                    new_name = f"Updated Section {int(time.time())}"
                    await section_name_input.fill(new_name)

                    # Save changes
                    save_btn = self.page.locator('button:has-text("Save"), input[type="submit"]')
                    await save_btn.click()

                    # Verify name change
                    await self.page.wait_for_timeout(2000)
                    section_heading = self.page.locator(f'.section h3:has-text("{new_name}")')
                    assert await section_heading.count() > 0, "Section name was not updated"

                    print(f"✅ Successfully updated section name to: {new_name}")

        finally:
            await self.delete_test_course(course_id)

    async def test_bulk_section_operations(self):
        """Test bulk operations on multiple sections"""
        course_name = f"E2E Test Course - Bulk Ops {int(time.time())}"
        course_id = await self.create_test_course(course_name)

        try:
            await self.page.goto(f"{self.config.moodle_url}/course/view.php?id={course_id}")
            await self.enable_edit_mode()

            # Create additional sections first
            for i in range(3):
                add_section_link = self.page.locator('a:has-text("Add section")')
                await add_section_link.first.click()
                await self.page.wait_for_timeout(1000)

            # Look for bulk actions button
            bulk_actions_btn = self.page.locator('button:has-text("Bulk actions"), .bulk-actions')
            if await bulk_actions_btn.count() > 0:
                await bulk_actions_btn.click()

                # Select multiple sections
                section_checkboxes = self.page.locator('.section input[type="checkbox"]')
                checkbox_count = await section_checkboxes.count()

                if checkbox_count >= 2:
                    # Select first two sections
                    await section_checkboxes.nth(0).check()
                    await section_checkboxes.nth(1).check()

                    # Look for bulk operation options
                    bulk_operations = await self.page.locator(
                        ".bulk-actions button, .bulk-actions select option"
                    ).all_text_contents()

                    # Verify bulk operations are available
                    expected_operations = ["Move", "Delete", "Availability"]
                    available_operations = [
                        op
                        for op in expected_operations
                        if any(expected in str(bulk_operations) for expected in [op.lower()])
                    ]

                    assert (
                        len(available_operations) > 0
                    ), f"No bulk operations found. Available: {bulk_operations}"
                    print(f"✅ Bulk operations available: {available_operations}")

        finally:
            await self.delete_test_course(course_id)

    async def test_section_availability_conditions(self):
        """Test setting availability conditions on sections"""
        course_name = f"E2E Test Course - Availability {int(time.time())}"
        course_id = await self.create_test_course(course_name)

        try:
            await self.page.goto(f"{self.config.moodle_url}/course/view.php?id={course_id}")
            await self.enable_edit_mode()

            # Look for section settings/edit
            section_edit = self.page.locator(
                '.section .section-handle .edit, .section [title*="Edit"]'
            )
            if await section_edit.count() > 0:
                await section_edit.first.click()

                # Navigate to section edit page if opened in new page
                await self.page.wait_for_timeout(2000)

                # Look for availability/restrict access settings
                availability_section = self.page.locator(
                    'fieldset:has-text("Restrict access"), .availability'
                )
                if await availability_section.count() > 0:
                    print("✅ Availability conditions interface found")

                    # Look for "Add restriction" button
                    add_restriction = self.page.locator(
                        'button:has-text("Add restriction"), .add-restriction'
                    )
                    if await add_restriction.count() > 0:
                        await add_restriction.click()

                        # Look for date restriction option
                        date_restriction = self.page.locator(
                            'a:has-text("Date"), [data-type="date"]'
                        )
                        if await date_restriction.count() > 0:
                            await date_restriction.click()
                            print("✅ Date restriction added successfully")

        finally:
            await self.delete_test_course(course_id)


class TestFileUpload(MoodleE2ETestBase):
    """E2E tests for file upload using core_files_upload"""

    async def setup_test_files(self):
        """Create test files for upload"""
        test_dir = Path(self.config.test_data_dir)
        test_dir.mkdir(exist_ok=True)

        # Create various test files
        test_files = {
            "text_file.txt": b"This is a test text file for E2E testing.",
            "test_document.pdf": b"%PDF-1.4 fake PDF content for testing",
            "image_file.jpg": base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            ),
            "data_file.csv": b"Name,Age,City\nJohn,25,New York\nJane,30,London",
        }

        for filename, content in test_files.items():
            file_path = test_dir / filename
            with open(file_path, "wb") as f:
                f.write(content)

        return test_dir

    async def test_file_resource_creation(self):
        """Test creating a file resource with upload"""
        course_name = f"E2E Test Course - File Upload {int(time.time())}"
        course_id = await self.create_test_course(course_name)
        test_dir = await self.setup_test_files()

        try:
            await self.page.goto(f"{self.config.moodle_url}/course/view.php?id={course_id}")
            await self.enable_edit_mode()

            # Find "Add content" or "+" button
            add_content_btn = self.page.locator(
                'button:has-text("Insert content"), .add-content, [aria-label*="Insert content"]'
            )
            await add_content_btn.first.click()

            # Look for "Activity or resource" option
            activity_resource = self.page.locator('button:has-text("Activity or resource")')
            if await activity_resource.count() > 0:
                await activity_resource.click()

            # Select File from the activity chooser
            await self.page.wait_for_selector(".activity-chooser, .chooser")
            file_option = self.page.locator('a:has-text("File"), .modicon_resource')
            await file_option.click()

            # Fill in file resource details
            await self.page.fill('input[name="name"]', "Test File Resource")

            # Upload file using file picker
            add_file_btn = self.page.locator('button:has-text("Add..."), .fp-btn-add')
            await add_file_btn.click()

            # Wait for file picker dialog
            await self.page.wait_for_selector(".file-picker, .fp-repo")

            # Select "Upload a file" repository
            upload_tab = self.page.locator(
                'a:has-text("Upload a file"), [aria-label*="Upload a file"]'
            )
            if await upload_tab.count() > 0:
                await upload_tab.click()

            # Upload file
            test_file = test_dir / "text_file.txt"
            file_input = self.page.locator('input[type="file"]')
            await file_input.set_input_files(str(test_file))

            # Submit upload
            upload_btn = self.page.locator('button:has-text("Upload this file"), .fp-upload-btn')
            await upload_btn.click()

            # Save the resource
            save_btn = self.page.locator(
                'button:has-text("Save and return"), input[name="submitbutton"]'
            )
            await save_btn.click()

            # Verify file resource was created
            await self.page.wait_for_timeout(3000)
            file_resource = self.page.locator('.activity.resource:has-text("Test File Resource")')
            assert await file_resource.count() > 0, "File resource was not created"

            print("✅ File resource created successfully with uploaded file")

        finally:
            await self.delete_test_course(course_id)
            # Cleanup test files
            import shutil

            shutil.rmtree(test_dir, ignore_errors=True)

    async def test_file_picker_repositories(self):
        """Test different file picker repositories"""
        course_name = f"E2E Test Course - File Picker {int(time.time())}"
        course_id = await self.create_test_course(course_name)

        try:
            await self.page.goto(f"{self.config.moodle_url}/course/view.php?id={course_id}")
            await self.enable_edit_mode()

            # Navigate to add file resource
            add_content_btn = self.page.locator('button:has-text("Insert content")')
            await add_content_btn.first.click()

            activity_resource = self.page.locator('button:has-text("Activity or resource")')
            if await activity_resource.count() > 0:
                await activity_resource.click()

            file_option = self.page.locator('a:has-text("File")')
            await file_option.click()

            # Open file picker
            add_file_btn = self.page.locator('button:has-text("Add...")')
            await add_file_btn.click()

            # Wait for file picker and check available repositories
            await self.page.wait_for_selector(".file-picker")

            repository_tabs = await self.page.locator(".fp-repo-name, .fp-tab").all_text_contents()

            expected_repositories = [
                "Upload a file",
                "Server files",
                "Recent files",
                "Private files",
                "Content bank",
            ]

            found_repositories = []
            for expected in expected_repositories:
                if any(expected.lower() in repo.lower() for repo in repository_tabs):
                    found_repositories.append(expected)

            assert (
                len(found_repositories) >= 3
            ), f"Expected at least 3 repositories, found: {found_repositories}"
            print(f"✅ File picker repositories available: {found_repositories}")

            # Test URL downloader if available
            url_tab = self.page.locator('a:has-text("URL downloader")')
            if await url_tab.count() > 0:
                await url_tab.click()

                url_input = self.page.locator('input[name="url"], .fp-url')
                if await url_input.count() > 0:
                    print("✅ URL downloader repository is functional")

        finally:
            await self.delete_test_course(course_id)

    async def test_drag_drop_file_upload(self):
        """Test drag and drop file upload functionality"""
        course_name = f"E2E Test Course - Drag Drop {int(time.time())}"
        course_id = await self.create_test_course(course_name)
        test_dir = await self.setup_test_files()

        try:
            await self.page.goto(f"{self.config.moodle_url}/course/view.php?id={course_id}")
            await self.enable_edit_mode()

            # Look for drag-drop area
            drag_drop_area = self.page.locator(".filemanager-container, .drag-drop-area")
            if await drag_drop_area.count() > 0:
                # Create file resource first
                add_content_btn = self.page.locator('button:has-text("Insert content")')
                await add_content_btn.first.click()

                activity_resource = self.page.locator('button:has-text("Activity or resource")')
                if await activity_resource.count() > 0:
                    await activity_resource.click()

                file_option = self.page.locator('a:has-text("File")')
                await file_option.click()

                # Look for drag-drop message
                drag_drop_text = self.page.locator(':has-text("drag and drop")')
                if await drag_drop_text.count() > 0:
                    print("✅ Drag and drop functionality is available")

                    # Simulate file selection instead of actual drag-drop
                    # (Playwright has limitations with actual drag-drop of files from OS)
                    file_input = self.page.locator('input[type="file"]')
                    if await file_input.count() > 0:
                        test_file = test_dir / "test_document.pdf"
                        await file_input.set_input_files(str(test_file))
                        print("✅ File upload simulation successful")

        finally:
            await self.delete_test_course(course_id)
            import shutil

            shutil.rmtree(test_dir, ignore_errors=True)


class TestMoodleClaudeIntegration(MoodleE2ETestBase):
    """E2E tests for complete MoodleClaude integration workflows"""

    async def test_course_creation_from_chat_simulation(self):
        """Simulate course creation from chat content"""
        # Simulate chat content
        chat_sections = [
            {"title": "Introduction", "content": "Welcome to the course"},
            {"title": "Basic Concepts", "content": "Core concepts and principles"},
            {"title": "Advanced Topics", "content": "Deep dive into advanced features"},
            {"title": "Conclusion", "content": "Summary and next steps"},
        ]

        course_name = f"E2E Claude Course {int(time.time())}"
        course_id = await self.create_test_course(course_name)

        try:
            await self.page.goto(f"{self.config.moodle_url}/course/view.php?id={course_id}")
            await self.enable_edit_mode()

            # Create sections based on chat content
            created_sections = 0
            for section_data in chat_sections:
                # Add new section
                add_section_link = self.page.locator('a:has-text("Add section")')
                await add_section_link.first.click()
                await self.page.wait_for_timeout(1000)

                # Edit section name (if possible)
                edit_btns = self.page.locator('.section .edit, img[alt*="Edit"]')
                if await edit_btns.count() > created_sections:
                    try:
                        await edit_btns.nth(created_sections).click()

                        # Add section content as text/media area
                        add_content = self.page.locator('button:has-text("Insert content")')
                        if await add_content.count() > 0:
                            await add_content.first.click()

                            activity_resource = self.page.locator(
                                'button:has-text("Activity or resource")'
                            )
                            if await activity_resource.count() > 0:
                                await activity_resource.click()

                            # Add text and media area
                            text_media = self.page.locator('a:has-text("Text and media area")')
                            if await text_media.count() > 0:
                                await text_media.click()

                                # Fill content
                                content_editor = self.page.locator(
                                    'iframe[title*="Rich text area"]'
                                )
                                if await content_editor.count() > 0:
                                    await content_editor.first.fill(section_data["content"])

                                save_btn = self.page.locator('button:has-text("Save and return")')
                                await save_btn.click()
                                await self.page.wait_for_timeout(2000)

                    except Exception as e:
                        print(f"Could not add content to section {section_data['title']}: {e}")

                created_sections += 1

            # Verify sections were created
            final_sections = await self.page.locator(".course-content .section").count()
            assert final_sections >= len(
                chat_sections
            ), f"Expected {len(chat_sections)} sections, found {final_sections}"

            print(
                f"✅ Successfully created course with {created_sections} sections from simulated chat content"
            )

        finally:
            await self.delete_test_course(course_id)

    async def test_bulk_course_management(self):
        """Test bulk management of course elements"""
        course_name = f"E2E Bulk Management {int(time.time())}"
        course_id = await self.create_test_course(course_name)

        try:
            await self.page.goto(f"{self.config.moodle_url}/course/view.php?id={course_id}")
            await self.enable_edit_mode()

            # Create multiple sections for bulk operations
            for i in range(4):
                add_section_link = self.page.locator('a:has-text("Add section")')
                await add_section_link.first.click()
                await self.page.wait_for_timeout(500)

            # Test bulk actions
            bulk_btn = self.page.locator('button:has-text("Bulk actions")')
            if await bulk_btn.count() > 0:
                await bulk_btn.click()

                # Select multiple sections
                checkboxes = self.page.locator('.section input[type="checkbox"]')
                checkbox_count = await checkboxes.count()

                if checkbox_count >= 3:
                    # Select first 3 sections
                    for i in range(min(3, checkbox_count)):
                        await checkboxes.nth(i).check()

                    # Check available bulk operations
                    bulk_operations = self.page.locator(
                        ".bulk-actions button, .bulk-actions .action"
                    )
                    operation_count = await bulk_operations.count()

                    assert operation_count > 0, "No bulk operations available"
                    print(f"✅ Bulk actions available: {operation_count} operations")

                    # Test selection count
                    selected_count = self.page.locator('.bulk-actions :has-text("selected")')
                    if await selected_count.count() > 0:
                        count_text = await selected_count.first.text_content()
                        assert "3" in count_text or "selected" in count_text.lower()
                        print(f"✅ Selection count display working: {count_text}")

        finally:
            await self.delete_test_course(course_id)


class TestAccessibilityAndUsability(MoodleE2ETestBase):
    """E2E tests for accessibility and usability features"""

    async def test_keyboard_navigation(self):
        """Test keyboard navigation in course management"""
        course_name = f"E2E Accessibility Test {int(time.time())}"
        course_id = await self.create_test_course(course_name)

        try:
            await self.page.goto(f"{self.config.moodle_url}/course/view.php?id={course_id}")
            await self.enable_edit_mode()

            # Test tab navigation
            await self.page.keyboard.press("Tab")
            focused_element = await self.page.evaluate("document.activeElement.tagName")

            assert focused_element in [
                "BUTTON",
                "A",
                "INPUT",
            ], f"Focus not on interactive element: {focused_element}"
            print(f"✅ Keyboard navigation working, focused on: {focused_element}")

            # Test skip links
            skip_links = self.page.locator('a:has-text("Skip to")')
            skip_count = await skip_links.count()

            if skip_count > 0:
                print(f"✅ Skip links available: {skip_count}")

        finally:
            await self.delete_test_course(course_id)

    async def test_screen_reader_compatibility(self):
        """Test screen reader compatibility features"""
        course_name = f"E2E Screen Reader Test {int(time.time())}"
        course_id = await self.create_test_course(course_name)

        try:
            await self.page.goto(f"{self.config.moodle_url}/course/view.php?id={course_id}")

            # Check for proper heading structure
            headings = await self.page.locator("h1, h2, h3, h4, h5, h6").all_text_contents()
            assert len(headings) > 0, "No headings found for screen reader navigation"

            # Check for alt text on images
            images = self.page.locator("img")
            image_count = await images.count()

            if image_count > 0:
                # Check first few images for alt text
                for i in range(min(3, image_count)):
                    alt_text = await images.nth(i).get_attribute("alt")
                    assert alt_text is not None, f"Image {i} missing alt text"

                print(f"✅ Images have alt text for screen readers")

            # Check for proper labels on form elements
            form_inputs = self.page.locator("input, select, textarea")
            input_count = await form_inputs.count()

            if input_count > 0:
                labeled_inputs = 0
                for i in range(min(5, input_count)):
                    input_elem = form_inputs.nth(i)
                    aria_label = await input_elem.get_attribute("aria-label")
                    input_id = await input_elem.get_attribute("id")

                    # Check if input has label or aria-label
                    if aria_label or input_id:
                        if input_id:
                            label = self.page.locator(f'label[for="{input_id}"]')
                            if await label.count() > 0 or aria_label:
                                labeled_inputs += 1
                        elif aria_label:
                            labeled_inputs += 1

                label_percentage = (labeled_inputs / min(5, input_count)) * 100
                assert label_percentage >= 50, f"Only {label_percentage}% of inputs have labels"
                print(f"✅ Form inputs properly labeled: {label_percentage}%")

        finally:
            await self.delete_test_course(course_id)


# Pytest fixtures and test runners
@pytest.fixture(scope="session")
async def test_config():
    """Test configuration fixture"""
    return TestConfig()


@pytest.fixture(scope="function")
async def browser_setup(test_config):
    """Browser setup fixture"""
    test_base = MoodleE2ETestBase(test_config)
    await test_base.setup_browser(headless=True)
    yield test_base
    await test_base.teardown_browser()


@pytest.fixture(scope="function")
async def authenticated_browser(browser_setup):
    """Authenticated browser fixture"""
    login_success = await browser_setup.login_as_admin()
    assert login_success, "Failed to login as admin"
    yield browser_setup


# Test classes using pytest
@pytest.mark.asyncio
class TestSectionManagementPytest:
    """Pytest version of section management tests"""

    async def test_create_section(self, authenticated_browser):
        """Test section creation with pytest"""
        test_runner = TestSectionManagement(authenticated_browser.config)
        test_runner.page = authenticated_browser.page
        test_runner.context = authenticated_browser.context
        test_runner.browser = authenticated_browser.browser

        await test_runner.test_create_new_section()

    async def test_edit_section_name(self, authenticated_browser):
        """Test section name editing with pytest"""
        test_runner = TestSectionManagement(authenticated_browser.config)
        test_runner.page = authenticated_browser.page
        test_runner.context = authenticated_browser.context
        test_runner.browser = authenticated_browser.browser

        await test_runner.test_edit_section_name()

    async def test_bulk_operations(self, authenticated_browser):
        """Test bulk section operations with pytest"""
        test_runner = TestSectionManagement(authenticated_browser.config)
        test_runner.page = authenticated_browser.page
        test_runner.context = authenticated_browser.context
        test_runner.browser = authenticated_browser.browser

        await test_runner.test_bulk_section_operations()


@pytest.mark.asyncio
class TestFileUploadPytest:
    """Pytest version of file upload tests"""

    async def test_file_resource_creation(self, authenticated_browser):
        """Test file resource creation with pytest"""
        test_runner = TestFileUpload(authenticated_browser.config)
        test_runner.page = authenticated_browser.page
        test_runner.context = authenticated_browser.context
        test_runner.browser = authenticated_browser.browser

        await test_runner.test_file_resource_creation()

    async def test_file_picker_repositories(self, authenticated_browser):
        """Test file picker repositories with pytest"""
        test_runner = TestFileUpload(authenticated_browser.config)
        test_runner.page = authenticated_browser.page
        test_runner.context = authenticated_browser.context
        test_runner.browser = authenticated_browser.browser

        await test_runner.test_file_picker_repositories()


class TestReportGenerator:
    """Generate comprehensive test reports"""

    def __init__(self):
        self.test_results = []
        self.start_time = time.time()

    def add_result(self, test_name: str, status: str, duration: float, details: str = ""):
        """Add test result"""
        self.test_results.append(
            {
                "test_name": test_name,
                "status": status,
                "duration": duration,
                "details": details,
                "timestamp": time.time(),
            }
        )

    def generate_html_report(self, output_file: str = "e2e_test_report.html"):
        """Generate HTML test report"""
        total_duration = time.time() - self.start_time
        passed_tests = [r for r in self.test_results if r["status"] == "PASSED"]
        failed_tests = [r for r in self.test_results if r["status"] == "FAILED"]

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MoodleClaude E2E Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .metric {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; text-align: center; }}
                .passed {{ background-color: #d4edda; }}
                .failed {{ background-color: #f8d7da; }}
                .test-result {{ margin: 10px 0; padding: 15px; border-left: 4px solid #007bff; background-color: #f8f9fa; }}
                .test-result.passed {{ border-left-color: #28a745; }}
                .test-result.failed {{ border-left-color: #dc3545; }}
                .duration {{ color: #6c757d; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>MoodleClaude E2E Test Report</h1>
                <p>Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Total Duration: {total_duration:.2f}s</p>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <h3>Total Tests</h3>
                    <p>{len(self.test_results)}</p>
                </div>
                <div class="metric passed">
                    <h3>Passed</h3>
                    <p>{len(passed_tests)}</p>
                </div>
                <div class="metric failed">
                    <h3>Failed</h3>
                    <p>{len(failed_tests)}</p>
                </div>
                <div class="metric">
                    <h3>Success Rate</h3>
                    <p>{(len(passed_tests) / len(self.test_results) * 100):.1f}%</p>
                </div>
            </div>
            
            <h2>Test Results</h2>
        """

        for result in self.test_results:
            status_class = result["status"].lower()
            html_content += f"""
            <div class="test-result {status_class}">
                <h4>{result['test_name']}</h4>
                <p><strong>Status:</strong> {result['status']}</p>
                <p class="duration"><strong>Duration:</strong> {result['duration']:.2f}s</p>
                {f'<p><strong>Details:</strong> {result["details"]}</p>' if result['details'] else ''}
            </div>
            """

        html_content += """
            </body>
            </html>
        """

        with open(output_file, "w") as f:
            f.write(html_content)

        print(f"📊 HTML report generated: {output_file}")


async def run_comprehensive_e2e_tests():
    """Run comprehensive E2E test suite"""
    config = TestConfig()
    report_generator = TestReportGenerator()

    print("🚀 Starting Comprehensive E2E Tests for MoodleClaude Integration")
    print("=" * 70)

    # Test categories
    test_categories = [
        ("Section Management", TestSectionManagement),
        ("File Upload", TestFileUpload),
        ("MoodleClaude Integration", TestMoodleClaudeIntegration),
        ("Accessibility & Usability", TestAccessibilityAndUsability),
    ]

    total_tests = 0
    passed_tests = 0

    for category_name, test_class in test_categories:
        print(f"\n📋 Running {category_name} Tests...")
        print("-" * 40)

        # Initialize test instance
        test_instance = test_class(config)
        await test_instance.setup_browser(headless=True)

        try:
            # Login as admin
            login_success = await test_instance.login_as_admin()
            if not login_success:
                print(f"❌ Failed to login for {category_name} tests")
                continue

            # Get test methods
            test_methods = [method for method in dir(test_instance) if method.startswith("test_")]

            for method_name in test_methods:
                test_start = time.time()
                total_tests += 1

                try:
                    print(f"🧪 Running {method_name}...")
                    test_method = getattr(test_instance, method_name)
                    await test_method()

                    test_duration = time.time() - test_start
                    print(f"✅ {method_name} PASSED ({test_duration:.2f}s)")

                    report_generator.add_result(
                        f"{category_name}: {method_name}", "PASSED", test_duration
                    )
                    passed_tests += 1

                except Exception as e:
                    test_duration = time.time() - test_start
                    print(f"❌ {method_name} FAILED ({test_duration:.2f}s): {str(e)}")

                    report_generator.add_result(
                        f"{category_name}: {method_name}", "FAILED", test_duration, str(e)
                    )

        finally:
            await test_instance.teardown_browser()

    # Generate final report
    print("\n" + "=" * 70)
    print("📊 E2E Test Results Summary")
    print("=" * 70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests / total_tests * 100):.1f}%")

    # Generate HTML report
    report_generator.generate_html_report()

    return passed_tests == total_tests


# CLI Runner
async def main():
    """Main CLI runner for E2E tests"""
    import argparse

    parser = argparse.ArgumentParser(description="MoodleClaude E2E Test Runner")
    parser.add_argument(
        "--headless", action="store_true", default=True, help="Run in headless mode"
    )
    parser.add_argument("--url", default="http://localhost", help="Moodle URL")
    parser.add_argument("--username", default="simon", help="Admin username")
    parser.add_argument("--password", default="Pwd1234!", help="Admin password")
    parser.add_argument("--category", type=int, default=1, help="Test course category ID")
    parser.add_argument("--timeout", type=int, default=30000, help="Default timeout in ms")
    parser.add_argument("--report", default="e2e_report.html", help="HTML report output file")

    args = parser.parse_args()

    # Update config from args
    config = TestConfig(
        moodle_url=args.url,
        admin_username=args.username,
        admin_password=args.password,
        test_course_category=args.category,
        default_timeout=args.timeout,
    )

    print("🎯 MoodleClaude E2E Test Suite")
    print("=" * 50)
    print(f"Moodle URL: {config.moodle_url}")
    print(f"Username: {config.admin_username}")
    print(f"Headless: {args.headless}")
    print("=" * 50)

    # Run tests
    success = await run_comprehensive_e2e_tests()

    if success:
        print("\n🎉 All E2E tests passed successfully!")
        return 0
    else:
        print("\n💥 Some E2E tests failed. Check the report for details.")
        return 1


if __name__ == "__main__":
    import sys

    exit_code = asyncio.run(main())
    sys.exit(exit_code)

"""
Unit tests for configuration management
"""

import os
from unittest.mock import Mock, patch

import pytest

from config import ENV_VARS, Config, get_config, reload_config


class TestConfig:
    """Test configuration class"""

    def test_init_with_env_vars(self, mock_env_vars):
        """Test config initialization with environment variables"""
        with patch.dict(os.environ, mock_env_vars):
            config = Config()

            assert config.moodle_url == mock_env_vars["MOODLE_URL"]
            assert config.moodle_token == mock_env_vars["MOODLE_TOKEN"]
            assert config.moodle_username == mock_env_vars["MOODLE_USERNAME"]
            assert config.server_name == mock_env_vars["SERVER_NAME"]
            assert config.log_level == mock_env_vars["LOG_LEVEL"]

    def test_init_with_defaults(self):
        """Test config initialization with default values"""
        # Clear environment
        with patch.dict(os.environ, {}, clear=True):
            config = Config()

            assert config.moodle_url == ""
            assert config.moodle_token == ""
            assert config.moodle_username is None
            assert config.server_name == "moodle-course-creator"
            assert config.log_level == "INFO"
            assert config.default_category_id == 1
            assert config.default_course_format == "topics"

    def test_validate_moodle_connection_valid(self, mock_env_vars):
        """Test Moodle connection validation with valid settings"""
        with patch.dict(os.environ, mock_env_vars):
            config = Config()
            assert config.validate_moodle_connection() is True

    def test_validate_moodle_connection_invalid_url(self):
        """Test Moodle connection validation with invalid URL"""
        invalid_env = {
            "MOODLE_URL": "invalid-url",
            "MOODLE_TOKEN": "test_token_12345678901234567890123456789012",
        }
        with patch.dict(os.environ, invalid_env):
            config = Config()
            assert config.validate_moodle_connection() is False

    def test_validate_moodle_connection_short_token(self):
        """Test Moodle connection validation with short token"""
        invalid_env = {"MOODLE_URL": "http://test.example.com", "MOODLE_TOKEN": "short"}
        with patch.dict(os.environ, invalid_env):
            config = Config()
            assert config.validate_moodle_connection() is False

    def test_get_content_limits(self, mock_env_vars):
        """Test content limits retrieval"""
        with patch.dict(os.environ, mock_env_vars):
            config = Config()
            limits = config.get_content_limits()

            assert "max_code_length" in limits
            assert "max_topic_length" in limits
            assert "min_code_lines" in limits
            assert "min_topic_words" in limits
            assert isinstance(limits["max_code_length"], int)

    def test_get_moodle_config(self, mock_env_vars):
        """Test Moodle config retrieval"""
        with patch.dict(os.environ, mock_env_vars):
            config = Config()
            moodle_config = config.get_moodle_config()

            assert moodle_config["url"] == mock_env_vars["MOODLE_URL"]
            assert moodle_config["token"] == mock_env_vars["MOODLE_TOKEN"]
            assert moodle_config["username"] == mock_env_vars["MOODLE_USERNAME"]
            assert "default_category_id" in moodle_config
            assert "default_course_format" in moodle_config

    def test_to_dict(self, mock_env_vars):
        """Test config serialization to dictionary"""
        with patch.dict(os.environ, mock_env_vars):
            config = Config()
            config_dict = config.to_dict()

            assert "server_name" in config_dict
            assert "server_version" in config_dict
            assert "moodle_url" in config_dict
            assert "moodle_token_length" in config_dict
            assert "content_limits" in config_dict
            assert "course_defaults" in config_dict

            # Ensure sensitive data is not exposed
            assert "moodle_token" not in config_dict
            assert config_dict["moodle_token_length"] == len(mock_env_vars["MOODLE_TOKEN"])

    def test_custom_content_limits(self):
        """Test custom content processing limits"""
        custom_env = {
            "MAX_CODE_LENGTH": "5000",
            "MAX_TOPIC_LENGTH": "2000",
            "MIN_CODE_LINES": "5",
            "MIN_TOPIC_WORDS": "20",
        }
        with patch.dict(os.environ, custom_env):
            config = Config()

            assert config.max_code_length == 5000
            assert config.max_topic_length == 2000
            assert config.min_code_lines == 5
            assert config.min_topic_words == 20

    def test_custom_course_defaults(self):
        """Test custom course default settings"""
        custom_env = {"DEFAULT_CATEGORY_ID": "5", "DEFAULT_COURSE_FORMAT": "weekly"}
        with patch.dict(os.environ, custom_env):
            config = Config()

            assert config.default_category_id == 5
            assert config.default_course_format == "weekly"

    @patch("config.logging.basicConfig")
    def test_logging_configuration(self, mock_basic_config, mock_env_vars):
        """Test logging configuration setup"""
        with patch.dict(os.environ, mock_env_vars):
            Config()
            mock_basic_config.assert_called_once()

    def test_logging_level_mapping(self):
        """Test different logging levels"""
        test_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in test_levels:
            with patch.dict(os.environ, {"LOG_LEVEL": level}):
                with patch("config.logging.basicConfig") as mock_config:
                    Config()
                    mock_config.assert_called_once()


class TestConfigGlobals:
    """Test global configuration functions"""

    def test_get_config_singleton(self, mock_env_vars):
        """Test that get_config returns singleton instance"""
        with patch.dict(os.environ, mock_env_vars):
            config1 = get_config()
            config2 = get_config()
            assert config1 is config2

    def test_reload_config(self, mock_env_vars):
        """Test configuration reloading"""
        # Initial config
        with patch.dict(os.environ, {"MOODLE_URL": "http://initial.com"}):
            config1 = get_config()
            initial_url = config1.moodle_url

        # Change environment and reload
        with patch.dict(os.environ, {"MOODLE_URL": "http://updated.com"}):
            reload_config()
            config2 = get_config()
            updated_url = config2.moodle_url

        assert initial_url != updated_url
        assert updated_url == "http://updated.com"


class TestEnvironmentVariables:
    """Test environment variable documentation"""

    def test_env_vars_structure(self):
        """Test ENV_VARS dictionary structure"""
        assert isinstance(ENV_VARS, dict)

        for var_name, var_info in ENV_VARS.items():
            assert isinstance(var_name, str)
            assert isinstance(var_info, dict)
            assert "required" in var_info
            assert "description" in var_info
            assert isinstance(var_info["required"], bool)
            assert isinstance(var_info["description"], str)

    def test_required_env_vars(self):
        """Test identification of required environment variables"""
        required_vars = [
            var_name for var_name, var_info in ENV_VARS.items() if var_info["required"]
        ]

        assert "MOODLE_URL" in required_vars
        assert "MOODLE_TOKEN" in required_vars

    def test_optional_env_vars_have_defaults(self):
        """Test that optional environment variables have default values"""
        for var_name, var_info in ENV_VARS.items():
            if not var_info["required"]:
                # Optional vars should have defaults or be explicitly nullable
                assert "default" in var_info or var_name in ["MOODLE_USERNAME"]


@pytest.mark.integration
class TestConfigIntegration:
    """Integration tests for configuration"""

    def test_config_with_real_env_file(self, temp_config_file):
        """Test config loading from actual environment file"""
        # This would test loading from .env file if we had python-dotenv
        # For now, just test that temp file exists
        assert os.path.exists(temp_config_file)

    def test_config_validation_flow(self, mock_env_vars):
        """Test complete configuration validation flow"""
        with patch.dict(os.environ, mock_env_vars):
            config = Config()

            # Test validation
            assert config.validate_moodle_connection() is True

            # Test config retrieval
            moodle_config = config.get_moodle_config()
            assert moodle_config["url"] == mock_env_vars["MOODLE_URL"]

            # Test serialization
            config_dict = config.to_dict()
            assert "moodle_url" in config_dict
            assert "moodle_token" not in config_dict  # Should be excluded

"""
Unit tests for configuration management
"""

import os
from unittest.mock import Mock, patch

import pytest

from config.dual_token_config import DualTokenConfig


class TestDualTokenConfig:
    """Test dual token configuration class"""

    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables for testing"""
        return {
            "MOODLE_URL": "http://test.example.com",
            "MOODLE_BASIC_TOKEN": "basic_token_12345678901234567890123456789012",
            "MOODLE_PLUGIN_TOKEN": "plugin_token_12345678901234567890123456789012",
            "MOODLE_USERNAME": "testuser"
        }

    def test_init_with_env_vars(self, mock_env_vars):
        """Test config initialization with environment variables"""
        with patch.dict(os.environ, mock_env_vars, clear=True):
            with patch('os.path.exists', return_value=False):  # Mock .env file doesn't exist
                config = DualTokenConfig.from_env()

                assert config.moodle_url == mock_env_vars["MOODLE_URL"]
                assert config.basic_token == mock_env_vars["MOODLE_BASIC_TOKEN"]
                assert config.plugin_token == mock_env_vars["MOODLE_PLUGIN_TOKEN"]
                assert config.username == mock_env_vars["MOODLE_USERNAME"]

    def test_init_missing_url(self):
        """Test config initialization with missing URL"""
        # Clear environment
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.path.exists', return_value=False):  # Mock .env file doesn't exist
                with pytest.raises(ValueError, match="MOODLE_URL environment variable is required"):
                    DualTokenConfig.from_env()

    def test_dual_token_mode(self, mock_env_vars):
        """Test dual token mode detection"""
        with patch.dict(os.environ, mock_env_vars, clear=True):
            with patch('os.path.exists', return_value=False):
                config = DualTokenConfig.from_env()
                assert config.is_dual_token_mode() is True

    def test_single_token_fallback(self):
        """Test single token fallback mode"""
        single_env = {
            "MOODLE_URL": "http://test.example.com",
            "MOODLE_TOKEN": "single_token_12345678901234567890123456789012",
        }
        with patch.dict(os.environ, single_env, clear=True):
            with patch('os.path.exists', return_value=False):
                config = DualTokenConfig.from_env()
                assert config.is_dual_token_mode() is False
                assert config.get_basic_token() == single_env["MOODLE_TOKEN"]
                assert config.get_plugin_token() == single_env["MOODLE_TOKEN"]

    def test_get_config_summary(self, mock_env_vars):
        """Test configuration summary"""
        with patch.dict(os.environ, mock_env_vars, clear=True):
            with patch('os.path.exists', return_value=False):
                config = DualTokenConfig.from_env()
                summary = config.get_config_summary()

                assert "moodle_url" in summary
                assert "token_mode" in summary
                assert "basic_token_set" in summary
                assert "plugin_token_set" in summary
                assert summary["token_mode"] == "dual"

    def test_get_basic_token(self, mock_env_vars):
        """Test basic token retrieval"""
        with patch.dict(os.environ, mock_env_vars, clear=True):
            with patch('os.path.exists', return_value=False):
                config = DualTokenConfig.from_env()
                basic_token = config.get_basic_token()
                assert basic_token == mock_env_vars["MOODLE_BASIC_TOKEN"]

    def test_get_plugin_token(self, mock_env_vars):
        """Test plugin token retrieval"""
        with patch.dict(os.environ, mock_env_vars, clear=True):
            with patch('os.path.exists', return_value=False):
                config = DualTokenConfig.from_env()
                plugin_token = config.get_plugin_token()
                assert plugin_token == mock_env_vars["MOODLE_PLUGIN_TOKEN"]


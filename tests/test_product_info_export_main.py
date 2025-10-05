"""
Tests for product_info_export_main module
"""
import pytest
import logging
import logging.handlers
from unittest.mock import patch, mock_open, MagicMock
import yaml

# Import functions to test
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logger_utils import (
    load_logger_config,
    _create_logger_handler,
    _create_file_handler,
    _get_logger_config_value,
    _setup_logger,
    setup_injector_logging,
    setup_sqlalchemy_logging,
    setup_file_logging,
    setup_application_logging
)


class TestLoadLoggerConfig:
    """Tests for load_logger_config function"""

    def test_load_logger_config_success(self):
        """Test successful loading of logger.yaml"""
        yaml_content = """
logger:
  injector:
    level: DEBUG
    format: "test format"
  sqlalchemy:
    format: "test format"
    engine:
      level: INFO
"""
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            config = load_logger_config()
            assert config is not None
            assert 'logger' in config
            assert 'injector' in config['logger']
            assert 'sqlalchemy' in config['logger']

    def test_load_logger_config_file_not_found(self):
        """Test behavior when logger.yaml is not found"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            config = load_logger_config()
            assert config is None

    def test_load_logger_config_yaml_error(self):
        """Test behavior when YAML parsing fails"""
        invalid_yaml = "invalid: yaml: content: ["
        with patch('builtins.open', mock_open(read_data=invalid_yaml)):
            config = load_logger_config()
            assert config is None

    def test_load_logger_config_unexpected_error(self):
        """Test behavior on unexpected errors"""
        with patch('builtins.open', side_effect=Exception("Unexpected error")):
            config = load_logger_config()
            assert config is None


class TestCreateLoggerHandler:
    """Tests for _create_logger_handler function"""

    def test_create_logger_handler_basic(self):
        """Test creating a basic logger handler"""
        handler = _create_logger_handler(logging.INFO, '%(levelname)s - %(message)s')

        assert handler is not None
        assert isinstance(handler, logging.StreamHandler)
        assert handler.level == logging.INFO
        assert handler.formatter is not None

    def test_create_logger_handler_debug_level(self):
        """Test creating a handler with DEBUG level"""
        handler = _create_logger_handler(logging.DEBUG, '%(asctime)s - %(message)s')

        assert handler.level == logging.DEBUG


class TestGetLoggerConfigValue:
    """Tests for _get_logger_config_value function"""

    def test_get_logger_config_value_exists(self):
        """Test getting an existing config value"""
        config = {
            'logger': {
                'injector': {
                    'level': 'DEBUG',
                    'format': 'test format'
                }
            }
        }

        result = _get_logger_config_value(config, 'injector', 'format', 'default')
        assert result == 'test format'

    def test_get_logger_config_value_level(self):
        """Test getting a level config value"""
        config = {
            'logger': {
                'injector': {
                    'level': 'INFO'
                }
            }
        }

        result = _get_logger_config_value(config, 'injector', 'level', logging.DEBUG)
        assert result == logging.INFO

    def test_get_logger_config_value_missing(self):
        """Test getting a missing config value returns default"""
        config = {
            'logger': {
                'injector': {}
            }
        }

        result = _get_logger_config_value(config, 'injector', 'format', 'default format')
        assert result == 'default format'

    def test_get_logger_config_value_no_config(self):
        """Test getting value when config is None"""
        result = _get_logger_config_value(None, 'injector', 'format', 'default format')
        assert result == 'default format'


class TestSetupLogger:
    """Tests for _setup_logger function"""

    def setup_method(self):
        """Clear logger handlers before each test"""
        test_logger = logging.getLogger('test.logger')
        test_logger.handlers.clear()

    def test_setup_logger_basic(self):
        """Test basic logger setup"""
        _setup_logger('test.logger', logging.INFO, '%(message)s')

        test_logger = logging.getLogger('test.logger')
        assert test_logger.level == logging.INFO
        assert len(test_logger.handlers) > 0

    def test_setup_logger_already_exists(self):
        """Test that duplicate handlers are not added"""
        _setup_logger('test.logger2', logging.INFO, '%(message)s')
        _setup_logger('test.logger2', logging.INFO, '%(message)s', "Already enabled")

        test_logger = logging.getLogger('test.logger2')
        assert len(test_logger.handlers) == 1


class TestSetupInjectorLogging:
    """Tests for setup_injector_logging function"""

    def setup_method(self):
        """Clear injector logger handlers before each test"""
        injector_logger = logging.getLogger('injector')
        injector_logger.handlers.clear()

    def test_setup_injector_logging_with_config(self):
        """Test setup with provided config"""
        config = {
            'logger': {
                'injector': {
                    'level': 'INFO',
                    'format': '%(levelname)s - %(message)s'
                }
            }
        }

        setup_injector_logging(config)

        injector_logger = logging.getLogger('injector')
        assert injector_logger.level == logging.INFO
        assert len(injector_logger.handlers) > 0

    def test_setup_injector_logging_without_config(self):
        """Test setup without config (uses defaults)"""
        with patch('utils.logger_utils.load_logger_config', return_value=None):
            setup_injector_logging()

            injector_logger = logging.getLogger('injector')
            assert injector_logger.level == logging.DEBUG
            assert len(injector_logger.handlers) > 0


class TestSetupSQLAlchemyLogging:
    """Tests for setup_sqlalchemy_logging function"""

    def setup_method(self):
        """Clear SQLAlchemy logger handlers before each test"""
        for logger_name in ['sqlalchemy.engine', 'sqlalchemy.pool',
                           'sqlalchemy.dialects', 'sqlalchemy.orm']:
            test_logger = logging.getLogger(logger_name)
            test_logger.handlers.clear()

    def test_setup_sqlalchemy_logging_with_config(self):
        """Test setup with provided config"""
        config = {
            'logger': {
                'sqlalchemy': {
                    'format': '%(levelname)s - %(message)s',
                    'engine': {'level': 'INFO'},
                    'pool': {'level': 'DEBUG'},
                    'dialects': {'level': 'DEBUG'},
                    'orm': {'level': 'DEBUG'}
                }
            }
        }

        setup_sqlalchemy_logging(config)

        # Check all SQLAlchemy loggers are set up
        engine_logger = logging.getLogger('sqlalchemy.engine')
        pool_logger = logging.getLogger('sqlalchemy.pool')
        dialects_logger = logging.getLogger('sqlalchemy.dialects')
        orm_logger = logging.getLogger('sqlalchemy.orm')

        assert engine_logger.level == logging.INFO
        assert pool_logger.level == logging.DEBUG
        assert dialects_logger.level == logging.DEBUG
        assert orm_logger.level == logging.DEBUG

        assert len(engine_logger.handlers) > 0
        assert len(pool_logger.handlers) > 0
        assert len(dialects_logger.handlers) > 0
        assert len(orm_logger.handlers) > 0

    def test_setup_sqlalchemy_logging_without_config(self):
        """Test setup without config (uses defaults)"""
        with patch('utils.logger_utils.load_logger_config', return_value=None):
            setup_sqlalchemy_logging()

            engine_logger = logging.getLogger('sqlalchemy.engine')
            assert engine_logger.level == logging.INFO
            assert len(engine_logger.handlers) > 0


class TestSetupFileLogging:
    """Tests for setup_file_logging function"""

    def setup_method(self):
        """Clear root logger file handlers before each test"""
        root_logger = logging.getLogger()
        root_logger.handlers = [h for h in root_logger.handlers
                               if not isinstance(h, logging.handlers.RotatingFileHandler)]

    def test_setup_file_logging_enabled(self):
        """Test setup with file.enable=true"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'test.log')
            config = {
                'logger': {
                    'file': {
                        'enable': True,
                        'path': log_file,
                        'max_bytes': 1024,
                        'backup_count': 3,
                        'level': 'INFO',
                        'format': '%(message)s'
                    }
                }
            }
            setup_file_logging(config)

            root_logger = logging.getLogger()
            has_file_handler = any(isinstance(h, logging.handlers.RotatingFileHandler)
                                  for h in root_logger.handlers)
            assert has_file_handler

            # Close and remove file handler before tempdir cleanup
            for handler in root_logger.handlers[:]:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    handler.close()
                    root_logger.removeHandler(handler)

    def test_setup_file_logging_disabled(self):
        """Test setup with file.enable=false"""
        config = {
            'logger': {
                'file': {
                    'enable': False,
                    'path': 'test.log'
                }
            }
        }
        setup_file_logging(config)

        root_logger = logging.getLogger()
        has_file_handler = any(isinstance(h, logging.handlers.RotatingFileHandler)
                              for h in root_logger.handlers)
        assert not has_file_handler

    def test_setup_file_logging_no_config(self):
        """Test setup without file configuration"""
        with patch('utils.logger_utils.load_logger_config', return_value=None):
            setup_file_logging()

            root_logger = logging.getLogger()
            has_file_handler = any(isinstance(h, logging.handlers.RotatingFileHandler)
                                  for h in root_logger.handlers)
            assert not has_file_handler


class TestSetupApplicationLogging:
    """Tests for setup_application_logging function"""

    def setup_method(self):
        """Clear logger handlers before each test"""
        root_logger = logging.getLogger()
        root_logger.handlers = [h for h in root_logger.handlers
                               if not isinstance(h, logging.handlers.RotatingFileHandler)]

        for logger_name in ['injector', 'sqlalchemy.engine', 'sqlalchemy.pool',
                           'sqlalchemy.dialects', 'sqlalchemy.orm']:
            test_logger = logging.getLogger(logger_name)
            test_logger.handlers.clear()

    def test_setup_application_logging_no_config(self):
        """Test setup without valid configuration"""
        with patch('utils.logger_utils.load_logger_config', return_value=None):
            setup_application_logging()

            # No loggers should be set up
            injector_logger = logging.getLogger('injector')
            assert len(injector_logger.handlers) == 0

    def test_setup_application_logging_disabled(self):
        """Test setup with enable=false in config"""
        config = {
            'logger': {
                'injector': {'enable': False},
                'sqlalchemy': {'enable': False}
            }
        }
        setup_application_logging(config)

        injector_logger = logging.getLogger('injector')
        engine_logger = logging.getLogger('sqlalchemy.engine')

        assert len(injector_logger.handlers) == 0
        assert len(engine_logger.handlers) == 0

    def test_setup_application_logging_injector_enabled(self):
        """Test setup with injector.enable=true"""
        config = {
            'logger': {
                'injector': {
                    'enable': True,
                    'level': 'DEBUG',
                    'format': '%(message)s'
                },
                'sqlalchemy': {'enable': False}
            }
        }
        setup_application_logging(config)

        injector_logger = logging.getLogger('injector')
        assert len(injector_logger.handlers) > 0

    def test_setup_application_logging_sqlalchemy_enabled(self):
        """Test setup with sqlalchemy.enable=true"""
        config = {
            'logger': {
                'injector': {'enable': False},
                'sqlalchemy': {
                    'enable': True,
                    'format': '%(message)s',
                    'engine': {'level': 'INFO'},
                    'pool': {'level': 'DEBUG'}
                }
            }
        }
        setup_application_logging(config)

        engine_logger = logging.getLogger('sqlalchemy.engine')
        assert len(engine_logger.handlers) > 0

    def test_setup_application_logging_both_enabled(self):
        """Test setup with both loggers enabled"""
        config = {
            'logger': {
                'injector': {
                    'enable': True,
                    'level': 'DEBUG',
                    'format': '%(message)s'
                },
                'sqlalchemy': {
                    'enable': True,
                    'format': '%(message)s',
                    'engine': {'level': 'INFO'},
                    'pool': {'level': 'DEBUG'}
                }
            }
        }
        setup_application_logging(config)

        injector_logger = logging.getLogger('injector')
        engine_logger = logging.getLogger('sqlalchemy.engine')

        assert len(injector_logger.handlers) > 0
        assert len(engine_logger.handlers) > 0

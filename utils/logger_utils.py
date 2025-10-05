"""
Logger utilities for setting up application logging
"""
import logging
import os
import yaml
from logging.handlers import RotatingFileHandler

# Logger configuration file path
LOGGER_CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logger.yaml')

# Default log format
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Module logger
logger = logging.getLogger(__name__)


def load_logger_config():
    """Load logger configuration from logger.yaml"""
    try:
        with open(LOGGER_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning("logger.yaml not found, using default configuration")
        return None
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse logger.yaml: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading logger.yaml: {e}")
        return None


def _create_logger_handler(level, log_format):
    """Create and configure a StreamHandler with the given level and format"""
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    return handler


def _create_file_handler(file_path, level, log_format, max_bytes, backup_count):
    """Create and configure a RotatingFileHandler with the given parameters"""
    # Ensure directory exists
    log_dir = os.path.dirname(file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    handler = RotatingFileHandler(
        file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    handler.setLevel(level)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    return handler


def _get_logger_config_value(config, logger_name, key, default):
    """Get configuration value from logger config with fallback to default"""
    if config and 'logger' in config and logger_name in config['logger']:
        logger_config = config['logger'][logger_name]
        if key == 'level':
            level_str = logger_config.get(key, default if isinstance(default, str) else 'DEBUG')
            return getattr(logging, level_str) if isinstance(level_str, str) else default
        return logger_config.get(key, default)
    return default


def _setup_logger(logger_name, level, log_format, already_enabled_msg=None):
    """Setup a logger with the given name, level, and format"""
    target_logger = logging.getLogger(logger_name)

    # Avoid duplicate handlers
    if target_logger.handlers:
        if already_enabled_msg:
            logger.info(already_enabled_msg)
        return

    target_logger.setLevel(level)
    target_logger.addHandler(_create_logger_handler(level, log_format))


def setup_injector_logging(config=None):
    """
    Enable debug logging for injector to trace dependency injection

    This will output detailed information about:
    - Dependency resolution process
    - Provider usage
    - Object creation
    - Singleton behavior
    """
    # Load configuration
    if config is None:
        config = load_logger_config()

    log_level = _get_logger_config_value(config, 'injector', 'level', logging.DEBUG)
    log_format = _get_logger_config_value(config, 'injector', 'format', DEFAULT_LOG_FORMAT)

    _setup_logger('injector', log_level, log_format, "Injector debug logging already enabled")
    logger.info("Injector debug logging enabled")


def setup_sqlalchemy_logging(config=None):
    """
    Enable debug logging for SQLAlchemy to trace SQL execution

    This will output detailed information about:
    - SQL statements execution
    - Connection pool management
    - SQL dialect details
    - ORM internal operations
    """
    # Load configuration
    if config is None:
        config = load_logger_config()

    # Get common format
    log_format = _get_logger_config_value(config, 'sqlalchemy', 'format', DEFAULT_LOG_FORMAT)

    # Get log levels for each component
    if config and 'logger' in config and 'sqlalchemy' in config['logger']:
        sqlalchemy_config = config['logger']['sqlalchemy']
        engine_level = getattr(logging, sqlalchemy_config.get('engine', {}).get('level', 'INFO'))
        pool_level = getattr(logging, sqlalchemy_config.get('pool', {}).get('level', 'DEBUG'))
        dialects_level = getattr(logging, sqlalchemy_config.get('dialects', {}).get('level', 'DEBUG'))
        orm_level = getattr(logging, sqlalchemy_config.get('orm', {}).get('level', 'DEBUG'))
    else:
        engine_level = logging.INFO
        pool_level = logging.DEBUG
        dialects_level = logging.DEBUG
        orm_level = logging.DEBUG

    # Setup SQLAlchemy loggers
    _setup_logger('sqlalchemy.engine', engine_level, log_format)
    _setup_logger('sqlalchemy.pool', pool_level, log_format)
    _setup_logger('sqlalchemy.dialects', dialects_level, log_format)
    _setup_logger('sqlalchemy.orm', orm_level, log_format)

    logger.info("SQLAlchemy debug logging enabled")


def setup_file_logging(config=None):
    """
    Enable file logging with rotation support

    This will output logs to a file with automatic rotation when size limit is reached.
    """
    # Load configuration
    if config is None:
        config = load_logger_config()

    # Check if file logging is enabled
    if not config or 'logger' not in config or 'file' not in config['logger']:
        return

    file_config = config['logger']['file']
    if not file_config.get('enable', False):
        return

    # Get file logging parameters
    file_path = file_config.get('path', 'logs/application.log')
    max_bytes = file_config.get('max_bytes', 10485760)  # Default 10MB
    backup_count = file_config.get('backup_count', 5)
    log_level = getattr(logging, file_config.get('level', 'INFO'))
    log_format = file_config.get('format', DEFAULT_LOG_FORMAT)

    # Get root logger
    root_logger = logging.getLogger()

    # Check if file handler already exists
    has_file_handler = any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers)
    if has_file_handler:
        logger.info("File logging already enabled")
        return

    # Add file handler to root logger
    try:
        file_handler = _create_file_handler(file_path, log_level, log_format, max_bytes, backup_count)
        root_logger.addHandler(file_handler)
        logger.info(f"File logging enabled: {file_path} (max: {max_bytes} bytes, backups: {backup_count})")
    except Exception as e:
        logger.error(f"Failed to setup file logging: {e}")


def setup_application_logging(logger_config=None):
    """
    Setup application logging based on logger.yaml configuration

    Args:
        logger_config: Pre-loaded logger configuration (optional)
    """
    # Load logger configuration if not provided
    if logger_config is None:
        logger_config = load_logger_config()

    # Check if logger_config is valid
    if not logger_config or 'logger' not in logger_config:
        logger.debug("No valid logger configuration found, skipping logging setup")
        return

    # Enable file logging if configured
    if logger_config['logger'].get('file', {}).get('enable', False):
        setup_file_logging(logger_config)

    # Enable injector logging if configured
    if logger_config['logger'].get('injector', {}).get('enable', False):
        setup_injector_logging(logger_config)

    # Enable SQLAlchemy logging if configured
    if logger_config['logger'].get('sqlalchemy', {}).get('enable', False):
        setup_sqlalchemy_logging(logger_config)

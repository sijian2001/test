"""
Logger utilities for setting up application logging
"""
import logging
import os
import yaml

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


def setup_application_logging(logger_config=None):
    """
    Setup application logging based on environment variables

    Args:
        logger_config: Pre-loaded logger configuration (optional)
    """
    # Load logger configuration if not provided
    if logger_config is None:
        logger_config = load_logger_config()

    # Enable injector logging if DEBUG_INJECTOR environment variable is set
    if os.getenv('DEBUG_INJECTOR', 'false').lower() == 'true':
        setup_injector_logging(logger_config)

    # Enable SQLAlchemy logging if DEBUG_SQL environment variable is set
    if os.getenv('DEBUG_SQL', 'false').lower() == 'true':
        setup_sqlalchemy_logging(logger_config)

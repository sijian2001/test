#!/usr/bin/env python3

import sys
import logging
import os
import yaml
from injector import Injector
from batch.product_info_csv_export_processor import ProductInfoCsvExportProcessorImpl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_logger_config():
    """Load logger configuration from logger.yaml"""
    try:
        with open('logger.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning("logger.yaml not found, using default configuration")
        return None
    except Exception as e:
        logger.error(f"Failed to load logger.yaml: {e}")
        return None


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

    if config and 'logger' in config and 'injector' in config['logger']:
        injector_config = config['logger']['injector']
        log_level = getattr(logging, injector_config.get('level', 'DEBUG'))
        log_format = injector_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    else:
        log_level = logging.DEBUG
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    injector_logger = logging.getLogger('injector')

    # Avoid duplicate handlers
    if injector_logger.handlers:
        logger.info("Injector debug logging already enabled")
        return

    injector_logger.setLevel(log_level)

    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    injector_logger.addHandler(handler)

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

    # Setup SQLAlchemy engine logger (SQL statements)
    engine_logger = logging.getLogger('sqlalchemy.engine')
    if not engine_logger.handlers:
        engine_logger.setLevel(engine_level)
        handler = logging.StreamHandler()
        handler.setLevel(engine_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        engine_logger.addHandler(handler)

    # Setup SQLAlchemy pool logger (connection pool)
    pool_logger = logging.getLogger('sqlalchemy.pool')
    if not pool_logger.handlers:
        pool_logger.setLevel(pool_level)
        handler = logging.StreamHandler()
        handler.setLevel(pool_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        pool_logger.addHandler(handler)

    logger.info("SQLAlchemy debug logging enabled")


def main():
    """Main function for Product Info CSV Export"""
    try:
        logger.info("Starting Product Info CSV Export Application...")

        # Load logger configuration once
        logger_config = load_logger_config()

        # Enable injector logging if DEBUG_INJECTOR environment variable is set
        if os.getenv('DEBUG_INJECTOR', 'false').lower() == 'true':
            setup_injector_logging(logger_config)

        # Enable SQLAlchemy logging if DEBUG_SQL environment variable is set
        if os.getenv('DEBUG_SQL', 'false').lower() == 'true':
            setup_sqlalchemy_logging(logger_config)

        # Create injector and get processor
        injector = Injector()
        processor = injector.get(ProductInfoCsvExportProcessorImpl)

        # Execute CSV export process
        result = processor.run_csv_export_process()

        if result:
            logger.info("Product Info CSV Export Application completed successfully!")
            return 0
        else:
            logger.error("Product Info CSV Export Application failed!")
            return 1

    except Exception as e:
        logger.error(f"Unexpected error in Product Info CSV Export Application: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
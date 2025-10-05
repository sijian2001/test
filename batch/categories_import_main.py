#!/usr/bin/env python3

import sys
import os
import logging

# Add project root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from injector import Injector
from batch.categories_csv_import_processor import CategoriesCsvImportProcessorImpl
from utils.logger_utils import setup_application_logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function for Categories CSV Import"""
    try:
        logger.info("Starting Categories CSV Import Application...")

        # Setup application logging (Injector and SQLAlchemy)
        setup_application_logging()

        # Create injector and get processor
        injector = Injector()
        processor = injector.get(CategoriesCsvImportProcessorImpl)

        # Execute CSV import process
        result = processor.run_csv_import_process()

        if result:
            logger.info("Categories CSV Import Application completed successfully!")
            return 0
        else:
            logger.error("Categories CSV Import Application failed!")
            return 1

    except Exception as e:
        logger.error(f"Unexpected error in Categories CSV Import Application: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
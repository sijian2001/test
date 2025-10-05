#!/usr/bin/env python3

import sys
import os
import logging

# Add project root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from injector import Injector
from batch.csv_export_processor import UserInfoCsvExportProcessor
from utils.logger_utils import setup_application_logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting CSV Export Application...")

    # Setup application logging (Injector and SQLAlchemy)
    setup_application_logging()

    injector = Injector()

    csv_export_processor = injector.get(UserInfoCsvExportProcessor)

    success = csv_export_processor.run_csv_export_process()

    if success:
        logger.info("\nCSV Export completed successfully!")
        return 0
    else:
        logger.error("\nCSV Export failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
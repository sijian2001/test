#!/usr/bin/env python3

import sys
import logging
from di_container import create_injector
from batch.csv_export_processor import CsvExportProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting CSV Export Application...")

    injector = create_injector()

    csv_export_processor = injector.get(CsvExportProcessor)

    success = csv_export_processor.run_csv_export_process()

    if success:
        logger.info("\nCSV Export completed successfully!")
        return 0
    else:
        logger.error("\nCSV Export failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
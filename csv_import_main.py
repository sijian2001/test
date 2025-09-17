#!/usr/bin/env python3

import sys
import logging
from di_container import create_injector
from batch.csv_import_processor import CsvImportProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting CSV Import Application...")
    
    injector = create_injector()
    
    csv_import_processor = injector.get(CsvImportProcessor)
    
    success = csv_import_processor.run_csv_import_process()
    
    if success:
        logger.info("\nCSV import completed successfully!")
        return 0
    else:
        logger.error("\nCSV import failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
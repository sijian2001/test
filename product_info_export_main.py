#!/usr/bin/env python3

import sys
import logging
from injector import Injector
from batch.product_info_csv_export_processor import ProductInfoCsvExportProcessorImpl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function for Product Info CSV Export"""
    try:
        logger.info("Starting Product Info CSV Export Application...")

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
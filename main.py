#!/usr/bin/env python3

import sys
import logging
from injector import Injector
from batch.data_batch_processor import DataBatchProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Batch Processing Application...")
    
    injector = Injector()

    batch_processor = injector.get(DataBatchProcessor)
    
    success = batch_processor.run_batch_process()
    
    if success:
        logger.info("\nBatch processing completed successfully!")
        return 0
    else:
        logger.error("\nBatch processing failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
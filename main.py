#!/usr/bin/env python3

import sys
import logging
from di_container import create_injector
from batch.processor import BatchProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Batch Processing Application...")
    
    injector = create_injector()

    batch_processor = injector.get(BatchProcessor)
    
    success = batch_processor.run_batch_process()
    
    if success:
        logger.info("\nBatch processing completed successfully!")
        return 0
    else:
        logger.error("\nBatch processing failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
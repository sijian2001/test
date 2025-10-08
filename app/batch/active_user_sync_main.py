#!/usr/bin/env python3

import sys
import os
import logging

# Add project root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from injector import Injector
from app.business.active_user_regist_service import ActiveUserRegistService, ActiveUserRegistInDto
from app.utils.logger_utils import setup_application_logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Active User Sync Main Application

    Syncs active users from test1.user (is_active=True) to test2.active_user
    """
    logger.info("=" * 60)
    logger.info("Active User Sync Application Started")
    logger.info("=" * 60)
    logger.info("Purpose: Sync active users from test1.user to test2.active_user")
    logger.info("")

    try:
        # Setup application logging (Injector and SQLAlchemy)
        setup_application_logging()

        # Initialize dependency injection container
        injector = Injector()

        # Get ActiveUserRegistService instance
        active_user_service = injector.get(ActiveUserRegistService)

        # Create input DTO (no parameters needed - auto-fetches from test1.user)
        in_dto = ActiveUserRegistInDto()

        # Execute sync process
        logger.info("Executing active user sync process...")
        result = active_user_service.execute(in_dto)

        # Display results
        logger.info("")
        logger.info("=" * 60)
        logger.info("Sync Results:")
        logger.info("=" * 60)
        logger.info(f"Source users (test1.user is_active=True): {result.sourceUserCount}")
        logger.info(f"Registered to test2.active_user: {result.activeUserCount}")
        logger.info("=" * 60)
        logger.info("Active user sync completed successfully!")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error("")
        logger.error("=" * 60)
        logger.error("Active user sync failed!")
        logger.error("=" * 60)
        logger.error(f"Error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())

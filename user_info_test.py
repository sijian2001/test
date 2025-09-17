#!/usr/bin/env python3

import sys
import logging
from injector import Injector
from business.user_info_service import UserInfoService, UserInfoSearchInDto

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_user_info_service():
    """Test UserInfoService functionality"""
    logger.info("Starting UserInfo Service Test...")

    injector = Injector()
    user_info_service = injector.get(UserInfoService)

    # Test 1: Get all user info
    logger.info("\n=== Test 1: Get All User Info ===")
    result = user_info_service.get_all_user_info()
    logger.info(f"Found {result.total_count} user info records")

    for user_info in result.user_info_list:
        logger.info(f"User: {user_info.username} - {user_info.email} - Department: {user_info.department_name}")

    # Test 2: Search by username
    logger.info("\n=== Test 2: Search by Username ===")
    search_dto = UserInfoSearchInDto(username="john.doe")
    result = user_info_service.search_user_info(search_dto)
    logger.info(f"Found {result.total_count} user info records for username 'john.doe'")

    for user_info in result.user_info_list:
        logger.info(f"User: {user_info.username} - {user_info.email} - Department: {user_info.department_name}")

    # Test 3: Search by department
    logger.info("\n=== Test 3: Search by Department ===")
    search_dto = UserInfoSearchInDto(department_name="Engineering")
    result = user_info_service.search_user_info(search_dto)
    logger.info(f"Found {result.total_count} user info records for department 'Engineering'")

    for user_info in result.user_info_list:
        logger.info(f"User: {user_info.username} - {user_info.email} - Department: {user_info.department_name}")

    # Test 4: Search by user_id
    logger.info("\n=== Test 4: Search by User ID ===")
    search_dto = UserInfoSearchInDto(user_id=1)
    result = user_info_service.search_user_info(search_dto)
    logger.info(f"Found {result.total_count} user info records for user_id 1")

    for user_info in result.user_info_list:
        logger.info(f"User: {user_info.username} - {user_info.email} - Department: {user_info.department_name}")

def main():
    try:
        test_user_info_service()
        logger.info("\nUserInfo Service Test completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"\nUserInfo Service Test failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
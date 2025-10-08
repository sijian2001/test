"""
Active User Service Test Script
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from injector import Injector
from app.business.active_user_regist_service import ActiveUserRegistService, ActiveUserRegistInDto
from app.business.active_user_info_service import ActiveUserInfoService, ActiveUserInfoSearchInDto
from app.business.vo.active_user_vo import ActiveUserVo
from app.domain.database import DatabaseConfig, Test2DatabaseEngine, Test2DatabaseSession
from app.domain.repository.test2.active_user_repository import ActiveUserRepository

def main():
    # Setup injector
    injector = Injector()

    # Test 1: Register Active Users
    print("=" * 60)
    print("Test 1: Active User Registration")
    print("=" * 60)

    regist_service = injector.get(ActiveUserRegistService)

    active_user_list = [
        ActiveUserVo(
            username="test_user1",
            email="test1@example.com",
            first_name="Test",
            last_name="User1",
            department_id=1
        ),
        ActiveUserVo(
            username="test_user2",
            email="test2@example.com",
            first_name="Test",
            last_name="User2",
            department_id=2
        )
    ]

    regist_in_dto = ActiveUserRegistInDto(activeUserList=active_user_list)
    regist_result = regist_service.execute(regist_in_dto)

    print(f"\nRegistered {regist_result.activeUserCount} active users")

    # Test 2: Search Active Users
    print("\n" + "=" * 60)
    print("Test 2: Active User Search")
    print("=" * 60)

    info_service = injector.get(ActiveUserInfoService)

    # Get all active users
    search_in_dto = ActiveUserInfoSearchInDto()
    search_result = info_service.execute(search_in_dto)

    print(f"\nTotal active users: {search_result.total_count}")
    for user in search_result.active_user_list:
        print(f"  - ID: {user.id}, Username: {user.username}, Email: {user.email}")

    # Search by username
    print("\n" + "-" * 60)
    print("Search by username: test_user1")
    print("-" * 60)

    username_search_dto = ActiveUserInfoSearchInDto(username="test_user1")
    username_result = info_service.execute(username_search_dto)

    if username_result.total_count > 0:
        user = username_result.active_user_list[0]
        print(f"Found: ID={user.id}, Username={user.username}, Email={user.email}")
    else:
        print("Not found")

    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()

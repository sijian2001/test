"""
Active User Sync Test Script
Test syncing active users from test1.user to test2.active_user
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from injector import Injector
from app.business.active_user_regist_service import ActiveUserRegistService, ActiveUserRegistInDto
from app.business.active_user_info_service import ActiveUserInfoService, ActiveUserInfoSearchInDto
from app.domain.database import DatabaseConfig, Test1DatabaseEngine, Test1DatabaseSession, Test2DatabaseEngine, Test2DatabaseSession
from app.domain.repository.test1.user_repository import UserRepository

def main():
    # Setup injector
    injector = Injector()

    # Check test1.user active users
    print("=" * 60)
    print("Step 1: Check active users in test1.user")
    print("=" * 60)

    user_repository = injector.get(UserRepository)
    active_users_in_test1 = user_repository.get_active_users()

    print(f"\nFound {len(active_users_in_test1)} active users in test1.user:")
    for user in active_users_in_test1:
        print(f"  - ID: {user.id}, Username: {user.username}, Email: {user.email}, Department: {user.department_id}")

    # Sync to test2.active_user
    print("\n" + "=" * 60)
    print("Step 2: Sync active users to test2.active_user")
    print("=" * 60)

    regist_service = injector.get(ActiveUserRegistService)
    regist_in_dto = ActiveUserRegistInDto()
    regist_result = regist_service.execute(regist_in_dto)

    print(f"\nSync Results:")
    print(f"  - Source users (test1.user is_active=True): {regist_result.sourceUserCount}")
    print(f"  - Registered to test2.active_user: {regist_result.activeUserCount}")

    # Check test2.active_user
    print("\n" + "=" * 60)
    print("Step 3: Verify data in test2.active_user")
    print("=" * 60)

    info_service = injector.get(ActiveUserInfoService)
    search_in_dto = ActiveUserInfoSearchInDto()
    search_result = info_service.execute(search_in_dto)

    print(f"\nTotal active users in test2.active_user: {search_result.total_count}")
    for user in search_result.active_user_list:
        print(f"  - ID: {user.id}, Username: {user.username}, Email: {user.email}, Department: {user.department_id}")

    print("\n" + "=" * 60)
    print("Sync test completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()

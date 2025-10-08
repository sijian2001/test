from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from injector import inject
import logging
from app.business.abstract_service import AbstractService, AbstractInDto, AbstractOutDto
from app.business.decorators.transactional import Transactional
from app.business.decorators.database_enum import Database
from app.domain.repository.test1.user_repository import UserRepository
from app.domain.repository.test2.active_user_repository import ActiveUserRepository

logging.basicConfig(level=logging.INFO)

@dataclass
class ActiveUserRegistInDto(AbstractInDto):
    """
    Input DTO for Active User Registration
    No parameters needed - automatically fetches active users from test1.user
    """
    pass

@dataclass
class ActiveUserRegistOutDto(AbstractOutDto):
    activeUserCount: int
    sourceUserCount: int  # test1から取得したユーザー数

class AbstractActiveUserRegistService(AbstractService):
    @abstractmethod
    def execute(self, in_dto: ActiveUserRegistInDto) -> ActiveUserRegistOutDto:
        pass

@inject
@dataclass
class ActiveUserRegistService(AbstractActiveUserRegistService):
    user_repository: UserRepository  # test1のUserRepository
    active_user_repository: ActiveUserRepository  # test2のActiveUserRepository

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    @Transactional(database=Database.TEST2)
    def execute(self, in_dto: ActiveUserRegistInDto) -> ActiveUserRegistOutDto:
        self.logger.info("=== Starting Active User Registration from test1.user ===")

        # Step 1: test2のactive_userテーブルの全データを削除
        self.logger.info("Deleting all existing data from test2.active_user...")
        deleted_count = self.active_user_repository.delete_all_active_users()
        self.logger.info(f"Deleted {deleted_count} existing records from test2.active_user")

        # Step 2: test1のuserテーブルからis_active=Trueのユーザーを取得
        self.logger.info("Fetching active users from test1.user...")
        active_users_from_test1 = self.user_repository.get_active_users()
        source_count = len(active_users_from_test1)
        self.logger.info(f"Found {source_count} active users in test1.user")

        # Step 3: test2のactive_userテーブルに登録
        active_users_registered = 0
        for user in active_users_from_test1:
            try:
                # test1.userからtest2.active_userへデータをコピー
                self.active_user_repository.create_active_user(
                    username=user.username,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    department_id=user.department_id
                )
                active_users_registered += 1
                self.logger.info(f"Registered active user: {user.username}")
            except Exception as e:
                self.logger.error(f"Failed to register active user {user.username}: {str(e)}")
                raise

        self.logger.info(f"Successfully registered {active_users_registered} active users from test1 to test2")
        self.logger.info("=== Active User Registration Completed Successfully ===")

        # Create and return result DTO
        result_dto = ActiveUserRegistOutDto(
            activeUserCount=active_users_registered,
            sourceUserCount=source_count
        )

        return result_dto

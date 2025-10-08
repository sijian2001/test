"""
Improved version with TEST1 transaction management
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from injector import inject
import logging
from app.business.abstract_service import AbstractService, AbstractInDto, AbstractOutDto
from app.business.decorators.transactional import Transactional
from app.business.decorators.database_enum import Database
from app.domain.repository.test1.user_repository import UserRepository
from app.domain.repository.test2.active_user_repository import ActiveUserRepository
from app.domain.model.test1.user import User

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
    sourceUserCount: int

class AbstractActiveUserRegistService(AbstractService):
    @abstractmethod
    def execute(self, in_dto: ActiveUserRegistInDto) -> ActiveUserRegistOutDto:
        pass

@inject
@dataclass
class ActiveUserRegistServiceImproved(AbstractActiveUserRegistService):
    user_repository: UserRepository
    active_user_repository: ActiveUserRepository

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    @Transactional(database=Database.TEST1, read_only=True)
    def fetch_active_users_from_test1(self) -> List[User]:
        """
        Fetch active users from TEST1 with explicit transaction management

        Returns:
            List of active users from test1.user

        Note:
            - Uses read-only transaction for TEST1
            - Ensures consistent snapshot read
            - Prevents data changes during read operation
        """
        self.logger.info("Fetching active users from test1.user...")
        active_users = self.user_repository.get_active_users()
        self.logger.info(f"Found {len(active_users)} active users in test1.user")
        return active_users

    @Transactional(database=Database.TEST2)
    def execute(self, in_dto: ActiveUserRegistInDto) -> ActiveUserRegistOutDto:
        self.logger.info("=== Starting Active User Registration from test1.user ===")

        # Step 1: Fetch active users from TEST1 (with read-only transaction)
        active_users_from_test1 = self.fetch_active_users_from_test1()
        source_count = len(active_users_from_test1)

        # Step 2: Delete all existing data from test2.active_user
        self.logger.info("Deleting all existing data from test2.active_user...")
        deleted_count = self.active_user_repository.delete_all_active_users()
        self.logger.info(f"Deleted {deleted_count} existing records from test2.active_user")

        # Step 3: Register users to test2.active_user
        active_users_registered = 0
        for user in active_users_from_test1:
            try:
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

        result_dto = ActiveUserRegistOutDto(
            activeUserCount=active_users_registered,
            sourceUserCount=source_count
        )

        return result_dto

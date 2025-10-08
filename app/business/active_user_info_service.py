from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from injector import inject
import logging
from app.business.abstract_service import AbstractService, AbstractInDto, AbstractOutDto
from app.domain.repository.test2.active_user_repository import ActiveUserRepository
from app.domain.model.test2.active_user import ActiveUser

logging.basicConfig(level=logging.INFO)

@dataclass
class ActiveUserInfoSearchInDto(AbstractInDto):
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    search_term: Optional[str] = None

@dataclass
class ActiveUserInfoOutDto(AbstractOutDto):
    active_user_list: List[ActiveUser]
    total_count: int

class AbstractActiveUserInfoService(AbstractService):
    @abstractmethod
    def get_all_active_users(self) -> ActiveUserInfoOutDto:
        pass

    @abstractmethod
    def search_active_users(self, in_dto: ActiveUserInfoSearchInDto) -> ActiveUserInfoOutDto:
        pass

    @abstractmethod
    def execute(self, in_dto: ActiveUserInfoSearchInDto) -> ActiveUserInfoOutDto:
        pass

@inject
@dataclass
class ActiveUserInfoService(AbstractActiveUserInfoService):
    active_user_repository: ActiveUserRepository

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    def get_all_active_users(self) -> ActiveUserInfoOutDto:
        self.logger.info("=== Getting All Active Users ===")

        active_user_list = self.active_user_repository.get_all_active_users()

        result_dto = ActiveUserInfoOutDto(
            active_user_list=active_user_list,
            total_count=len(active_user_list)
        )

        self.logger.info(f"Retrieved {result_dto.total_count} active users")
        self.logger.info("=== Get All Active Users Completed Successfully ===")

        return result_dto

    def search_active_users(self, in_dto: ActiveUserInfoSearchInDto) -> ActiveUserInfoOutDto:
        self.logger.info("=== Starting Active User Search ===")

        active_user_list = []

        # Priority-based search logic
        if in_dto.user_id:
            self.logger.info(f"Searching by user_id: {in_dto.user_id}")
            active_user = self.active_user_repository.get_active_user_by_id(in_dto.user_id)
            if active_user:
                active_user_list = [active_user]
        elif in_dto.username:
            self.logger.info(f"Searching by username: {in_dto.username}")
            active_user = self.active_user_repository.get_active_user_by_username(in_dto.username)
            if active_user:
                active_user_list = [active_user]
        elif in_dto.email:
            self.logger.info(f"Searching by email: {in_dto.email}")
            active_user = self.active_user_repository.get_active_user_by_email(in_dto.email)
            if active_user:
                active_user_list = [active_user]
        elif in_dto.department_id:
            self.logger.info(f"Searching by department_id: {in_dto.department_id}")
            active_user_list = self.active_user_repository.get_active_users_by_department(in_dto.department_id)
        elif in_dto.search_term:
            self.logger.info(f"Searching by search term: {in_dto.search_term}")
            active_user_list = self.active_user_repository.search_active_users_by_name(in_dto.search_term)
        else:
            self.logger.info("No specific search criteria provided, getting all active users")
            active_user_list = self.active_user_repository.get_all_active_users()

        result_dto = ActiveUserInfoOutDto(
            active_user_list=active_user_list,
            total_count=len(active_user_list)
        )

        self.logger.info(f"Search completed - Found {result_dto.total_count} active users")
        self.logger.info("=== Active User Search Completed Successfully ===")

        return result_dto

    def execute(self, in_dto: ActiveUserInfoSearchInDto) -> ActiveUserInfoOutDto:
        return self.search_active_users(in_dto)

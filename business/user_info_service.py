from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from injector import inject
import logging
from .abstract_service import AbstractService, AbstractInDto, AbstractOutDto
from domain.repository.user_info_repository import AbstractUserInfoRepository
from domain.model.user_info import UserInfo

logging.basicConfig(level=logging.INFO)

@dataclass
class UserInfoSearchInDto(AbstractInDto):
    user_id: Optional[int] = None
    username: Optional[str] = None
    department_name: Optional[str] = None

@dataclass
class UserInfoOutDto(AbstractOutDto):
    user_info_list: List[UserInfo]
    total_count: int

class AbstractUserInfoService(AbstractService):
    @abstractmethod
    def get_all_user_info(self) -> UserInfoOutDto:
        pass

    @abstractmethod
    def search_user_info(self, in_dto: UserInfoSearchInDto) -> UserInfoOutDto:
        pass

    @abstractmethod
    def execute(self, in_dto: UserInfoSearchInDto) -> UserInfoOutDto:
        pass

@inject
@dataclass
class UserInfoService(AbstractUserInfoService):
    user_info_repository: AbstractUserInfoRepository

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    def get_all_user_info(self) -> UserInfoOutDto:
        self.logger.info("=== Getting All User Info ===")

        user_info_list = self.user_info_repository.get_all_user_info()

        result_dto = UserInfoOutDto(
            user_info_list=user_info_list,
            total_count=len(user_info_list)
        )

        self.logger.info(f"Retrieved {result_dto.total_count} user info records")
        self.logger.info("=== Get All User Info Completed Successfully ===")

        return result_dto

    def search_user_info(self, in_dto: UserInfoSearchInDto) -> UserInfoOutDto:
        self.logger.info("=== Starting User Info Search ===")

        user_info_list = []

        if in_dto.user_id:
            self.logger.info(f"Searching by user_id: {in_dto.user_id}")
            user_info = self.user_info_repository.get_user_info_by_id(in_dto.user_id)
            if user_info:
                user_info_list = [user_info]
        elif in_dto.username:
            self.logger.info(f"Searching by username: {in_dto.username}")
            user_info = self.user_info_repository.get_user_info_by_username(in_dto.username)
            if user_info:
                user_info_list = [user_info]
        elif in_dto.department_name:
            self.logger.info(f"Searching by department: {in_dto.department_name}")
            user_info_list = self.user_info_repository.get_user_info_by_department(in_dto.department_name)
        else:
            self.logger.info("No search criteria provided, getting all user info")
            user_info_list = self.user_info_repository.get_all_user_info()

        result_dto = UserInfoOutDto(
            user_info_list=user_info_list,
            total_count=len(user_info_list)
        )

        self.logger.info(f"Search completed - Found {result_dto.total_count} user info records")
        self.logger.info("=== User Info Search Completed Successfully ===")

        return result_dto

    def execute(self, in_dto: UserInfoSearchInDto) -> UserInfoOutDto:
        return self.search_user_info(in_dto)
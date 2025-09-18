from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from injector import inject
import logging
from business.abstract_service import AbstractService, AbstractInDto, AbstractOutDto
from domain.repository.test1.user_repository import UserRepository
from domain.vo.user_vo import UserVo

logging.basicConfig(level=logging.INFO)

@dataclass
class UserRegistInDto(AbstractInDto):
    userList: List[UserVo]

@dataclass
class UserRegistOutDto(AbstractOutDto):
    userCount: int

class AbstractUserRegistService(AbstractService):
    @abstractmethod
    def execute(self, in_dto: UserRegistInDto) -> UserRegistOutDto:
        pass

@inject
@dataclass
class UserRegistService(AbstractUserRegistService):
    user_repository: UserRepository

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)
    
    def execute(self, in_dto: UserRegistInDto) -> UserRegistOutDto:
        self.logger.info("=== Starting User Registration ===")
        
        users_registered = 0
        for user_vo in in_dto.userList:
            try:
                self.user_repository.create_user(
                    username=user_vo.username,
                    email=user_vo.email,
                    password_hash=user_vo.password_hash,
                    first_name=user_vo.first_name,
                    last_name=user_vo.last_name,
                    department_id=user_vo.department_id
                )
                users_registered += 1
                self.logger.info(f"Registered user: {user_vo.username}")
            except Exception as e:
                self.logger.error(f"Failed to register user {user_vo.username}: {str(e)}")
                raise
        
        self.logger.info(f"Successfully registered {users_registered} users")
        self.logger.info("=== User Registration Completed Successfully ===")
        
        # Create and return result DTO
        result_dto = UserRegistOutDto(
            userCount=users_registered
        )
        
        return result_dto
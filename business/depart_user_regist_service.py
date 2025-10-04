from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from injector import inject
import logging
from business.abstract_service import AbstractService, AbstractInDto, AbstractOutDto
from business.department_regist_service import DepartmentRegistService, DepartmentRegistInDto
from business.user_regist_service import UserRegistService, UserRegistInDto
from business.decorators.session_manager import SessionManager
from business.decorators.database_enum import Database
from domain.database import DatabaseSession
from business.vo.department_vo import DepartmentVo
from business.vo.user_vo import UserVo

logging.basicConfig(level=logging.INFO)

@dataclass
class DepartUserRegistInDto(AbstractInDto):
    departmentList: List[DepartmentVo]
    userList: List[UserVo]

@dataclass
class DepartUserRegistOutDto(AbstractOutDto):
    departmentCount: int
    userCount: int

class AbstractDepartUserRegistService(AbstractService):
    @abstractmethod
    def execute(self, in_dto: DepartUserRegistInDto) -> DepartUserRegistOutDto:
        pass
    
    @abstractmethod
    def regist_depart_user(self, input_dto: DepartUserRegistInDto) -> DepartUserRegistOutDto:
        pass

@inject
@dataclass
class DepartUserRegistService(AbstractDepartUserRegistService):
    department_regist_service: DepartmentRegistService
    user_regist_service: UserRegistService
    db_session: DatabaseSession

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)
    
    def execute(self, in_dto: DepartUserRegistInDto) -> DepartUserRegistOutDto:
        return self.regist_depart_user(in_dto)
    
    @SessionManager(database=Database.TEST1)
    def regist_depart_user(self, input_dto: DepartUserRegistInDto) -> DepartUserRegistOutDto:
        self.logger.info("=== Starting Department and User Registration ===")
        
        # 1. Department registration
        self.logger.info("1. Registering departments...")
        department_input_dto = DepartmentRegistInDto(
            departmentList=input_dto.departmentList
        )
        department_result = self.department_regist_service.execute(department_input_dto)
        self.logger.info(f"Successfully registered {department_result.departmentCount} departments")
        
        # 2. User registration
        self.logger.info("2. Registering users...")
        user_input_dto = UserRegistInDto(
            userList=input_dto.userList
        )
        user_result = self.user_regist_service.execute(user_input_dto)
        self.logger.info(f"Successfully registered {user_result.userCount} users")
        
        self.logger.info("=== Department and User Registration Completed Successfully ===")
        
        # Create and return result DTO
        result_dto = DepartUserRegistOutDto(
            departmentCount=department_result.departmentCount,
            userCount=user_result.userCount
        )
        
        return result_dto
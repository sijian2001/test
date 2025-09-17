from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from injector import inject
import logging
from business.abstract_service import AbstractService, AbstractInDto, AbstractOutDto
from domain.repository.department_repository import DepartmentRepository
from domain.vo.department_vo import DepartmentVo

logging.basicConfig(level=logging.INFO)

@dataclass
class DepartmentRegistInDto(AbstractInDto):
    departmentList: List[DepartmentVo]

@dataclass
class DepartmentRegistOutDto(AbstractOutDto):
    departmentCount: int

class AbstractDepartmentRegistService(AbstractService):
    @abstractmethod
    def execute(self, in_dto: DepartmentRegistInDto) -> DepartmentRegistOutDto:
        pass

@inject
@dataclass
class DepartmentRegistService(AbstractDepartmentRegistService):
    department_repository: DepartmentRepository

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)
    
    def execute(self, in_dto: DepartmentRegistInDto) -> DepartmentRegistOutDto:
        self.logger.info("=== Starting Department Registration ===")
        
        departments_registered = 0
        for department_vo in in_dto.departmentList:
            try:
                self.department_repository.create_department(
                    name=department_vo.name,
                    description=department_vo.description,
                    manager_id=department_vo.manager_id
                )
                departments_registered += 1
                self.logger.info(f"Registered department: {department_vo.name}")
            except Exception as e:
                self.logger.error(f"Failed to register department {department_vo.name}: {str(e)}")
                raise
        
        self.logger.info(f"Successfully registered {departments_registered} departments")
        self.logger.info("=== Department Registration Completed Successfully ===")
        
        # Create and return result DTO
        result_dto = DepartmentRegistOutDto(
            departmentCount=departments_registered
        )
        
        return result_dto
    

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from injector import inject
from sqlalchemy.orm import Session

from domain.database import Test1DatabaseSession
from domain.model.test1.department import Department


class AbstractDepartmentRepository(ABC):
    @abstractmethod
    def get_all_departments(self) -> List[Department]:
        pass

    @abstractmethod
    def get_department_by_id(self, department_id: int) -> Optional[Department]:
        pass

    @abstractmethod
    def create_department(self, name: str, description: str = None, manager_id: int = None) -> Department:
        pass

    @abstractmethod
    def update_department(self, department_id: int, name: str = None, description: str = None, manager_id: int = None) \
            -> Optional[Department]:
        pass

    @abstractmethod
    def delete_department(self, department_id: int) -> bool:
        pass


@inject
@dataclass
class DepartmentRepository(AbstractDepartmentRepository):
    session: Test1DatabaseSession

    def __post_init__(self):
        pass

    def get_all_departments(self) -> List[Department]:
        return self.session.query(Department).all()

    def get_department_by_id(self, department_id: int) -> Optional[Department]:
        return self.session.query(Department).filter(Department.id == department_id).first()

    def create_department(self, name: str, description: str = None, manager_id: int = None) -> Department:
        department = Department(name=name, description=description, manager_id=manager_id)
        self.session.add(department)
        self.session.commit()
        self.session.refresh(department)
        return department

    def update_department(self, department_id: int, name: str = None, description: str = None, manager_id: int = None) \
            -> Optional[Department]:
        department = self.session.query(Department).filter(Department.id == department_id).first()
        if department:
            if name:
                department.name = name
            if description is not None:
                department.description = description
            if manager_id is not None:
                department.manager_id = manager_id
            self.session.commit()
            self.session.refresh(department)
        return department

    def delete_department(self, department_id: int) -> bool:
        department = self.session.query(Department).filter(Department.id == department_id).first()
        if department:
            department.is_active = False
            self.session.commit()
            return True
        return False

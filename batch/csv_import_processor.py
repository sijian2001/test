import csv
import os
from dataclasses import dataclass
from abc import ABC, abstractmethod
from injector import inject
import logging
from business.depart_user_regist_service import DepartUserRegistService, DepartUserRegistInDto
from business.vo.department_vo import DepartmentVo
from business.vo.user_vo import UserVo

logging.basicConfig(level=logging.INFO)

class CsvImportProcessor(ABC):
    @abstractmethod
    def run_csv_import_process(self) -> bool:
        pass

@inject
@dataclass
class DataCsvImportProcessor(CsvImportProcessor):
    depart_user_regist_service: DepartUserRegistService

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)
    
    def run_csv_import_process(self) -> bool:
        try:
            self.logger.info("=== Starting CSV Import Process ===")
            
            # 1. Department CSV読み込み
            self.logger.info("1. Reading departments from CSV...")
            department_list = self._read_departments_from_csv()
            self.logger.info(f"Read {len(department_list)} departments")
            
            # 2. User CSV読み込み
            self.logger.info("2. Reading users from CSV...")
            user_list = self._read_users_from_csv()
            self.logger.info(f"Read {len(user_list)} users")
            
            # 3. DTOを作成してサービスに渡す
            input_dto = DepartUserRegistInDto(
                departmentList=department_list,
                userList=user_list
            )
            
            # 4. DepartUserRegistServiceで一括登録
            self.logger.info("3. Registering departments and users...")
            result_dto = self.depart_user_regist_service.regist_depart_user(input_dto)
            
            self.logger.info(f"Registration completed - Departments: {result_dto.departmentCount}, Users: {result_dto.userCount}")
            self.logger.info("=== CSV Import Process Completed Successfully ===")
            return True
                
        except Exception as e:
            self.logger.error(f"Error during CSV import process: {str(e)}")
            return False
    
    def _read_departments_from_csv(self) -> list[DepartmentVo]:
        csv_path = os.path.join("work", "department.csv")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Department CSV file not found: {csv_path}")
        
        department_list = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    department_vo = DepartmentVo(
                        name=row['name'].strip(),
                        description=row['description'].strip() if row['description'] else None,
                        manager_id=int(row['manager_id']) if row['manager_id'] else None,
                        is_active=row['is_active'].lower() == 'true'
                    )
                    department_list.append(department_vo)
                    self.logger.info(f"Read department: {department_vo.name}")
                    
                except Exception as e:
                    raise ValueError(f"Error processing department row {row}: {str(e)}")
        
        return department_list
    
    def _read_users_from_csv(self) -> list[UserVo]:
        csv_path = os.path.join("work", "user.csv")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"User CSV file not found: {csv_path}")
        
        user_list = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    user_vo = UserVo(
                        username=row['username'].strip(),
                        email=row['email'].strip(),
                        password_hash=row['password_hash'].strip(),
                        first_name=row['first_name'].strip() if row['first_name'] else None,
                        last_name=row['last_name'].strip() if row['last_name'] else None,
                        department_id=int(row['department_id']) if row['department_id'] else None,
                        is_active=row['is_active'].lower() == 'true'
                    )
                    user_list.append(user_vo)
                    self.logger.info(f"Read user: {user_vo.username}")
                    
                except Exception as e:
                    raise ValueError(f"Error processing user row {row}: {str(e)}")
        
        return user_list
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from injector import inject
import logging
from .abstract_service import AbstractService, AbstractInDto, AbstractOutDto
from business.user_info_service import AbstractUserInfoService, UserInfoSearchInDto

logging.basicConfig(level=logging.INFO)

@dataclass
class CsvExportInDto(AbstractInDto):
    output_file_path: str
    sort_by_user_id: bool = True

@dataclass
class CsvExportOutDto(AbstractOutDto):
    exported_count: int
    output_file_path: str
    success: bool

class AbstractCsvExportService(AbstractService):
    @abstractmethod
    def export_user_info_to_csv(self, in_dto: CsvExportInDto) -> CsvExportOutDto:
        pass

    @abstractmethod
    def execute(self, in_dto: CsvExportInDto) -> CsvExportOutDto:
        pass

@inject
@dataclass
class CsvExportService(AbstractCsvExportService):
    user_info_service: AbstractUserInfoService

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    def export_user_info_to_csv(self, in_dto: CsvExportInDto) -> CsvExportOutDto:
        self.logger.info("=== Starting CSV Export Service ===")

        try:
            # Get all user info data
            self.logger.info("Retrieving user info data for CSV export...")
            search_dto = UserInfoSearchInDto()
            result = self.user_info_service.search_user_info(search_dto)

            # Sort by user_id if requested
            user_info_list = result.user_info_list
            if in_dto.sort_by_user_id:
                user_info_list = sorted(user_info_list, key=lambda x: x.user_id)
                self.logger.info(f"Sorted {len(user_info_list)} records by user_id")

            # Prepare result DTO
            result_dto = CsvExportOutDto(
                exported_count=len(user_info_list),
                output_file_path=in_dto.output_file_path,
                success=True
            )

            self.logger.info(f"CSV export service completed - {result_dto.exported_count} records prepared")
            self.logger.info("=== CSV Export Service Completed Successfully ===")

            return result_dto

        except Exception as e:
            self.logger.error(f"Error in CSV export service: {str(e)}")
            return CsvExportOutDto(
                exported_count=0,
                output_file_path=in_dto.output_file_path,
                success=False
            )

    def execute(self, in_dto: CsvExportInDto) -> CsvExportOutDto:
        return self.export_user_info_to_csv(in_dto)
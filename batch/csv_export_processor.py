import csv
import os
from abc import ABC, abstractmethod
from injector import inject
from dataclasses import dataclass
import logging
from business.user_info_service import UserInfoService, UserInfoSearchInDto

logging.basicConfig(level=logging.INFO)

class CsvExportProcessor(ABC):
    @abstractmethod
    def run_csv_export_process(self) -> bool:
        pass

@inject
@dataclass
class UserInfoCsvExportProcessor(CsvExportProcessor):
    user_info_service: UserInfoService

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    def run_csv_export_process(self) -> bool:
        try:
            self.logger.info("=== Starting User Info CSV Export Process ===")

            # 1. Get all user info data sorted by user_id
            self.logger.info("1. Retrieving user info data...")
            search_dto = UserInfoSearchInDto()  # Get all users
            result = self.user_info_service.search_user_info(search_dto)

            # Sort by user_id ascending
            user_info_list = sorted(result.user_info_list, key=lambda x: x.user_id)
            self.logger.info(f"Retrieved {len(user_info_list)} user info records")

            # 2. Prepare output directory
            output_dir = "work"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                self.logger.info(f"Created output directory: {output_dir}")

            # 3. Export to CSV
            output_file = os.path.join(output_dir, "report.csv")
            self.logger.info(f"2. Exporting data to CSV file: {output_file}")

            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                # Define CSV headers
                fieldnames = ['user_id', 'username', 'department_name', 'is_active', 'created_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write header
                writer.writeheader()
                self.logger.info("CSV header written")

                # Write data rows
                for user_info in user_info_list:
                    row = {
                        'user_id': user_info.user_id,
                        'username': user_info.username,
                        'department_name': user_info.department_name or '',
                        'is_active': user_info.is_active or '',
                        'created_at': user_info.created_at.strftime('%Y-%m-%d %H:%M:%S') if user_info.created_at else ''
                    }
                    writer.writerow(row)

                self.logger.info(f"Exported {len(user_info_list)} records to CSV")

            self.logger.info(f"3. CSV export completed successfully!")
            self.logger.info(f"Output file: {os.path.abspath(output_file)}")
            self.logger.info("=== User Info CSV Export Process Completed Successfully ===")
            return True

        except Exception as e:
            self.logger.error(f"Error during CSV export process: {str(e)}")
            return False
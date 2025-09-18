import csv
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

from injector import inject

from business.category_regist_service import CategoryRegistService, CategoryRegistInDto
from domain.vo.category_vo import CategoryVo

logging.basicConfig(level=logging.INFO)


class CategoriesCsvImportProcessor(ABC):
    @abstractmethod
    def run_csv_import_process(self) -> bool:
        pass


@inject
@dataclass
class CategoriesCsvImportProcessorImpl(CategoriesCsvImportProcessor):
    category_regist_service: CategoryRegistService

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    def run_csv_import_process(self) -> bool:
        try:
            self.logger.info("=== Starting Categories CSV Import Process ===")

            # 1. Check CSV file existence
            csv_file_path = os.path.join("work", "categories.csv")
            if not os.path.exists(csv_file_path):
                self.logger.error(f"CSV file not found: {csv_file_path}")
                return False

            self.logger.info(f"1. Reading CSV file: {csv_file_path}")

            # 2. Read and parse CSV file
            category_list = []
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                csv_reader = csv.DictReader(csvfile)

                for row_num, row in enumerate(csv_reader, start=2):  # Start from 2 because header is row 1
                    try:
                        # Validate required fields
                        if not row.get('category_name'):
                            self.logger.warning(f"Row {row_num}: Missing category_name, skipping")
                            continue

                        # Create CategoryVo
                        category_vo = CategoryVo(
                            category_name=row['category_name'].strip(),
                            category_description=row.get('category_description', '').strip() if row.get(
                                'category_description') else None,
                            parent_category_id=int(row['parent_category_id']) if row.get('parent_category_id') and row[
                                'parent_category_id'].strip() else None
                        )

                        category_list.append(category_vo)
                        self.logger.debug(f"Parsed category: {category_vo.category_name}")

                    except ValueError as ve:
                        self.logger.error(f"Row {row_num}: Data conversion error - {str(ve)}")
                        continue
                    except Exception as e:
                        self.logger.error(f"Row {row_num}: Unexpected error - {str(e)}")
                        continue

            self.logger.info(f"2. Successfully parsed {len(category_list)} categories from CSV")

            if not category_list:
                self.logger.warning("No valid categories found in CSV file")
                return True  # Not an error, just empty file

            # 3. Register categories
            self.logger.info("3. Registering categories to database...")
            category_regist_dto = CategoryRegistInDto(categoryList=category_list)
            result = self.category_regist_service.execute(category_regist_dto)

            self.logger.info(f"4. CSV import completed successfully!")
            self.logger.info(f"Total categories registered: {result.categoryCount}")
            self.logger.info("=== Categories CSV Import Process Completed Successfully ===")
            return True

        except FileNotFoundError:
            self.logger.error(f"CSV file not found: {csv_file_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error during CSV import process: {str(e)}")
            return False

import csv
import os
from abc import ABC, abstractmethod
from injector import inject
from dataclasses import dataclass
import logging
from typing import List
from business.product_regist_service import ProductRegistService, ProductRegistInDto
from business.vo.product_vo import ProductVo

logging.basicConfig(level=logging.INFO)

class ProductsCsvImportProcessor(ABC):
    @abstractmethod
    def run_csv_import_process(self) -> bool:
        pass

@inject
@dataclass
class ProductsCsvImportProcessorImpl(ProductsCsvImportProcessor):
    product_regist_service: ProductRegistService

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    def run_csv_import_process(self) -> bool:
        try:
            self.logger.info("=== Starting Products CSV Import Process ===")

            # 1. Check CSV file existence
            csv_file_path = os.path.join("work", "products.csv")
            if not os.path.exists(csv_file_path):
                self.logger.error(f"CSV file not found: {csv_file_path}")
                return False

            self.logger.info(f"1. Reading CSV file: {csv_file_path}")

            # 2. Read and parse CSV file
            product_list = []
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                csv_reader = csv.DictReader(csvfile)

                for row_num, row in enumerate(csv_reader, start=2):  # Start from 2 because header is row 1
                    try:
                        # Validate required fields
                        if not row.get('product_name'):
                            self.logger.warning(f"Row {row_num}: Missing product_name, skipping")
                            continue

                        if not row.get('price'):
                            self.logger.warning(f"Row {row_num}: Missing price, skipping")
                            continue

                        # Create ProductVo
                        product_vo = ProductVo(
                            product_name=row['product_name'].strip(),
                            description=row.get('description', '').strip() if row.get('description') else None,
                            price=float(row['price']),
                            stock_quantity=int(row.get('stock_quantity', 0)),
                            category_id=int(row['category_id']) if row.get('category_id') and row['category_id'].strip() else None
                        )

                        product_list.append(product_vo)
                        self.logger.debug(f"Parsed product: {product_vo.product_name}")

                    except ValueError as ve:
                        self.logger.error(f"Row {row_num}: Data conversion error - {str(ve)}")
                        continue
                    except Exception as e:
                        self.logger.error(f"Row {row_num}: Unexpected error - {str(e)}")
                        continue

            self.logger.info(f"2. Successfully parsed {len(product_list)} products from CSV")

            if not product_list:
                self.logger.warning("No valid products found in CSV file")
                return True  # Not an error, just empty file

            # 3. Register products
            self.logger.info("3. Registering products to database...")
            product_regist_dto = ProductRegistInDto(productList=product_list)
            result = self.product_regist_service.execute(product_regist_dto)

            self.logger.info(f"4. CSV import completed successfully!")
            self.logger.info(f"Total products registered: {result.productCount}")
            self.logger.info("=== Products CSV Import Process Completed Successfully ===")
            return True

        except FileNotFoundError:
            self.logger.error(f"CSV file not found: {csv_file_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error during CSV import process: {str(e)}")
            return False
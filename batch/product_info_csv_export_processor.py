import csv
import os
from abc import ABC, abstractmethod
from injector import inject
from dataclasses import dataclass
import logging
from business.product_info_service import ProductInfoService, ProductInfoSearchInDto

logging.basicConfig(level=logging.INFO)

class ProductInfoCsvExportProcessor(ABC):
    @abstractmethod
    def run_csv_export_process(self) -> bool:
        pass

@inject
@dataclass
class ProductInfoCsvExportProcessorImpl(ProductInfoCsvExportProcessor):
    product_info_service: ProductInfoService

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    def run_csv_export_process(self) -> bool:
        try:
            self.logger.info("=== Starting Product Info CSV Export Process ===")

            # 1. Get all product info data sorted by product_id
            self.logger.info("1. Retrieving product info data...")
            search_dto = ProductInfoSearchInDto(sort_by="name", sort_order="asc")  # Sort by product name
            result = self.product_info_service.search_product_info(search_dto)

            product_info_list = result.product_info_list
            self.logger.info(f"Retrieved {len(product_info_list)} product info records")

            # 2. Prepare output directory
            output_dir = "work"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                self.logger.info(f"Created output directory: {output_dir}")

            # 3. Export to CSV
            output_file = os.path.join(output_dir, "product_info_report.csv")
            self.logger.info(f"2. Exporting data to CSV file: {output_file}")

            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                # Define CSV headers
                fieldnames = [
                    'product_id', 'product_name', 'description', 'price', 'stock_quantity',
                    'category_id', 'category_name', 'category_description', 'parent_category_id',
                    'created_at', 'updated_at'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write header
                writer.writeheader()
                self.logger.info("CSV header written")

                # Write data rows
                for product_info in product_info_list:
                    row = {
                        'product_id': product_info.product_id,
                        'product_name': product_info.product_name or '',
                        'description': product_info.description or '',
                        'price': float(product_info.price) if product_info.price else 0.0,
                        'stock_quantity': product_info.stock_quantity or 0,
                        'category_id': product_info.category_id or '',
                        'category_name': product_info.category_name or '',
                        'category_description': product_info.category_description or '',
                        'parent_category_id': product_info.parent_category_id or '',
                        'created_at': product_info.created_at.strftime('%Y-%m-%d %H:%M:%S') if product_info.created_at else '',
                        'updated_at': product_info.updated_at.strftime('%Y-%m-%d %H:%M:%S') if product_info.updated_at else ''
                    }
                    writer.writerow(row)

                self.logger.info(f"Exported {len(product_info_list)} records to CSV")

            self.logger.info(f"3. CSV export completed successfully!")
            self.logger.info(f"Output file: {os.path.abspath(output_file)}")
            self.logger.info("=== Product Info CSV Export Process Completed Successfully ===")
            return True

        except Exception as e:
            self.logger.error(f"Error during CSV export process: {str(e)}")
            return False
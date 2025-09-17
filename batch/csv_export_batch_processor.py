from dataclasses import dataclass
from .processor import BatchProcessor
from .csv_export_processor import CsvExportProcessor
from injector import inject
import logging

@inject
@dataclass
class CsvExportBatchProcessor(BatchProcessor):
    csv_export_processor: CsvExportProcessor

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    def run_batch_process(self) -> bool:
        try:
            self.logger.info("=== Starting CSV Export Batch Process ===")

            # CSV Export処理を実行
            success = self.csv_export_processor.run_csv_export_process()

            if success:
                self.logger.info("=== CSV Export Batch Process Completed Successfully ===")
            else:
                self.logger.error("=== CSV Export Batch Process Failed ===")

            return success

        except Exception as e:
            self.logger.error(f"Error during CSV export batch process: {str(e)}")
            return False
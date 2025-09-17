from dataclasses import dataclass
from .processor import BatchProcessor
from .csv_import_processor import CsvImportProcessor
from injector import inject
import logging

@inject
@dataclass
class DataBatchProcessor(BatchProcessor):
    csv_import_processor: CsvImportProcessor

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    def run_batch_process(self) -> bool:
        try:
            self.logger.info("=== Starting Data Batch Process ===")

            # CSV インポート処理を実行
            success = self.csv_import_processor.run_csv_import_process()

            if success:
                self.logger.info("=== Data Batch Process Completed Successfully ===")
            else:
                self.logger.error("=== Data Batch Process Failed ===")

            return success

        except Exception as e:
            self.logger.error(f"Error during batch process: {str(e)}")
            return False
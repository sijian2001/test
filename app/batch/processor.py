from abc import ABC, abstractmethod
import logging

logging.basicConfig(level=logging.INFO)

class BatchProcessor(ABC):
    @abstractmethod
    def run_batch_process(self) -> bool:
        pass
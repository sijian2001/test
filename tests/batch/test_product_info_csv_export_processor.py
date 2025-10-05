import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from typing import List, Optional
import sys
import os
import csv
from datetime import datetime

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.batch.product_info_csv_export_processor import ProductInfoCsvExportProcessorImpl
from app.business.product_info_service import ProductInfoService, ProductInfoSearchInDto, ProductInfoOutDto
from app.domain.model.test2.product_info import ProductInfo


class TestProductInfoCsvExportProcessor:
    """Unit tests for ProductInfoCsvExportProcessorImpl class"""

    def setup_method(self):
        """Setup method called before each test"""
        # Create a mock ProductInfoService
        self.mock_product_info_service = Mock(spec=ProductInfoService)

        # Create ProductInfoCsvExportProcessorImpl instance with mocked dependencies
        self.processor = ProductInfoCsvExportProcessorImpl(product_info_service=self.mock_product_info_service)

    def create_mock_product_info(self, product_id: int, product_name: str, description: str = None,
                               price: float = 99.99, stock_quantity: int = 10, category_id: int = 1,
                               category_name: str = "Electronics", category_description: str = None,
                               parent_category_id: int = None, created_at: str = "2025-09-17 17:47:03",
                               updated_at: str = "2025-09-17 17:47:03") -> ProductInfo:
        """Helper method to create mock ProductInfo objects"""
        product_info = Mock(spec=ProductInfo)
        product_info.product_id = product_id
        product_info.product_name = product_name
        product_info.description = description or f"Description for {product_name}"
        product_info.price = price
        product_info.stock_quantity = stock_quantity
        product_info.category_id = category_id
        product_info.category_name = category_name
        product_info.category_description = category_description or f"Description for {category_name}"
        product_info.parent_category_id = parent_category_id

        # Mock datetime objects for created_at and updated_at
        if created_at:
            mock_created_at = Mock()
            mock_created_at.strftime.return_value = created_at
            product_info.created_at = mock_created_at
        else:
            product_info.created_at = None

        if updated_at:
            mock_updated_at = Mock()
            mock_updated_at.strftime.return_value = updated_at
            product_info.updated_at = mock_updated_at
        else:
            product_info.updated_at = None

        return product_info

    @patch('app.batch.product_info_csv_export_processor.os.path.exists')
    @patch('app.batch.product_info_csv_export_processor.os.makedirs')
    @patch('app.batch.product_info_csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_success(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process with successful execution"""
        # Arrange
        mock_exists.return_value = True  # work directory exists
        mock_product_info_list = [
            self.create_mock_product_info(1, "Laptop Pro 15", "High-performance laptop", 1299.99, 10, 1, "Electronics"),
            self.create_mock_product_info(2, "Wireless Mouse", "Ergonomic wireless mouse", 29.99, 50, 2, "Computer Accessories"),
            self.create_mock_product_info(3, "Monitor 24 inch", "4K Ultra HD monitor", 349.99, 15, 3, "Monitors")
        ]
        mock_result = ProductInfoOutDto(product_info_list=mock_product_info_list, total_count=3)
        self.mock_product_info_service.search_product_info.return_value = mock_result

        # Act
        result = self.processor.run_csv_export_process()

        # Assert
        assert result is True
        self.mock_product_info_service.search_product_info.assert_called_once()
        # Verify search was called with sorting parameters
        call_args = self.mock_product_info_service.search_product_info.call_args[0][0]
        assert isinstance(call_args, ProductInfoSearchInDto)
        assert call_args.sort_by == "name"
        assert call_args.sort_order == "asc"

        mock_file.assert_called_once_with(os.path.join("work", "product_info_report.csv"), 'w', newline='', encoding='utf-8')
        mock_makedirs.assert_not_called()  # Directory exists, so makedirs not called

    @patch('app.batch.product_info_csv_export_processor.os.path.exists')
    @patch('app.batch.product_info_csv_export_processor.os.makedirs')
    @patch('app.batch.product_info_csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_creates_directory(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process creates work directory when it doesn't exist"""
        # Arrange
        mock_exists.return_value = False  # work directory doesn't exist
        mock_product_info_list = [self.create_mock_product_info(1, "Laptop Pro 15")]
        mock_result = ProductInfoOutDto(product_info_list=mock_product_info_list, total_count=1)
        self.mock_product_info_service.search_product_info.return_value = mock_result

        # Act
        result = self.processor.run_csv_export_process()

        # Assert
        assert result is True
        mock_makedirs.assert_called_once_with("work")
        mock_file.assert_called_once()

    @patch('app.batch.product_info_csv_export_processor.os.path.exists')
    @patch('app.batch.product_info_csv_export_processor.os.makedirs')
    @patch('app.batch.product_info_csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_empty_data(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process with empty product info data"""
        # Arrange
        mock_exists.return_value = True
        mock_result = ProductInfoOutDto(product_info_list=[], total_count=0)
        self.mock_product_info_service.search_product_info.return_value = mock_result

        # Act
        result = self.processor.run_csv_export_process()

        # Assert
        assert result is True
        self.mock_product_info_service.search_product_info.assert_called_once()
        mock_file.assert_called_once()

    @patch('app.batch.product_info_csv_export_processor.os.path.exists')
    @patch('app.batch.product_info_csv_export_processor.os.makedirs')
    @patch('app.batch.product_info_csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_handles_null_values(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process handles null/None values correctly"""
        # Arrange
        mock_exists.return_value = True
        product_info = Mock(spec=ProductInfo)
        product_info.product_id = 1
        product_info.product_name = None  # Null product name
        product_info.description = None  # Null description
        product_info.price = None  # Null price
        product_info.stock_quantity = None  # Null stock quantity
        product_info.category_id = None  # Null category_id
        product_info.category_name = None  # Null category name
        product_info.category_description = None  # Null category description
        product_info.parent_category_id = None  # Null parent category id
        product_info.created_at = None  # Null created_at
        product_info.updated_at = None  # Null updated_at

        mock_result = ProductInfoOutDto(product_info_list=[product_info], total_count=1)
        self.mock_product_info_service.search_product_info.return_value = mock_result

        # Mock the csv.DictWriter to capture written rows
        with patch('app.batch.product_info_csv_export_processor.csv.DictWriter') as mock_dict_writer:
            mock_writer = Mock()
            mock_dict_writer.return_value = mock_writer

            # Act
            result = self.processor.run_csv_export_process()

            # Assert
            assert result is True
            mock_writer.writerow.assert_called_once()

            # Get the written row data
            written_row = mock_writer.writerow.call_args[0][0]
            assert written_row['product_name'] == ''  # None should become empty string
            assert written_row['description'] == ''  # None should become empty string
            assert written_row['price'] == 0.0  # None should become 0.0
            assert written_row['stock_quantity'] == 0  # None should become 0
            assert written_row['category_id'] == ''  # None should become empty string
            assert written_row['category_name'] == ''  # None should become empty string
            assert written_row['category_description'] == ''  # None should become empty string
            assert written_row['parent_category_id'] == ''  # None should become empty string
            assert written_row['created_at'] == ''  # None should become empty string
            assert written_row['updated_at'] == ''  # None should become empty string

    @patch('app.batch.product_info_csv_export_processor.os.path.exists')
    @patch('app.batch.product_info_csv_export_processor.os.makedirs')
    @patch('app.batch.product_info_csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_csv_headers(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process writes correct CSV headers"""
        # Arrange
        mock_exists.return_value = True
        mock_result = ProductInfoOutDto(product_info_list=[], total_count=0)
        self.mock_product_info_service.search_product_info.return_value = mock_result

        # Mock the csv.DictWriter to capture header writing
        with patch('app.batch.product_info_csv_export_processor.csv.DictWriter') as mock_dict_writer:
            mock_writer = Mock()
            mock_dict_writer.return_value = mock_writer

            # Act
            result = self.processor.run_csv_export_process()

            # Assert
            assert result is True
            # Verify DictWriter was created with correct fieldnames
            expected_fieldnames = [
                'product_id', 'product_name', 'description', 'price', 'stock_quantity',
                'category_id', 'category_name', 'category_description', 'parent_category_id',
                'created_at', 'updated_at'
            ]
            mock_dict_writer.assert_called_once()
            call_args = mock_dict_writer.call_args
            assert call_args[1]['fieldnames'] == expected_fieldnames

            # Verify writeheader was called
            mock_writer.writeheader.assert_called_once()

    def test_run_csv_export_process_service_exception(self):
        """Test run_csv_export_process handles service exceptions"""
        # Arrange
        self.mock_product_info_service.search_product_info.side_effect = Exception("Service error")

        # Act
        result = self.processor.run_csv_export_process()

        # Assert
        assert result is False
        self.mock_product_info_service.search_product_info.assert_called_once()

    @patch('app.batch.product_info_csv_export_processor.os.path.exists')
    @patch('app.batch.product_info_csv_export_processor.os.makedirs')
    @patch('app.batch.product_info_csv_export_processor.open', side_effect=IOError("File write error"))
    def test_run_csv_export_process_file_exception(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process handles file I/O exceptions"""
        # Arrange
        mock_exists.return_value = True
        mock_result = ProductInfoOutDto(product_info_list=[], total_count=0)
        self.mock_product_info_service.search_product_info.return_value = mock_result

        # Act
        result = self.processor.run_csv_export_process()

        # Assert
        assert result is False

    @patch('app.batch.product_info_csv_export_processor.os.makedirs', side_effect=OSError("Permission denied"))
    @patch('app.batch.product_info_csv_export_processor.os.path.exists')
    def test_run_csv_export_process_directory_creation_exception(self, mock_exists, mock_makedirs):
        """Test run_csv_export_process handles directory creation exceptions"""
        # Arrange
        mock_exists.return_value = False  # Directory doesn't exist
        mock_result = ProductInfoOutDto(product_info_list=[], total_count=0)
        self.mock_product_info_service.search_product_info.return_value = mock_result

        # Act
        result = self.processor.run_csv_export_process()

        # Assert
        assert result is False
        mock_makedirs.assert_called_once_with("work")

    @patch('app.batch.product_info_csv_export_processor.os.path.exists')
    @patch('app.batch.product_info_csv_export_processor.os.makedirs')
    @patch('app.batch.product_info_csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_datetime_formatting(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process formats datetime correctly"""
        # Arrange
        mock_exists.return_value = True
        product_info = Mock(spec=ProductInfo)
        product_info.product_id = 1
        product_info.product_name = "Test Product"
        product_info.description = "Test Description"
        product_info.price = 99.99
        product_info.stock_quantity = 10
        product_info.category_id = 1
        product_info.category_name = "Electronics"
        product_info.category_description = "Electronic devices"
        product_info.parent_category_id = None

        # Mock datetime with strftime method
        mock_created_at = Mock()
        mock_created_at.strftime.return_value = "2025-09-17 17:47:03"
        product_info.created_at = mock_created_at

        mock_updated_at = Mock()
        mock_updated_at.strftime.return_value = "2025-09-17 17:47:03"
        product_info.updated_at = mock_updated_at

        mock_result = ProductInfoOutDto(product_info_list=[product_info], total_count=1)
        self.mock_product_info_service.search_product_info.return_value = mock_result

        with patch('app.batch.product_info_csv_export_processor.csv.DictWriter') as mock_dict_writer:
            mock_writer = Mock()
            mock_dict_writer.return_value = mock_writer

            # Act
            result = self.processor.run_csv_export_process()

            # Assert
            assert result is True
            mock_created_at.strftime.assert_called_once_with('%Y-%m-%d %H:%M:%S')
            mock_updated_at.strftime.assert_called_once_with('%Y-%m-%d %H:%M:%S')

            # Verify the formatted datetime was written
            written_row = mock_writer.writerow.call_args[0][0]
            assert written_row['created_at'] == "2025-09-17 17:47:03"
            assert written_row['updated_at'] == "2025-09-17 17:47:03"

    @patch('app.batch.product_info_csv_export_processor.os.path.exists')
    @patch('app.batch.product_info_csv_export_processor.os.makedirs')
    @patch('app.batch.product_info_csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_output_file_path(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process uses correct output file path"""
        # Arrange
        mock_exists.return_value = True
        mock_result = ProductInfoOutDto(product_info_list=[], total_count=0)
        self.mock_product_info_service.search_product_info.return_value = mock_result

        # Act
        result = self.processor.run_csv_export_process()

        # Assert
        assert result is True
        expected_path = os.path.join("work", "product_info_report.csv")
        mock_file.assert_called_once_with(expected_path, 'w', newline='', encoding='utf-8')

    @patch('app.batch.product_info_csv_export_processor.os.path.exists')
    @patch('app.batch.product_info_csv_export_processor.os.makedirs')
    @patch('app.batch.product_info_csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_price_conversion(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process converts price to float correctly"""
        # Arrange
        mock_exists.return_value = True
        product_info = Mock(spec=ProductInfo)
        product_info.product_id = 1
        product_info.product_name = "Test Product"
        product_info.description = "Test Description"
        product_info.price = 123.45  # Ensure this gets converted to float
        product_info.stock_quantity = 10
        product_info.category_id = 1
        product_info.category_name = "Electronics"
        product_info.category_description = "Electronic devices"
        product_info.parent_category_id = None
        product_info.created_at = None
        product_info.updated_at = None

        mock_result = ProductInfoOutDto(product_info_list=[product_info], total_count=1)
        self.mock_product_info_service.search_product_info.return_value = mock_result

        with patch('app.batch.product_info_csv_export_processor.csv.DictWriter') as mock_dict_writer:
            mock_writer = Mock()
            mock_dict_writer.return_value = mock_writer

            # Act
            result = self.processor.run_csv_export_process()

            # Assert
            assert result is True
            written_row = mock_writer.writerow.call_args[0][0]
            assert written_row['price'] == 123.45
            assert isinstance(written_row['price'], float)

    def test_post_init_method(self):
        """Test that __post_init__ method initializes logger correctly"""
        # Act & Assert - should not raise any exceptions
        self.processor.__post_init__()
        assert hasattr(self.processor, 'logger')

    @patch('app.batch.product_info_csv_export_processor.logging.getLogger')
    def test_logging_calls(self, mock_get_logger):
        """Test that appropriate logging calls are made"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        self.processor.__post_init__()
        mock_result = ProductInfoOutDto(product_info_list=[], total_count=0)
        self.mock_product_info_service.search_product_info.return_value = mock_result

        with patch('app.batch.product_info_csv_export_processor.open', mock_open()):
            with patch('app.batch.product_info_csv_export_processor.os.path.exists', return_value=True):
                # Act
                self.processor.run_csv_export_process()

                # Assert
                mock_logger.info.assert_called()
                assert mock_logger.info.call_count >= 6  # Multiple log messages expected


if __name__ == "__main__":
    pytest.main([__file__])
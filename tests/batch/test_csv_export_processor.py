import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from typing import List, Optional
import sys
import os
import csv
from datetime import datetime

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from batch.csv_export_processor import UserInfoCsvExportProcessor
from business.user_info_service import UserInfoService, UserInfoSearchInDto, UserInfoOutDto
from domain.model.test1.user_info import UserInfo


class TestUserInfoCsvExportProcessor:
    """Unit tests for UserInfoCsvExportProcessor class"""

    def setup_method(self):
        """Setup method called before each test"""
        # Create a mock UserInfoService
        self.mock_user_info_service = Mock(spec=UserInfoService)

        # Create UserInfoCsvExportProcessor instance with mocked dependencies
        self.processor = UserInfoCsvExportProcessor(user_info_service=self.mock_user_info_service)

    def create_mock_user_info(self, user_id: int, username: str, department_name: str = "Engineering",
                             is_active: str = "active", created_at: str = "2025-09-17 17:47:03") -> UserInfo:
        """Helper method to create mock UserInfo objects"""
        user_info = Mock(spec=UserInfo)
        user_info.user_id = user_id
        user_info.username = username
        user_info.department_name = department_name
        user_info.is_active = is_active
        # Mock datetime object for created_at
        if created_at:
            mock_datetime = Mock()
            mock_datetime.strftime.return_value = created_at
            user_info.created_at = mock_datetime
        else:
            user_info.created_at = None
        return user_info

    @patch('batch.csv_export_processor.os.path.exists')
    @patch('batch.csv_export_processor.os.makedirs')
    @patch('batch.csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_success(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process with successful execution"""
        # Arrange
        mock_exists.return_value = True  # work directory exists
        mock_user_info_list = [
            self.create_mock_user_info(3, "charlie.brown", "Sales"),
            self.create_mock_user_info(1, "john.doe", "Engineering"),
            self.create_mock_user_info(2, "jane.smith", "Marketing")
        ]
        mock_result = UserInfoOutDto(user_info_list=mock_user_info_list, total_count=3)
        self.mock_user_info_service.search_user_info.return_value = mock_result

        # Act
        result = self.processor.run_csv_export_process()

        # Assert
        assert result is True
        self.mock_user_info_service.search_user_info.assert_called_once()
        mock_file.assert_called_once_with(os.path.join("work", "report.csv"), 'w', newline='', encoding='utf-8')
        mock_makedirs.assert_not_called()  # Directory exists, so makedirs not called

    @patch('batch.csv_export_processor.os.path.exists')
    @patch('batch.csv_export_processor.os.makedirs')
    @patch('batch.csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_creates_directory(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process creates work directory when it doesn't exist"""
        # Arrange
        mock_exists.return_value = False  # work directory doesn't exist
        mock_user_info_list = [self.create_mock_user_info(1, "john.doe", "Engineering")]
        mock_result = UserInfoOutDto(user_info_list=mock_user_info_list, total_count=1)
        self.mock_user_info_service.search_user_info.return_value = mock_result

        # Act
        result = self.processor.run_csv_export_process()

        # Assert
        assert result is True
        mock_makedirs.assert_called_once_with("work")
        mock_file.assert_called_once()

    @patch('batch.csv_export_processor.os.path.exists')
    @patch('batch.csv_export_processor.os.makedirs')
    @patch('batch.csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_empty_data(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process with empty user data"""
        # Arrange
        mock_exists.return_value = True
        mock_result = UserInfoOutDto(user_info_list=[], total_count=0)
        self.mock_user_info_service.search_user_info.return_value = mock_result

        # Act
        result = self.processor.run_csv_export_process()

        # Assert
        assert result is True
        self.mock_user_info_service.search_user_info.assert_called_once()
        mock_file.assert_called_once()

    @patch('batch.csv_export_processor.os.path.exists')
    @patch('batch.csv_export_processor.os.makedirs')
    @patch('batch.csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_sorts_by_user_id(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process sorts data by user_id ascending"""
        # Arrange
        mock_exists.return_value = True
        # Create unsorted list
        mock_user_info_list = [
            self.create_mock_user_info(3, "charlie.brown", "Sales"),
            self.create_mock_user_info(1, "john.doe", "Engineering"),
            self.create_mock_user_info(2, "jane.smith", "Marketing")
        ]
        mock_result = UserInfoOutDto(user_info_list=mock_user_info_list, total_count=3)
        self.mock_user_info_service.search_user_info.return_value = mock_result

        # Mock the csv.DictWriter to capture written rows
        with patch('batch.csv_export_processor.csv.DictWriter') as mock_dict_writer:
            mock_writer = Mock()
            mock_dict_writer.return_value = mock_writer

            # Act
            result = self.processor.run_csv_export_process()

            # Assert
            assert result is True
            # Verify that writerow was called 3 times (for 3 users)
            assert mock_writer.writerow.call_count == 3

            # Get the calls to writerow and verify sorting
            calls = mock_writer.writerow.call_args_list
            assert calls[0][0][0]['user_id'] == 1  # First call should have user_id=1
            assert calls[1][0][0]['user_id'] == 2  # Second call should have user_id=2
            assert calls[2][0][0]['user_id'] == 3  # Third call should have user_id=3

    @patch('batch.csv_export_processor.os.path.exists')
    @patch('batch.csv_export_processor.os.makedirs')
    @patch('batch.csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_handles_null_values(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process handles null/None values correctly"""
        # Arrange
        mock_exists.return_value = True
        user_info = Mock(spec=UserInfo)
        user_info.user_id = 1
        user_info.username = "test.user"
        user_info.department_name = None  # Null department
        user_info.is_active = None  # Null is_active
        user_info.created_at = None  # Null created_at

        mock_result = UserInfoOutDto(user_info_list=[user_info], total_count=1)
        self.mock_user_info_service.search_user_info.return_value = mock_result

        # Mock the csv.DictWriter to capture written rows
        with patch('batch.csv_export_processor.csv.DictWriter') as mock_dict_writer:
            mock_writer = Mock()
            mock_dict_writer.return_value = mock_writer

            # Act
            result = self.processor.run_csv_export_process()

            # Assert
            assert result is True
            mock_writer.writerow.assert_called_once()

            # Get the written row data
            written_row = mock_writer.writerow.call_args[0][0]
            assert written_row['department_name'] == ''  # None should become empty string
            assert written_row['is_active'] == ''  # None should become empty string
            assert written_row['created_at'] == ''  # None should become empty string

    @patch('batch.csv_export_processor.os.path.exists')
    @patch('batch.csv_export_processor.os.makedirs')
    @patch('batch.csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_csv_headers(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process writes correct CSV headers"""
        # Arrange
        mock_exists.return_value = True
        mock_result = UserInfoOutDto(user_info_list=[], total_count=0)
        self.mock_user_info_service.search_user_info.return_value = mock_result

        # Mock the csv.DictWriter to capture header writing
        with patch('batch.csv_export_processor.csv.DictWriter') as mock_dict_writer:
            mock_writer = Mock()
            mock_dict_writer.return_value = mock_writer

            # Act
            result = self.processor.run_csv_export_process()

            # Assert
            assert result is True
            # Verify DictWriter was created with correct fieldnames
            expected_fieldnames = ['user_id', 'username', 'department_name', 'is_active', 'created_at']
            mock_dict_writer.assert_called_once()
            call_args = mock_dict_writer.call_args
            assert call_args[1]['fieldnames'] == expected_fieldnames

            # Verify writeheader was called
            mock_writer.writeheader.assert_called_once()

    def test_run_csv_export_process_service_exception(self):
        """Test run_csv_export_process handles service exceptions"""
        # Arrange
        self.mock_user_info_service.search_user_info.side_effect = Exception("Service error")

        # Act
        result = self.processor.run_csv_export_process()

        # Assert
        assert result is False
        self.mock_user_info_service.search_user_info.assert_called_once()

    @patch('batch.csv_export_processor.os.path.exists')
    @patch('batch.csv_export_processor.os.makedirs')
    @patch('batch.csv_export_processor.open', side_effect=IOError("File write error"))
    def test_run_csv_export_process_file_exception(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process handles file I/O exceptions"""
        # Arrange
        mock_exists.return_value = True
        mock_result = UserInfoOutDto(user_info_list=[], total_count=0)
        self.mock_user_info_service.search_user_info.return_value = mock_result

        # Act
        result = self.processor.run_csv_export_process()

        # Assert
        assert result is False

    @patch('batch.csv_export_processor.os.makedirs', side_effect=OSError("Permission denied"))
    @patch('batch.csv_export_processor.os.path.exists')
    def test_run_csv_export_process_directory_creation_exception(self, mock_exists, mock_makedirs):
        """Test run_csv_export_process handles directory creation exceptions"""
        # Arrange
        mock_exists.return_value = False  # Directory doesn't exist
        mock_result = UserInfoOutDto(user_info_list=[], total_count=0)
        self.mock_user_info_service.search_user_info.return_value = mock_result

        # Act
        result = self.processor.run_csv_export_process()

        # Assert
        assert result is False
        mock_makedirs.assert_called_once_with("work")

    def test_run_csv_export_process_calls_search_user_info_correctly(self):
        """Test run_csv_export_process calls search_user_info with empty search criteria"""
        # Arrange
        mock_result = UserInfoOutDto(user_info_list=[], total_count=0)
        self.mock_user_info_service.search_user_info.return_value = mock_result

        with patch('batch.csv_export_processor.open', mock_open()):
            with patch('batch.csv_export_processor.os.path.exists', return_value=True):
                # Act
                self.processor.run_csv_export_process()

                # Assert
                self.mock_user_info_service.search_user_info.assert_called_once()
                call_args = self.mock_user_info_service.search_user_info.call_args[0][0]
                assert isinstance(call_args, UserInfoSearchInDto)
                assert call_args.user_id is None
                assert call_args.username is None
                assert call_args.department_name is None

    def test_post_init_method(self):
        """Test that __post_init__ method initializes logger correctly"""
        # Act & Assert - should not raise any exceptions
        self.processor.__post_init__()
        assert hasattr(self.processor, 'logger')

    @patch('batch.csv_export_processor.logging.getLogger')
    def test_logging_calls(self, mock_get_logger):
        """Test that appropriate logging calls are made"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        self.processor.__post_init__()
        mock_result = UserInfoOutDto(user_info_list=[], total_count=0)
        self.mock_user_info_service.search_user_info.return_value = mock_result

        with patch('batch.csv_export_processor.open', mock_open()):
            with patch('batch.csv_export_processor.os.path.exists', return_value=True):
                # Act
                self.processor.run_csv_export_process()

                # Assert
                mock_logger.info.assert_called()
                assert mock_logger.info.call_count >= 5  # Multiple log messages expected

    @patch('batch.csv_export_processor.os.path.exists')
    @patch('batch.csv_export_processor.os.makedirs')
    @patch('batch.csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_output_file_path(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process uses correct output file path"""
        # Arrange
        mock_exists.return_value = True
        mock_result = UserInfoOutDto(user_info_list=[], total_count=0)
        self.mock_user_info_service.search_user_info.return_value = mock_result

        # Act
        result = self.processor.run_csv_export_process()

        # Assert
        assert result is True
        expected_path = os.path.join("work", "report.csv")
        mock_file.assert_called_once_with(expected_path, 'w', newline='', encoding='utf-8')

    @patch('batch.csv_export_processor.os.path.exists')
    @patch('batch.csv_export_processor.os.makedirs')
    @patch('batch.csv_export_processor.open', new_callable=mock_open)
    def test_run_csv_export_process_datetime_formatting(self, mock_file, mock_makedirs, mock_exists):
        """Test run_csv_export_process formats datetime correctly"""
        # Arrange
        mock_exists.return_value = True
        user_info = Mock(spec=UserInfo)
        user_info.user_id = 1
        user_info.username = "test.user"
        user_info.department_name = "Engineering"
        user_info.is_active = "active"

        # Mock datetime with strftime method
        mock_datetime = Mock()
        mock_datetime.strftime.return_value = "2025-09-17 17:47:03"
        user_info.created_at = mock_datetime

        mock_result = UserInfoOutDto(user_info_list=[user_info], total_count=1)
        self.mock_user_info_service.search_user_info.return_value = mock_result

        with patch('batch.csv_export_processor.csv.DictWriter') as mock_dict_writer:
            mock_writer = Mock()
            mock_dict_writer.return_value = mock_writer

            # Act
            result = self.processor.run_csv_export_process()

            # Assert
            assert result is True
            mock_datetime.strftime.assert_called_once_with('%Y-%m-%d %H:%M:%S')

            # Verify the formatted datetime was written
            written_row = mock_writer.writerow.call_args[0][0]
            assert written_row['created_at'] == "2025-09-17 17:47:03"


if __name__ == "__main__":
    pytest.main([__file__])
import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
import sys
import os

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from batch.categories_csv_import_processor import CategoriesCsvImportProcessorImpl
from business.category_regist_service import CategoryRegistService, CategoryRegistInDto, CategoryRegistOutDto
from domain.vo.category_vo import CategoryVo


class TestCategoriesCsvImportProcessorImpl:
    """Unit tests for CategoriesCsvImportProcessorImpl class"""

    def setup_method(self):
        """Setup method called before each test"""
        # Create a mock CategoryRegistService
        self.mock_category_regist_service = Mock(spec=CategoryRegistService)

        # Create CategoriesCsvImportProcessorImpl instance with mocked dependencies
        self.processor = CategoriesCsvImportProcessorImpl(
            category_regist_service=self.mock_category_regist_service
        )
        self.processor.__post_init__()

    @patch('batch.categories_csv_import_processor.os.path.exists')
    @patch('batch.categories_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_success(self, mock_file, mock_exists):
        """Test successful CSV import process"""
        # Arrange
        mock_exists.return_value = True

        # Mock CSV content
        csv_content = """category_name,category_description,parent_category_id
Electronics,Electronic devices and gadgets,
Computers,Computer hardware and software,1
Smartphones,Mobile phones and accessories,1"""

        mock_file.return_value.read.return_value = csv_content
        mock_file.return_value.__iter__.return_value = iter(csv_content.splitlines())

        # Mock CSV DictReader behavior
        mock_csv_data = [
            {'category_name': 'Electronics', 'category_description': 'Electronic devices and gadgets', 'parent_category_id': ''},
            {'category_name': 'Computers', 'category_description': 'Computer hardware and software', 'parent_category_id': '1'},
            {'category_name': 'Smartphones', 'category_description': 'Mobile phones and accessories', 'parent_category_id': '1'}
        ]

        with patch('batch.categories_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service response
            mock_result = CategoryRegistOutDto(categoryCount=3)
            self.mock_category_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True
            mock_exists.assert_called_once_with(os.path.join("work", "categories.csv"))
            mock_file.assert_called_once_with(os.path.join("work", "categories.csv"), 'r', encoding='utf-8')

            # Verify service was called with correct DTO
            self.mock_category_regist_service.execute.assert_called_once()
            call_args = self.mock_category_regist_service.execute.call_args[0][0]
            assert isinstance(call_args, CategoryRegistInDto)
            assert len(call_args.categoryList) == 3

            # Verify category data
            categories = call_args.categoryList
            assert categories[0].category_name == 'Electronics'
            assert categories[0].category_description == 'Electronic devices and gadgets'
            assert categories[0].parent_category_id is None

            assert categories[1].category_name == 'Computers'
            assert categories[1].category_description == 'Computer hardware and software'
            assert categories[1].parent_category_id == 1

            assert categories[2].category_name == 'Smartphones'
            assert categories[2].category_description == 'Mobile phones and accessories'
            assert categories[2].parent_category_id == 1

    @patch('batch.categories_csv_import_processor.os.path.exists')
    def test_run_csv_import_process_file_not_found(self, mock_exists):
        """Test CSV import when file does not exist"""
        # Arrange
        mock_exists.return_value = False

        # Act
        result = self.processor.run_csv_import_process()

        # Assert
        assert result is False
        mock_exists.assert_called_once_with(os.path.join("work", "categories.csv"))
        self.mock_category_regist_service.execute.assert_not_called()

    @patch('batch.categories_csv_import_processor.os.path.exists')
    @patch('batch.categories_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_empty_file(self, mock_file, mock_exists):
        """Test CSV import with empty file"""
        # Arrange
        mock_exists.return_value = True

        with patch('batch.categories_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = []

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True
            self.mock_category_regist_service.execute.assert_not_called()

    @patch('batch.categories_csv_import_processor.os.path.exists')
    @patch('batch.categories_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_missing_required_fields(self, mock_file, mock_exists):
        """Test CSV import with missing required fields"""
        # Arrange
        mock_exists.return_value = True

        # Mock CSV data with missing category_name
        mock_csv_data = [
            {'category_name': '', 'category_description': 'Empty name', 'parent_category_id': ''},
            {'category_description': 'No name field', 'parent_category_id': '1'},
            {'category_name': 'Valid Category', 'category_description': 'Valid description', 'parent_category_id': ''}
        ]

        with patch('batch.categories_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service response
            mock_result = CategoryRegistOutDto(categoryCount=1)
            self.mock_category_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True

            # Verify only valid category was processed
            self.mock_category_regist_service.execute.assert_called_once()
            call_args = self.mock_category_regist_service.execute.call_args[0][0]
            assert len(call_args.categoryList) == 1
            assert call_args.categoryList[0].category_name == 'Valid Category'

    @patch('batch.categories_csv_import_processor.os.path.exists')
    @patch('batch.categories_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_data_conversion_error(self, mock_file, mock_exists):
        """Test CSV import with data conversion errors"""
        # Arrange
        mock_exists.return_value = True

        # Mock CSV data with invalid parent_category_id
        mock_csv_data = [
            {'category_name': 'Category1', 'category_description': 'Description1', 'parent_category_id': 'invalid_id'},
            {'category_name': 'Category2', 'category_description': 'Description2', 'parent_category_id': '2'}
        ]

        with patch('batch.categories_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service response
            mock_result = CategoryRegistOutDto(categoryCount=1)
            self.mock_category_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True

            # Verify only valid category was processed
            self.mock_category_regist_service.execute.assert_called_once()
            call_args = self.mock_category_regist_service.execute.call_args[0][0]
            assert len(call_args.categoryList) == 1
            assert call_args.categoryList[0].category_name == 'Category2'
            assert call_args.categoryList[0].parent_category_id == 2

    @patch('batch.categories_csv_import_processor.os.path.exists')
    @patch('batch.categories_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_service_exception(self, mock_file, mock_exists):
        """Test CSV import when service raises exception"""
        # Arrange
        mock_exists.return_value = True

        mock_csv_data = [
            {'category_name': 'Test Category', 'category_description': 'Test Description', 'parent_category_id': ''}
        ]

        with patch('batch.categories_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service to raise exception
            self.mock_category_regist_service.execute.side_effect = Exception("Service error")

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is False
            self.mock_category_regist_service.execute.assert_called_once()

    @patch('batch.categories_csv_import_processor.os.path.exists')
    @patch('batch.categories_csv_import_processor.open')
    def test_run_csv_import_process_file_read_exception(self, mock_file, mock_exists):
        """Test CSV import when file read raises exception"""
        # Arrange
        mock_exists.return_value = True
        mock_file.side_effect = IOError("File read error")

        # Act
        result = self.processor.run_csv_import_process()

        # Assert
        assert result is False
        self.mock_category_regist_service.execute.assert_not_called()

    @patch('batch.categories_csv_import_processor.os.path.exists')
    @patch('batch.categories_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_with_none_and_empty_values(self, mock_file, mock_exists):
        """Test CSV import with None and empty string values"""
        # Arrange
        mock_exists.return_value = True

        mock_csv_data = [
            {'category_name': 'Category1', 'category_description': '', 'parent_category_id': ''},
            {'category_name': 'Category2', 'category_description': None, 'parent_category_id': None},
            {'category_name': 'Category3', 'category_description': 'Valid Description', 'parent_category_id': '0'}
        ]

        with patch('batch.categories_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service response
            mock_result = CategoryRegistOutDto(categoryCount=3)
            self.mock_category_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True

            # Verify categories were processed correctly
            call_args = self.mock_category_regist_service.execute.call_args[0][0]
            categories = call_args.categoryList

            # Category1: empty description should become None
            assert categories[0].category_name == 'Category1'
            assert categories[0].category_description is None
            assert categories[0].parent_category_id is None

            # Category2: None values should remain None
            assert categories[1].category_name == 'Category2'
            assert categories[1].category_description is None
            assert categories[1].parent_category_id is None

            # Category3: valid values
            assert categories[2].category_name == 'Category3'
            assert categories[2].category_description == 'Valid Description'
            assert categories[2].parent_category_id == 0

    @patch('batch.categories_csv_import_processor.os.path.exists')
    @patch('batch.categories_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_with_whitespace(self, mock_file, mock_exists):
        """Test CSV import with whitespace in values"""
        # Arrange
        mock_exists.return_value = True

        mock_csv_data = [
            {'category_name': '  Electronics  ', 'category_description': '  Electronic devices  ', 'parent_category_id': ' 1 '},
            {'category_name': 'Computers\t', 'category_description': '\tComputer hardware\t', 'parent_category_id': ''}
        ]

        with patch('batch.categories_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service response
            mock_result = CategoryRegistOutDto(categoryCount=2)
            self.mock_category_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True

            # Verify whitespace was stripped
            call_args = self.mock_category_regist_service.execute.call_args[0][0]
            categories = call_args.categoryList

            assert categories[0].category_name == 'Electronics'
            assert categories[0].category_description == 'Electronic devices'
            assert categories[0].parent_category_id == 1

            assert categories[1].category_name == 'Computers'
            assert categories[1].category_description == 'Computer hardware'
            assert categories[1].parent_category_id is None

    @patch('batch.categories_csv_import_processor.os.path.exists')
    @patch('batch.categories_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_row_exception_handling(self, mock_file, mock_exists):
        """Test CSV import with row-level exceptions"""
        # Arrange
        mock_exists.return_value = True

        # Create a mock iterator that causes an exception during CSV processing but continues
        mock_csv_data = [
            {'category_name': 'Category1', 'category_description': 'Description1', 'parent_category_id': ''}
        ]

        with patch('batch.categories_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service response
            mock_result = CategoryRegistOutDto(categoryCount=1)
            self.mock_category_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True

            # Verify category was processed
            call_args = self.mock_category_regist_service.execute.call_args[0][0]
            assert len(call_args.categoryList) == 1
            assert call_args.categoryList[0].category_name == 'Category1'

    @patch('batch.categories_csv_import_processor.logging.getLogger')
    def test_post_init_method(self, mock_get_logger):
        """Test that __post_init__ method initializes logger correctly"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Act
        self.processor.__post_init__()

        # Assert
        mock_get_logger.assert_called_with('batch.categories_csv_import_processor')
        assert self.processor.logger == mock_logger

    @patch('batch.categories_csv_import_processor.os.path.exists')
    @patch('batch.categories_csv_import_processor.open', new_callable=mock_open)
    @patch('batch.categories_csv_import_processor.logging.getLogger')
    def test_logging_calls_success(self, mock_get_logger, mock_file, mock_exists):
        """Test that appropriate logging calls are made for successful import"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        self.processor.__post_init__()

        mock_exists.return_value = True

        mock_csv_data = [
            {'category_name': 'Electronics', 'category_description': 'Electronic devices', 'parent_category_id': ''}
        ]

        with patch('batch.categories_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            mock_result = CategoryRegistOutDto(categoryCount=1)
            self.mock_category_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True
            mock_logger.info.assert_called()
            # Should have start, file reading, parsing, registration, and completion messages
            assert mock_logger.info.call_count >= 5

    @patch('batch.categories_csv_import_processor.os.path.exists')
    @patch('batch.categories_csv_import_processor.logging.getLogger')
    def test_logging_calls_file_not_found(self, mock_get_logger, mock_exists):
        """Test that appropriate logging calls are made when file not found"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        self.processor.__post_init__()

        mock_exists.return_value = False

        # Act
        result = self.processor.run_csv_import_process()

        # Assert
        assert result is False
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        assert "CSV file not found" in error_call_args

    def test_category_vo_creation_with_various_parent_ids(self):
        """Test CategoryVo creation with various parent_category_id values"""
        # Test with valid integer string
        category_vo1 = CategoryVo(
            category_name="Test1",
            category_description="Description1",
            parent_category_id=5
        )
        assert category_vo1.parent_category_id == 5

        # Test with None
        category_vo2 = CategoryVo(
            category_name="Test2",
            category_description="Description2",
            parent_category_id=None
        )
        assert category_vo2.parent_category_id is None

        # Test with zero
        category_vo3 = CategoryVo(
            category_name="Test3",
            category_description="Description3",
            parent_category_id=0
        )
        assert category_vo3.parent_category_id == 0


if __name__ == "__main__":
    pytest.main([__file__])
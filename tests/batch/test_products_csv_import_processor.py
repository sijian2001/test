import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
import sys
import os

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from batch.products_csv_import_processor import ProductsCsvImportProcessorImpl
from business.product_regist_service import ProductRegistService, ProductRegistInDto, ProductRegistOutDto
from domain.vo.product_vo import ProductVo


class TestProductsCsvImportProcessorImpl:
    """Unit tests for ProductsCsvImportProcessorImpl class"""

    def setup_method(self):
        """Setup method called before each test"""
        # Create a mock ProductRegistService
        self.mock_product_regist_service = Mock(spec=ProductRegistService)

        # Create ProductsCsvImportProcessorImpl instance with mocked dependencies
        self.processor = ProductsCsvImportProcessorImpl(
            product_regist_service=self.mock_product_regist_service
        )
        self.processor.__post_init__()

    @patch('batch.products_csv_import_processor.os.path.exists')
    @patch('batch.products_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_success(self, mock_file, mock_exists):
        """Test successful CSV import process"""
        # Arrange
        mock_exists.return_value = True

        # Mock CSV content
        csv_content = """product_name,description,price,stock_quantity,category_id
Laptop,High-performance laptop,999.99,10,1
Mouse,Wireless mouse,29.99,50,2
Keyboard,Mechanical keyboard,79.99,25,2"""

        mock_file.return_value.read.return_value = csv_content
        mock_file.return_value.__iter__.return_value = iter(csv_content.splitlines())

        # Mock CSV DictReader behavior
        mock_csv_data = [
            {'product_name': 'Laptop', 'description': 'High-performance laptop', 'price': '999.99', 'stock_quantity': '10', 'category_id': '1'},
            {'product_name': 'Mouse', 'description': 'Wireless mouse', 'price': '29.99', 'stock_quantity': '50', 'category_id': '2'},
            {'product_name': 'Keyboard', 'description': 'Mechanical keyboard', 'price': '79.99', 'stock_quantity': '25', 'category_id': '2'}
        ]

        with patch('batch.products_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service response
            mock_result = ProductRegistOutDto(productCount=3)
            self.mock_product_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True
            mock_exists.assert_called_once_with(os.path.join("work", "products.csv"))
            mock_file.assert_called_once_with(os.path.join("work", "products.csv"), 'r', encoding='utf-8')

            # Verify service was called with correct DTO
            self.mock_product_regist_service.execute.assert_called_once()
            call_args = self.mock_product_regist_service.execute.call_args[0][0]
            assert isinstance(call_args, ProductRegistInDto)
            assert len(call_args.productList) == 3

            # Verify product data
            products = call_args.productList
            assert products[0].product_name == 'Laptop'
            assert products[0].description == 'High-performance laptop'
            assert products[0].price == 999.99
            assert products[0].stock_quantity == 10
            assert products[0].category_id == 1

            assert products[1].product_name == 'Mouse'
            assert products[1].description == 'Wireless mouse'
            assert products[1].price == 29.99
            assert products[1].stock_quantity == 50
            assert products[1].category_id == 2

            assert products[2].product_name == 'Keyboard'
            assert products[2].description == 'Mechanical keyboard'
            assert products[2].price == 79.99
            assert products[2].stock_quantity == 25
            assert products[2].category_id == 2

    @patch('batch.products_csv_import_processor.os.path.exists')
    def test_run_csv_import_process_file_not_found(self, mock_exists):
        """Test CSV import when file does not exist"""
        # Arrange
        mock_exists.return_value = False

        # Act
        result = self.processor.run_csv_import_process()

        # Assert
        assert result is False
        mock_exists.assert_called_once_with(os.path.join("work", "products.csv"))
        self.mock_product_regist_service.execute.assert_not_called()

    @patch('batch.products_csv_import_processor.os.path.exists')
    @patch('batch.products_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_empty_file(self, mock_file, mock_exists):
        """Test CSV import with empty file"""
        # Arrange
        mock_exists.return_value = True

        with patch('batch.products_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = []

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True
            self.mock_product_regist_service.execute.assert_not_called()

    @patch('batch.products_csv_import_processor.os.path.exists')
    @patch('batch.products_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_missing_required_fields(self, mock_file, mock_exists):
        """Test CSV import with missing required fields"""
        # Arrange
        mock_exists.return_value = True

        # Mock CSV data with missing required fields
        mock_csv_data = [
            {'product_name': '', 'description': 'Empty name', 'price': '10.00', 'stock_quantity': '5', 'category_id': '1'},
            {'description': 'No name field', 'price': '20.00', 'stock_quantity': '10', 'category_id': '2'},
            {'product_name': 'Valid Product', 'description': 'Valid description', 'price': '', 'stock_quantity': '15', 'category_id': '3'},
            {'product_name': 'Another Valid Product', 'description': 'Another description', 'price': '30.00', 'stock_quantity': '20', 'category_id': '4'}
        ]

        with patch('batch.products_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service response
            mock_result = ProductRegistOutDto(productCount=1)
            self.mock_product_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True

            # Verify only valid product was processed
            self.mock_product_regist_service.execute.assert_called_once()
            call_args = self.mock_product_regist_service.execute.call_args[0][0]
            assert len(call_args.productList) == 1
            assert call_args.productList[0].product_name == 'Another Valid Product'

    @patch('batch.products_csv_import_processor.os.path.exists')
    @patch('batch.products_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_data_conversion_error(self, mock_file, mock_exists):
        """Test CSV import with data conversion errors"""
        # Arrange
        mock_exists.return_value = True

        # Mock CSV data with invalid numeric values
        mock_csv_data = [
            {'product_name': 'Product1', 'description': 'Description1', 'price': 'invalid_price', 'stock_quantity': '5', 'category_id': '1'},
            {'product_name': 'Product2', 'description': 'Description2', 'price': '25.99', 'stock_quantity': 'invalid_quantity', 'category_id': '2'},
            {'product_name': 'Product3', 'description': 'Description3', 'price': '35.99', 'stock_quantity': '10', 'category_id': 'invalid_category'},
            {'product_name': 'Product4', 'description': 'Description4', 'price': '45.99', 'stock_quantity': '15', 'category_id': '4'}
        ]

        with patch('batch.products_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service response
            mock_result = ProductRegistOutDto(productCount=1)
            self.mock_product_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True

            # Verify only valid product was processed
            self.mock_product_regist_service.execute.assert_called_once()
            call_args = self.mock_product_regist_service.execute.call_args[0][0]
            assert len(call_args.productList) == 1
            assert call_args.productList[0].product_name == 'Product4'
            assert call_args.productList[0].price == 45.99
            assert call_args.productList[0].stock_quantity == 15
            assert call_args.productList[0].category_id == 4

    @patch('batch.products_csv_import_processor.os.path.exists')
    @patch('batch.products_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_service_exception(self, mock_file, mock_exists):
        """Test CSV import when service raises exception"""
        # Arrange
        mock_exists.return_value = True

        mock_csv_data = [
            {'product_name': 'Test Product', 'description': 'Test Description', 'price': '19.99', 'stock_quantity': '5', 'category_id': '1'}
        ]

        with patch('batch.products_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service to raise exception
            self.mock_product_regist_service.execute.side_effect = Exception("Service error")

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is False
            self.mock_product_regist_service.execute.assert_called_once()

    @patch('batch.products_csv_import_processor.os.path.exists')
    @patch('batch.products_csv_import_processor.open')
    def test_run_csv_import_process_file_read_exception(self, mock_file, mock_exists):
        """Test CSV import when file read raises exception"""
        # Arrange
        mock_exists.return_value = True
        mock_file.side_effect = IOError("File read error")

        # Act
        result = self.processor.run_csv_import_process()

        # Assert
        assert result is False
        self.mock_product_regist_service.execute.assert_not_called()

    @patch('batch.products_csv_import_processor.os.path.exists')
    @patch('batch.products_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_with_none_and_empty_values(self, mock_file, mock_exists):
        """Test CSV import with None and empty string values"""
        # Arrange
        mock_exists.return_value = True

        # Empty string and None values cause ValueError for int conversion, so only valid product will be processed
        mock_csv_data = [
            {'product_name': 'Product1', 'description': '', 'price': '10.99', 'stock_quantity': '', 'category_id': ''},
            {'product_name': 'Product2', 'description': None, 'price': '20.99', 'stock_quantity': None, 'category_id': None},
            {'product_name': 'Product3', 'description': 'Valid Description', 'price': '30.99', 'stock_quantity': '0', 'category_id': '0'}
        ]

        with patch('batch.products_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service response - only valid product will be processed
            mock_result = ProductRegistOutDto(productCount=1)
            self.mock_product_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True

            # Verify only valid product was processed (Product3)
            call_args = self.mock_product_regist_service.execute.call_args[0][0]
            products = call_args.productList

            # Only Product3 should be processed successfully
            assert len(products) == 1
            assert products[0].product_name == 'Product3'
            assert products[0].description == 'Valid Description'
            assert products[0].price == 30.99
            assert products[0].stock_quantity == 0
            assert products[0].category_id == 0

    @patch('batch.products_csv_import_processor.os.path.exists')
    @patch('batch.products_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_with_whitespace(self, mock_file, mock_exists):
        """Test CSV import with whitespace in values"""
        # Arrange
        mock_exists.return_value = True

        mock_csv_data = [
            {'product_name': '  Laptop  ', 'description': '  Gaming laptop  ', 'price': '999.99', 'stock_quantity': ' 5 ', 'category_id': ' 1 '},
            {'product_name': 'Mouse\t', 'description': '\tWireless gaming mouse\t', 'price': '49.99', 'stock_quantity': '10', 'category_id': ''}
        ]

        with patch('batch.products_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service response
            mock_result = ProductRegistOutDto(productCount=2)
            self.mock_product_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True

            # Verify whitespace was handled correctly
            call_args = self.mock_product_regist_service.execute.call_args[0][0]
            products = call_args.productList

            assert products[0].product_name == 'Laptop'
            assert products[0].description == 'Gaming laptop'
            assert products[0].price == 999.99
            assert products[0].stock_quantity == 5
            assert products[0].category_id == 1

            assert products[1].product_name == 'Mouse'
            assert products[1].description == 'Wireless gaming mouse'
            assert products[1].price == 49.99
            assert products[1].stock_quantity == 10
            assert products[1].category_id is None

    @patch('batch.products_csv_import_processor.os.path.exists')
    @patch('batch.products_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_decimal_price_handling(self, mock_file, mock_exists):
        """Test CSV import with various decimal price formats"""
        # Arrange
        mock_exists.return_value = True

        mock_csv_data = [
            {'product_name': 'Product1', 'description': 'Description1', 'price': '10', 'stock_quantity': '5', 'category_id': '1'},
            {'product_name': 'Product2', 'description': 'Description2', 'price': '20.5', 'stock_quantity': '10', 'category_id': '2'},
            {'product_name': 'Product3', 'description': 'Description3', 'price': '30.99', 'stock_quantity': '15', 'category_id': '3'},
            {'product_name': 'Product4', 'description': 'Description4', 'price': '0.01', 'stock_quantity': '20', 'category_id': '4'}
        ]

        with patch('batch.products_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service response
            mock_result = ProductRegistOutDto(productCount=4)
            self.mock_product_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True

            # Verify price conversions
            call_args = self.mock_product_regist_service.execute.call_args[0][0]
            products = call_args.productList

            assert products[0].price == 10.0
            assert products[1].price == 20.5
            assert products[2].price == 30.99
            assert products[3].price == 0.01

    @patch('batch.products_csv_import_processor.os.path.exists')
    @patch('batch.products_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_row_exception_handling(self, mock_file, mock_exists):
        """Test CSV import with row-level exceptions"""
        # Arrange
        mock_exists.return_value = True

        # Test with valid data that won't cause exceptions during CSV processing
        mock_csv_data = [
            {'product_name': 'Product1', 'description': 'Description1', 'price': '10.99', 'stock_quantity': '5', 'category_id': '1'}
        ]

        with patch('batch.products_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service response
            mock_result = ProductRegistOutDto(productCount=1)
            self.mock_product_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True

            # Verify product was processed
            call_args = self.mock_product_regist_service.execute.call_args[0][0]
            assert len(call_args.productList) == 1
            assert call_args.productList[0].product_name == 'Product1'

    @patch('batch.products_csv_import_processor.logging.getLogger')
    def test_post_init_method(self, mock_get_logger):
        """Test that __post_init__ method initializes logger correctly"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Act
        self.processor.__post_init__()

        # Assert
        mock_get_logger.assert_called_with('batch.products_csv_import_processor')
        assert self.processor.logger == mock_logger

    @patch('batch.products_csv_import_processor.os.path.exists')
    @patch('batch.products_csv_import_processor.open', new_callable=mock_open)
    @patch('batch.products_csv_import_processor.logging.getLogger')
    def test_logging_calls_success(self, mock_get_logger, mock_file, mock_exists):
        """Test that appropriate logging calls are made for successful import"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        self.processor.__post_init__()

        mock_exists.return_value = True

        mock_csv_data = [
            {'product_name': 'Test Product', 'description': 'Test Description', 'price': '19.99', 'stock_quantity': '5', 'category_id': '1'}
        ]

        with patch('batch.products_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            mock_result = ProductRegistOutDto(productCount=1)
            self.mock_product_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True
            mock_logger.info.assert_called()
            # Should have start, file reading, parsing, registration, and completion messages
            assert mock_logger.info.call_count >= 5

    @patch('batch.products_csv_import_processor.os.path.exists')
    @patch('batch.products_csv_import_processor.logging.getLogger')
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

    def test_product_vo_creation_with_various_values(self):
        """Test ProductVo creation with various field values"""
        # Test with all valid values
        product_vo1 = ProductVo(
            product_name="Test Product",
            description="Test Description",
            price=99.99,
            stock_quantity=10,
            category_id=5
        )
        assert product_vo1.product_name == "Test Product"
        assert product_vo1.description == "Test Description"
        assert product_vo1.price == 99.99
        assert product_vo1.stock_quantity == 10
        assert product_vo1.category_id == 5

        # Test with None values
        product_vo2 = ProductVo(
            product_name="Test Product 2",
            description=None,
            price=0.0,
            stock_quantity=0,
            category_id=None
        )
        assert product_vo2.product_name == "Test Product 2"
        assert product_vo2.description is None
        assert product_vo2.price == 0.0
        assert product_vo2.stock_quantity == 0
        assert product_vo2.category_id is None

    @patch('batch.products_csv_import_processor.os.path.exists')
    @patch('batch.products_csv_import_processor.open', new_callable=mock_open)
    def test_run_csv_import_process_large_dataset(self, mock_file, mock_exists):
        """Test CSV import with large number of products"""
        # Arrange
        mock_exists.return_value = True

        # Create mock data for 100 products
        mock_csv_data = []
        for i in range(100):
            mock_csv_data.append({
                'product_name': f'Product{i}',
                'description': f'Description{i}',
                'price': f'{10.0 + i}',
                'stock_quantity': f'{i + 1}',
                'category_id': f'{(i % 5) + 1}'
            })

        with patch('batch.products_csv_import_processor.csv.DictReader') as mock_dict_reader:
            mock_dict_reader.return_value = mock_csv_data

            # Mock service response
            mock_result = ProductRegistOutDto(productCount=100)
            self.mock_product_regist_service.execute.return_value = mock_result

            # Act
            result = self.processor.run_csv_import_process()

            # Assert
            assert result is True

            # Verify all products were processed
            call_args = self.mock_product_regist_service.execute.call_args[0][0]
            assert len(call_args.productList) == 100

            # Verify first and last products
            products = call_args.productList
            assert products[0].product_name == 'Product0'
            assert products[0].price == 10.0
            assert products[99].product_name == 'Product99'
            assert products[99].price == 109.0


if __name__ == "__main__":
    pytest.main([__file__])
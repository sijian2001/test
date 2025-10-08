import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List
import sys
import os

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.business.product_regist_service import ProductRegistService, ProductRegistInDto, ProductRegistOutDto
from app.domain.repository.test2.product_repository import ProductRepository
from app.domain.model.test2.product import Product
from app.business.vo.product_vo import ProductVo
from app.domain.session_holder import SessionHolder


# Transactional デコレーターのSessionHolderをモックするためのデコレーター
def mock_transactional_session(test_func):
    """Decorator to mock SessionHolder for Transactional decorator"""
    def wrapper(self, *args, **kwargs):
        with patch('app.business.decorators.transactional.SessionHolder') as mock_holder:
            mock_holder.get_session.return_value = self.mock_session
            return test_func(self, *args, **kwargs)
    wrapper.__name__ = test_func.__name__
    wrapper.__doc__ = test_func.__doc__
    return wrapper


class TestProductRegistService:
    """Unit tests for ProductRegistService class"""

    def setup_method(self):
        """Setup method called before each test"""
        # モックセッションの作成
        self.mock_session = Mock()
        self.mock_session.begin = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.rollback = Mock()
        self.mock_session.close = Mock()

        # SessionHolderをクリア
        SessionHolder.clear()

        # モックセッションを登録
        SessionHolder.register('test2', lambda: self.mock_session)

        # Create a mock ProductRepository
        self.mock_repository = Mock(spec=ProductRepository)

        # Create ProductRegistService instance with mocked dependencies
        self.service = ProductRegistService(product_repository=self.mock_repository)

    def teardown_method(self):
        """Teardown method called after each test"""
        SessionHolder.clear()

    def create_product_vo(self, product_name: str, description: str = None, price: float = 99.99,
                         stock_quantity: int = 10, category_id: int = 1) -> ProductVo:
        """Helper method to create ProductVo objects"""
        return ProductVo(
            product_name=product_name,
            description=description or f"Description for {product_name}",
            price=price,
            stock_quantity=stock_quantity,
            category_id=category_id
        )

    def test_execute_single_product_success(self):
        """Test execute with single product registration success"""
        # Arrange
        product_vo = self.create_product_vo("Laptop Pro 15", "High-performance laptop", 1299.99, 10, 1)
        in_dto = ProductRegistInDto(productList=[product_vo])

        # Mock repository to return successfully created product
        mock_product = Mock(spec=Product)
        self.mock_repository.create_product.return_value = mock_product

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, ProductRegistOutDto)
        assert result.productCount == 1
        self.mock_repository.create_product.assert_called_once()

        # Verify the Product object was created with correct parameters
        call_args = self.mock_repository.create_product.call_args[0][0]
        assert call_args.product_name == "Laptop Pro 15"
        assert call_args.description == "High-performance laptop"
        assert call_args.price == 1299.99
        assert call_args.stock_quantity == 10
        assert call_args.category_id == 1

    def test_execute_multiple_products_success(self):
        """Test execute with multiple products registration success"""
        # Arrange
        product_vo_list = [
            self.create_product_vo("Laptop Pro 15", "High-performance laptop", 1299.99, 10, 1),
            self.create_product_vo("Wireless Mouse", "Ergonomic wireless mouse", 29.99, 50, 2),
            self.create_product_vo("Monitor 24 inch", "4K Ultra HD monitor", 349.99, 15, 3)
        ]
        in_dto = ProductRegistInDto(productList=product_vo_list)

        # Mock repository to return successfully created products
        mock_product = Mock(spec=Product)
        self.mock_repository.create_product.return_value = mock_product

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, ProductRegistOutDto)
        assert result.productCount == 3
        assert self.mock_repository.create_product.call_count == 3

        # Verify each product was created with correct parameters
        call_args_list = self.mock_repository.create_product.call_args_list

        # First product
        first_call = call_args_list[0][0][0]
        assert first_call.product_name == "Laptop Pro 15"
        assert first_call.description == "High-performance laptop"
        assert first_call.price == 1299.99
        assert first_call.stock_quantity == 10
        assert first_call.category_id == 1

        # Second product
        second_call = call_args_list[1][0][0]
        assert second_call.product_name == "Wireless Mouse"
        assert second_call.description == "Ergonomic wireless mouse"
        assert second_call.price == 29.99
        assert second_call.stock_quantity == 50
        assert second_call.category_id == 2

        # Third product
        third_call = call_args_list[2][0][0]
        assert third_call.product_name == "Monitor 24 inch"
        assert third_call.description == "4K Ultra HD monitor"
        assert third_call.price == 349.99
        assert third_call.stock_quantity == 15
        assert third_call.category_id == 3

    def test_execute_empty_product_list(self):
        """Test execute with empty product list"""
        # Arrange
        in_dto = ProductRegistInDto(productList=[])

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, ProductRegistOutDto)
        assert result.productCount == 0
        self.mock_repository.create_product.assert_not_called()

    def test_execute_product_with_none_description(self):
        """Test execute with product having None description"""
        # Arrange
        product_vo = ProductVo(
            product_name="Test Product",
            description=None,
            price=99.99,
            stock_quantity=5,
            category_id=1
        )
        in_dto = ProductRegistInDto(productList=[product_vo])

        # Mock repository
        mock_product = Mock(spec=Product)
        self.mock_repository.create_product.return_value = mock_product

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, ProductRegistOutDto)
        assert result.productCount == 1

        # Verify the Product object was created with None description
        call_args = self.mock_repository.create_product.call_args[0][0]
        assert call_args.product_name == "Test Product"
        assert call_args.description is None
        assert call_args.price == 99.99
        assert call_args.stock_quantity == 5
        assert call_args.category_id == 1

    def test_execute_product_with_none_category_id(self):
        """Test execute with product having None category_id"""
        # Arrange
        product_vo = ProductVo(
            product_name="Uncategorized Product",
            description="Product without category",
            price=50.0,
            stock_quantity=20,
            category_id=None
        )
        in_dto = ProductRegistInDto(productList=[product_vo])

        # Mock repository
        mock_product = Mock(spec=Product)
        self.mock_repository.create_product.return_value = mock_product

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, ProductRegistOutDto)
        assert result.productCount == 1

        # Verify the Product object was created with None category_id
        call_args = self.mock_repository.create_product.call_args[0][0]
        assert call_args.product_name == "Uncategorized Product"
        assert call_args.description == "Product without category"
        assert call_args.price == 50.0
        assert call_args.stock_quantity == 20
        assert call_args.category_id is None

    def test_execute_product_repository_exception(self):
        """Test execute handles repository exceptions correctly"""
        # Arrange
        product_vo = self.create_product_vo("Test Product")
        in_dto = ProductRegistInDto(productList=[product_vo])

        # Mock repository to raise exception
        self.mock_repository.create_product.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.execute(in_dto)

        assert str(exc_info.value) == "Database error"
        self.mock_repository.create_product.assert_called_once()

    def test_execute_partial_failure_with_multiple_products(self):
        """Test execute with partial failure in multiple products"""
        # Arrange
        product_vo_list = [
            self.create_product_vo("Product 1"),
            self.create_product_vo("Failing Product"),
            self.create_product_vo("Product 3")
        ]
        in_dto = ProductRegistInDto(productList=product_vo_list)

        # Mock repository: first succeeds, second fails, third never called due to exception
        mock_product = Mock(spec=Product)
        self.mock_repository.create_product.side_effect = [
            mock_product,  # First call succeeds
            Exception("Database error"),  # Second call fails
        ]

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.execute(in_dto)

        assert str(exc_info.value) == "Database error"
        # Only first two products should have been attempted
        assert self.mock_repository.create_product.call_count == 2

    def test_execute_with_different_price_formats(self):
        """Test execute with various price formats"""
        # Arrange
        product_vo_list = [
            self.create_product_vo("Cheap Product", price=9.99),
            self.create_product_vo("Expensive Product", price=9999.99),
            self.create_product_vo("Free Product", price=0.0),
            self.create_product_vo("Decimal Product", price=123.456)
        ]
        in_dto = ProductRegistInDto(productList=product_vo_list)

        # Mock repository
        mock_product = Mock(spec=Product)
        self.mock_repository.create_product.return_value = mock_product

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, ProductRegistOutDto)
        assert result.productCount == 4
        assert self.mock_repository.create_product.call_count == 4

        # Verify prices are preserved correctly
        call_args_list = self.mock_repository.create_product.call_args_list
        assert call_args_list[0][0][0].price == 9.99
        assert call_args_list[1][0][0].price == 9999.99
        assert call_args_list[2][0][0].price == 0.0
        assert call_args_list[3][0][0].price == 123.456

    def test_execute_with_different_stock_quantities(self):
        """Test execute with various stock quantity values"""
        # Arrange
        product_vo_list = [
            self.create_product_vo("No Stock Product", stock_quantity=0),
            self.create_product_vo("Low Stock Product", stock_quantity=1),
            self.create_product_vo("High Stock Product", stock_quantity=1000)
        ]
        in_dto = ProductRegistInDto(productList=product_vo_list)

        # Mock repository
        mock_product = Mock(spec=Product)
        self.mock_repository.create_product.return_value = mock_product

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, ProductRegistOutDto)
        assert result.productCount == 3

        # Verify stock quantities are preserved correctly
        call_args_list = self.mock_repository.create_product.call_args_list
        assert call_args_list[0][0][0].stock_quantity == 0
        assert call_args_list[1][0][0].stock_quantity == 1
        assert call_args_list[2][0][0].stock_quantity == 1000

    def test_post_init_method(self):
        """Test that __post_init__ method initializes logger correctly"""
        # Act & Assert - should not raise any exceptions
        self.service.__post_init__()
        assert hasattr(self.service, 'logger')

    @patch('app.business.product_regist_service.logging.getLogger')
    def test_logging_calls_success(self, mock_get_logger):
        """Test that appropriate logging calls are made for successful registration"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        self.service.__post_init__()

        product_vo = self.create_product_vo("Test Product")
        in_dto = ProductRegistInDto(productList=[product_vo])

        mock_product = Mock(spec=Product)
        self.mock_repository.create_product.return_value = mock_product

        # Act
        self.service.execute(in_dto)

        # Assert
        mock_logger.info.assert_called()
        # Should have at least: start, per-product, count, and completion messages
        assert mock_logger.info.call_count >= 4

    @patch('app.business.product_regist_service.logging.getLogger')
    def test_logging_calls_failure(self, mock_get_logger):
        """Test that appropriate logging calls are made for failed registration"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        self.service.__post_init__()

        product_vo = self.create_product_vo("Failing Product")
        in_dto = ProductRegistInDto(productList=[product_vo])

        # Mock repository to raise exception
        self.mock_repository.create_product.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            self.service.execute(in_dto)

        # Verify error logging was called
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        assert "Failed to register product Failing Product" in error_call_args
        assert "Database error" in error_call_args

    def test_product_entity_creation(self):
        """Test that Product entities are created correctly from ProductVo objects"""
        # Arrange
        product_vo = ProductVo(
            product_name="Test Product",
            description="Test Description",
            price=199.99,
            stock_quantity=25,
            category_id=5
        )
        in_dto = ProductRegistInDto(productList=[product_vo])

        # Mock repository
        mock_product = Mock(spec=Product)
        self.mock_repository.create_product.return_value = mock_product

        # Act
        result = self.service.execute(in_dto)

        # Assert
        self.mock_repository.create_product.assert_called_once()

        # Get the Product object that was passed to create_product
        created_product = self.mock_repository.create_product.call_args[0][0]

        # Verify it's a Product instance (or at least has the expected attributes)
        assert hasattr(created_product, 'product_name')
        assert hasattr(created_product, 'description')
        assert hasattr(created_product, 'price')
        assert hasattr(created_product, 'stock_quantity')
        assert hasattr(created_product, 'category_id')

        # Verify the values were correctly transferred from VO to entity
        assert created_product.product_name == "Test Product"
        assert created_product.description == "Test Description"
        assert created_product.price == 199.99
        assert created_product.stock_quantity == 25
        assert created_product.category_id == 5

    def test_in_dto_validation(self):
        """Test that ProductRegistInDto accepts the expected structure"""
        # Arrange
        product_vo_list = [
            self.create_product_vo("Product 1"),
            self.create_product_vo("Product 2")
        ]

        # Act
        in_dto = ProductRegistInDto(productList=product_vo_list)

        # Assert
        assert isinstance(in_dto, ProductRegistInDto)
        assert len(in_dto.productList) == 2
        assert in_dto.productList[0].product_name == "Product 1"
        assert in_dto.productList[1].product_name == "Product 2"

    def test_out_dto_structure(self):
        """Test that ProductRegistOutDto has the expected structure"""
        # Act
        out_dto = ProductRegistOutDto(productCount=10)

        # Assert
        assert isinstance(out_dto, ProductRegistOutDto)
        assert out_dto.productCount == 10


if __name__ == "__main__":
    pytest.main([__file__])
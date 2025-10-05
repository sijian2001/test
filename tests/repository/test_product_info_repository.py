import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List, Optional
import sys
import os

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.domain.repository.test2.product_info_repository import ProductInfoRepository
from app.domain.model.test2.product_info import ProductInfo
from sqlalchemy.orm import Session


class TestProductInfoRepository:
    """Unit tests for ProductInfoRepository class"""

    def setup_method(self):
        """Setup method called before each test"""
        # Create a mock Session (since Test2DatabaseSession now inherits from Session)
        self.mock_db_session = Mock(spec=Session)

        # Create ProductInfoRepository instance with mocked dependencies
        self.repository = ProductInfoRepository(db_session=self.mock_db_session)

    def create_mock_product_info(self, product_id: int, product_name: str, price: float = 99.99,
                                stock_quantity: int = 10, category_id: int = 1, category_name: str = "Electronics",
                                description: str = None, parent_category_id: int = None) -> ProductInfo:
        """Helper method to create mock ProductInfo objects"""
        product_info = Mock(spec=ProductInfo)
        product_info.product_id = product_id
        product_info.product_name = product_name
        product_info.description = description or f"Description for {product_name}"
        product_info.price = price
        product_info.stock_quantity = stock_quantity
        product_info.category_id = category_id
        product_info.category_name = category_name
        product_info.category_description = f"Description for {category_name}"
        product_info.parent_category_id = parent_category_id
        product_info.created_at = "2025-09-17 17:47:03"
        product_info.updated_at = "2025-09-17 17:47:03"
        return product_info

    def test_get_all_product_info_success(self):
        """Test get_all_product_info returns all product info with category details"""
        # Arrange
        mock_product_infos = [
            self.create_mock_product_info(1, "Laptop Pro 15", 1299.99, 10, 1, "Electronics"),
            self.create_mock_product_info(2, "Wireless Mouse", 29.99, 50, 2, "Computer Accessories"),
            self.create_mock_product_info(3, "Monitor 24 inch", 349.99, 15, 3, "Monitors")
        ]
        self.mock_db_session.query.return_value.all.return_value = mock_product_infos

        # Act
        result = self.repository.get_all_product_info()

        # Assert
        assert result == mock_product_infos
        assert len(result) == 3
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()
        self.mock_db_session.query.assert_called_once_with(ProductInfo)
        self.mock_db_session.query.return_value.all.assert_called_once()

    def test_get_all_product_info_empty_result(self):
        """Test get_all_product_info returns empty list when no product info found"""
        # Arrange
        self.mock_db_session.query.return_value.all.return_value = []

        # Act
        result = self.repository.get_all_product_info()

        # Assert
        assert result == []
        assert len(result) == 0
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_info_by_id_success(self):
        """Test get_product_info_by_id returns product info when found"""
        # Arrange
        product_id = 1
        mock_product_info = self.create_mock_product_info(1, "Laptop Pro 15")
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_product_info

        # Act
        result = self.repository.get_product_info_by_id(product_id)

        # Assert
        assert result == mock_product_info
        assert result.product_id == product_id
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()
        self.mock_db_session.query.assert_called_once_with(ProductInfo)

    def test_get_product_info_by_id_not_found(self):
        """Test get_product_info_by_id returns None when product info not found"""
        # Arrange
        product_id = 999
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.repository.get_product_info_by_id(product_id)

        # Assert
        assert result is None
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_info_by_name_success(self):
        """Test get_product_info_by_name returns product info when found"""
        # Arrange
        product_name = "Laptop Pro 15"
        mock_product_info = self.create_mock_product_info(1, product_name)
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_product_info

        # Act
        result = self.repository.get_product_info_by_name(product_name)

        # Assert
        assert result == mock_product_info
        assert result.product_name == product_name
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_info_by_category_success(self):
        """Test get_product_info_by_category returns product info for specified category"""
        # Arrange
        category_id = 1
        mock_product_infos = [
            self.create_mock_product_info(1, "Laptop Pro 15", category_id=1, category_name="Electronics"),
            self.create_mock_product_info(7, "Smartphone Pro", category_id=1, category_name="Electronics")
        ]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_product_infos

        # Act
        result = self.repository.get_product_info_by_category(category_id)

        # Assert
        assert result == mock_product_infos
        assert len(result) == 2
        for product_info in result:
            assert product_info.category_id == category_id
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_info_by_category_name_success(self):
        """Test get_product_info_by_category_name returns product info for specified category name"""
        # Arrange
        category_name = "Electronics"
        mock_product_infos = [
            self.create_mock_product_info(1, "Laptop Pro 15", category_name="Electronics"),
            self.create_mock_product_info(7, "Smartphone Pro", category_name="Electronics")
        ]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_product_infos

        # Act
        result = self.repository.get_product_info_by_category_name(category_name)

        # Assert
        assert result == mock_product_infos
        assert len(result) == 2
        for product_info in result:
            assert product_info.category_name == category_name
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_info_by_price_range_success(self):
        """Test get_product_info_by_price_range returns product info within price range"""
        # Arrange
        min_price = 100.0
        max_price = 500.0
        mock_product_infos = [
            self.create_mock_product_info(3, "Monitor 24 inch", 349.99),
            self.create_mock_product_info(10, "External SSD 1TB", 149.99)
        ]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_product_infos

        # Act
        result = self.repository.get_product_info_by_price_range(min_price, max_price)

        # Assert
        assert result == mock_product_infos
        assert len(result) == 2
        for product_info in result:
            assert min_price <= product_info.price <= max_price
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_info_in_stock_success(self):
        """Test get_product_info_in_stock returns product info with stock > 0"""
        # Arrange
        mock_product_infos = [
            self.create_mock_product_info(1, "Laptop Pro 15", stock_quantity=10),
            self.create_mock_product_info(2, "Wireless Mouse", stock_quantity=50)
        ]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_product_infos

        # Act
        result = self.repository.get_product_info_in_stock()

        # Assert
        assert result == mock_product_infos
        assert len(result) == 2
        for product_info in result:
            assert product_info.stock_quantity > 0
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_info_out_of_stock_success(self):
        """Test get_product_info_out_of_stock returns product info with stock <= 0"""
        # Arrange
        mock_product_infos = [
            self.create_mock_product_info(11, "Out of Stock Product", stock_quantity=0)
        ]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_product_infos

        # Act
        result = self.repository.get_product_info_out_of_stock()

        # Assert
        assert result == mock_product_infos
        assert len(result) == 1
        for product_info in result:
            assert product_info.stock_quantity <= 0
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_search_product_info_by_name_success(self):
        """Test search_product_info_by_name returns product info matching search term"""
        # Arrange
        search_term = "Pro"
        mock_product_infos = [
            self.create_mock_product_info(1, "Laptop Pro 15"),
            self.create_mock_product_info(7, "Smartphone Pro")
        ]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_product_infos

        # Act
        result = self.repository.search_product_info_by_name(search_term)

        # Assert
        assert result == mock_product_infos
        assert len(result) == 2
        for product_info in result:
            assert search_term in product_info.product_name
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_search_product_info_by_description_success(self):
        """Test search_product_info_by_description returns product info matching search term"""
        # Arrange
        search_term = "laptop"
        mock_product_infos = [
            self.create_mock_product_info(1, "Laptop Pro 15", description="High-performance laptop")
        ]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_product_infos

        # Act
        result = self.repository.search_product_info_by_description(search_term)

        # Assert
        assert result == mock_product_infos
        assert len(result) == 1
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_info_by_parent_category_success(self):
        """Test get_product_info_by_parent_category returns product info for specified parent category"""
        # Arrange
        parent_category_id = 1
        mock_product_infos = [
            self.create_mock_product_info(2, "Wireless Mouse", category_name="Computer Accessories", parent_category_id=1),
            self.create_mock_product_info(3, "Monitor 24 inch", category_name="Monitors", parent_category_id=1)
        ]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_product_infos

        # Act
        result = self.repository.get_product_info_by_parent_category(parent_category_id)

        # Assert
        assert result == mock_product_infos
        assert len(result) == 2
        for product_info in result:
            assert product_info.parent_category_id == parent_category_id
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_info_without_category_success(self):
        """Test get_product_info_without_category returns product info without category"""
        # Arrange
        mock_product_infos = [
            self.create_mock_product_info(12, "Uncategorized Product", category_id=None, category_name=None)
        ]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_product_infos

        # Act
        result = self.repository.get_product_info_without_category()

        # Assert
        assert result == mock_product_infos
        assert len(result) == 1
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_info_sorted_by_price_ascending(self):
        """Test get_product_info_sorted_by_price returns product info sorted by price ascending"""
        # Arrange
        mock_product_infos = [
            self.create_mock_product_info(2, "Wireless Mouse", 29.99),
            self.create_mock_product_info(3, "Monitor 24 inch", 349.99),
            self.create_mock_product_info(1, "Laptop Pro 15", 1299.99)
        ]
        mock_order_by = Mock()
        self.mock_db_session.query.return_value.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = mock_product_infos

        # Act
        result = self.repository.get_product_info_sorted_by_price(ascending=True)

        # Assert
        assert result == mock_product_infos
        assert len(result) == 3
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_info_sorted_by_price_descending(self):
        """Test get_product_info_sorted_by_price returns product info sorted by price descending"""
        # Arrange
        mock_product_infos = [
            self.create_mock_product_info(1, "Laptop Pro 15", 1299.99),
            self.create_mock_product_info(3, "Monitor 24 inch", 349.99),
            self.create_mock_product_info(2, "Wireless Mouse", 29.99)
        ]
        mock_order_by = Mock()
        self.mock_db_session.query.return_value.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = mock_product_infos

        # Act
        result = self.repository.get_product_info_sorted_by_price(ascending=False)

        # Assert
        assert result == mock_product_infos
        assert len(result) == 3
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_info_sorted_by_stock_ascending(self):
        """Test get_product_info_sorted_by_stock returns product info sorted by stock ascending"""
        # Arrange
        mock_product_infos = [
            self.create_mock_product_info(1, "Laptop Pro 15", stock_quantity=10),
            self.create_mock_product_info(3, "Monitor 24 inch", stock_quantity=15),
            self.create_mock_product_info(2, "Wireless Mouse", stock_quantity=50)
        ]
        mock_order_by = Mock()
        self.mock_db_session.query.return_value.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = mock_product_infos

        # Act
        result = self.repository.get_product_info_sorted_by_stock(ascending=True)

        # Assert
        assert result == mock_product_infos
        assert len(result) == 3
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_info_sorted_by_name_ascending(self):
        """Test get_product_info_sorted_by_name returns product info sorted by name ascending"""
        # Arrange
        mock_product_infos = [
            self.create_mock_product_info(1, "Laptop Pro 15"),
            self.create_mock_product_info(3, "Monitor 24 inch"),
            self.create_mock_product_info(2, "Wireless Mouse")
        ]
        mock_order_by = Mock()
        self.mock_db_session.query.return_value.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = mock_product_infos

        # Act
        result = self.repository.get_product_info_sorted_by_name(ascending=True)

        # Assert
        assert result == mock_product_infos
        assert len(result) == 3
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_info_count_by_category_success(self):
        """Test get_product_info_count_by_category returns category count tuples"""
        # Arrange
        mock_count_results = [
            ("Electronics", 5),
            ("Computer Accessories", 3),
            ("Office Supplies", 2)
        ]
        mock_group_by = Mock()
        self.mock_db_session.query.return_value.group_by.return_value = mock_group_by
        mock_group_by.all.return_value = mock_count_results

        # Act
        result = self.repository.get_product_info_count_by_category()

        # Assert
        assert result == mock_count_results
        assert len(result) == 3
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_post_init_method(self):
        """Test that __post_init__ method can be called without errors"""
        # Act & Assert - should not raise any exceptions
        self.repository.__post_init__()

    def test_db_session_called_for_all_methods(self):
        """Test that db_session.get_session() is called for all methods with test2 parameter"""
        # Setup mocks
        self.mock_db_session.query.return_value.all.return_value = []
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = []
        mock_order_by = Mock()
        self.mock_db_session.query.return_value.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = []
        mock_group_by = Mock()
        self.mock_db_session.query.return_value.group_by.return_value = mock_group_by
        mock_group_by.all.return_value = []

        # Call all methods
        self.repository.get_all_product_info()
        self.repository.get_product_info_by_id(1)
        self.repository.get_product_info_by_name("Test")
        self.repository.get_product_info_by_category(1)
        self.repository.get_product_info_by_category_name("Electronics")
        self.repository.get_product_info_by_price_range(10.0, 100.0)
        self.repository.get_product_info_in_stock()
        self.repository.get_product_info_out_of_stock()
        self.repository.search_product_info_by_name("Test")
        self.repository.search_product_info_by_description("Test")
        self.repository.get_product_info_by_parent_category(1)
        self.repository.get_product_info_without_category()
        self.repository.get_product_info_sorted_by_price(True)
        self.repository.get_product_info_sorted_by_stock(True)
        self.repository.get_product_info_sorted_by_name(True)
        self.repository.get_product_info_count_by_category()

        # Assert session methods were called directly
        # Query should be called for all read operations (17 times)
        assert self.mock_db_session.query.call_count == 17


if __name__ == "__main__":
    pytest.main([__file__])
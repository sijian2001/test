import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List, Optional
import sys
import os

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from domain.repository.test2.product_repository import ProductRepository
from domain.model.test2.product import Product
from sqlalchemy.orm import Session


class TestProductRepository:
    """Unit tests for ProductRepository class"""

    def setup_method(self):
        """Setup method called before each test"""
        # Create a mock Session (since Test2DatabaseSession now inherits from Session)
        self.mock_db_session = Mock(spec=Session)

        # Create ProductRepository instance with mocked dependencies
        self.repository = ProductRepository(db_session=self.mock_db_session)

    def create_mock_product(self, product_id: int, product_name: str, price: float = 99.99,
                          stock_quantity: int = 10, category_id: int = 1, description: str = None) -> Product:
        """Helper method to create mock Product objects"""
        product = Mock(spec=Product)
        product.product_id = product_id
        product.product_name = product_name
        product.description = description or f"Description for {product_name}"
        product.price = price
        product.stock_quantity = stock_quantity
        product.category_id = category_id
        product.created_at = "2025-09-17 17:47:03"
        product.updated_at = "2025-09-17 17:47:03"
        return product

    def test_get_all_products_success(self):
        """Test get_all_products returns all products"""
        # Arrange
        mock_products = [
            self.create_mock_product(1, "Laptop Pro 15", 1299.99, 10, 1),
            self.create_mock_product(2, "Wireless Mouse", 29.99, 50, 2),
            self.create_mock_product(3, "Monitor 24 inch", 349.99, 15, 3)
        ]
        self.mock_db_session.query.return_value.all.return_value = mock_products

        # Act
        result = self.repository.get_all_products()

        # Assert
        assert result == mock_products
        assert len(result) == 3
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()
        self.mock_db_session.query.assert_called_with(Product)
        self.mock_db_session.query.return_value.all.assert_called_once()

    def test_get_all_products_empty_result(self):
        """Test get_all_products returns empty list when no products found"""
        # Arrange
        self.mock_db_session.query.return_value.all.return_value = []

        # Act
        result = self.repository.get_all_products()

        # Assert
        assert result == []
        assert len(result) == 0
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_by_id_success(self):
        """Test get_product_by_id returns product when found"""
        # Arrange
        product_id = 1
        mock_product = self.create_mock_product(1, "Laptop Pro 15")
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_product

        # Act
        result = self.repository.get_product_by_id(product_id)

        # Assert
        assert result == mock_product
        assert result.product_id == product_id
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()
        self.mock_db_session.query.assert_called_with(Product)

    def test_get_product_by_id_not_found(self):
        """Test get_product_by_id returns None when product not found"""
        # Arrange
        product_id = 999
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.repository.get_product_by_id(product_id)

        # Assert
        assert result is None
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_by_name_success(self):
        """Test get_product_by_name returns product when found"""
        # Arrange
        product_name = "Laptop Pro 15"
        mock_product = self.create_mock_product(1, product_name)
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_product

        # Act
        result = self.repository.get_product_by_name(product_name)

        # Assert
        assert result == mock_product
        assert result.product_name == product_name
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_product_by_name_not_found(self):
        """Test get_product_by_name returns None when product not found"""
        # Arrange
        product_name = "NonexistentProduct"
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.repository.get_product_by_name(product_name)

        # Assert
        assert result is None
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_products_by_category_success(self):
        """Test get_products_by_category returns products for specified category"""
        # Arrange
        category_id = 1
        mock_products = [
            self.create_mock_product(1, "Laptop Pro 15", category_id=1),
            self.create_mock_product(7, "Smartphone Pro", category_id=1)
        ]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_products

        # Act
        result = self.repository.get_products_by_category(category_id)

        # Assert
        assert result == mock_products
        assert len(result) == 2
        for product in result:
            assert product.category_id == category_id
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_products_by_category_empty_result(self):
        """Test get_products_by_category returns empty list when no products found"""
        # Arrange
        category_id = 999
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = []

        # Act
        result = self.repository.get_products_by_category(category_id)

        # Assert
        assert result == []
        assert len(result) == 0
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_products_by_price_range_success(self):
        """Test get_products_by_price_range returns products within price range"""
        # Arrange
        min_price = 100.0
        max_price = 500.0
        mock_products = [
            self.create_mock_product(3, "Monitor 24 inch", 349.99),
            self.create_mock_product(10, "External SSD 1TB", 149.99)
        ]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_products

        # Act
        result = self.repository.get_products_by_price_range(min_price, max_price)

        # Assert
        assert result == mock_products
        assert len(result) == 2
        for product in result:
            assert min_price <= product.price <= max_price
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_products_in_stock_success(self):
        """Test get_products_in_stock returns products with stock > 0"""
        # Arrange
        mock_products = [
            self.create_mock_product(1, "Laptop Pro 15", stock_quantity=10),
            self.create_mock_product(2, "Wireless Mouse", stock_quantity=50)
        ]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_products

        # Act
        result = self.repository.get_products_in_stock()

        # Assert
        assert result == mock_products
        assert len(result) == 2
        for product in result:
            assert product.stock_quantity > 0
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_products_out_of_stock_success(self):
        """Test get_products_out_of_stock returns products with stock <= 0"""
        # Arrange
        mock_products = [
            self.create_mock_product(11, "Out of Stock Product", stock_quantity=0)
        ]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_products

        # Act
        result = self.repository.get_products_out_of_stock()

        # Assert
        assert result == mock_products
        assert len(result) == 1
        for product in result:
            assert product.stock_quantity <= 0
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_search_products_by_name_success(self):
        """Test search_products_by_name returns products matching search term"""
        # Arrange
        search_term = "Pro"
        mock_products = [
            self.create_mock_product(1, "Laptop Pro 15"),
            self.create_mock_product(7, "Smartphone Pro")
        ]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_products

        # Act
        result = self.repository.search_products_by_name(search_term)

        # Assert
        assert result == mock_products
        assert len(result) == 2
        for product in result:
            assert search_term in product.product_name
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_create_product_success(self):
        """Test create_product creates new product successfully"""
        # Arrange
        mock_product = self.create_mock_product(12, "New Product", 199.99, 25, 1)

        # Mock session.add, commit, refresh
        self.mock_db_session.add = Mock()
        self.mock_db_session.commit = Mock()
        self.mock_db_session.refresh = Mock()

        # Act
        result = self.repository.create_product(mock_product)

        # Assert
        assert result == mock_product
        self.mock_db_session.add.assert_called_once_with(mock_product)
        self.mock_db_session.commit.assert_called_once()
        self.mock_db_session.refresh.assert_called_once_with(mock_product)

    def test_update_product_success(self):
        """Test update_product updates existing product successfully"""
        # Arrange
        mock_product = self.create_mock_product(1, "Updated Product", 299.99, 15, 1)

        # Mock session.merge, commit
        self.mock_db_session.merge = Mock(return_value=mock_product)
        self.mock_db_session.commit = Mock()

        # Act
        result = self.repository.update_product(mock_product)

        # Assert
        assert result == mock_product
        self.mock_db_session.merge.assert_called_once_with(mock_product)
        self.mock_db_session.commit.assert_called_once()

    def test_update_stock_quantity_success(self):
        """Test update_stock_quantity updates stock successfully"""
        # Arrange
        product_id = 1
        new_quantity = 25
        mock_product = self.create_mock_product(product_id, "Test Product", stock_quantity=10)

        # Mock get_product_by_id to return the product
        with patch.object(self.repository, 'get_product_by_id', return_value=mock_product):
            self.mock_db_session.commit = Mock()

            # Act
            result = self.repository.update_stock_quantity(product_id, new_quantity)

            # Assert
            assert result is True
            assert mock_product.stock_quantity == new_quantity
            self.mock_db_session.commit.assert_called_once()

    def test_update_stock_quantity_product_not_found(self):
        """Test update_stock_quantity returns False when product not found"""
        # Arrange
        product_id = 999
        new_quantity = 25

        # Mock get_product_by_id to return None
        with patch.object(self.repository, 'get_product_by_id', return_value=None):
            # Act
            result = self.repository.update_stock_quantity(product_id, new_quantity)

            # Assert
            assert result is False

    def test_delete_product_success(self):
        """Test delete_product deletes existing product successfully"""
        # Arrange
        product_id = 1
        mock_product = self.create_mock_product(product_id, "Product to Delete")

        # Mock get_product_by_id to return the product
        with patch.object(self.repository, 'get_product_by_id', return_value=mock_product):
            self.mock_db_session.delete = Mock()
            self.mock_db_session.commit = Mock()

            # Act
            result = self.repository.delete_product(product_id)

            # Assert
            assert result is True
            self.mock_db_session.delete.assert_called_once_with(mock_product)
            self.mock_db_session.commit.assert_called_once()

    def test_delete_product_not_found(self):
        """Test delete_product returns False when product not found"""
        # Arrange
        product_id = 999

        # Mock get_product_by_id to return None
        with patch.object(self.repository, 'get_product_by_id', return_value=None):
            # Act
            result = self.repository.delete_product(product_id)

            # Assert
            assert result is False

    def test_post_init_method(self):
        """Test that __post_init__ method can be called without errors"""
        # Act & Assert - should not raise any exceptions
        self.repository.__post_init__()

    def test_db_session_called_for_all_methods(self):
        """Test that db_session is used directly for all methods"""
        # Setup mocks
        self.mock_db_session.query.return_value.all.return_value = []
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = []
        self.mock_db_session.add = Mock()
        self.mock_db_session.commit = Mock()
        self.mock_db_session.refresh = Mock()
        self.mock_db_session.merge = Mock()
        self.mock_db_session.delete = Mock()

        mock_product = self.create_mock_product(1, "Test")

        # Call all methods
        self.repository.get_all_products()
        self.repository.get_product_by_id(1)
        self.repository.get_product_by_name("Test")
        self.repository.get_products_by_category(1)
        self.repository.get_products_by_price_range(10.0, 100.0)
        self.repository.get_products_in_stock()
        self.repository.get_products_out_of_stock()
        self.repository.search_products_by_name("Test")
        self.repository.create_product(mock_product)
        self.repository.update_product(mock_product)

        with patch.object(self.repository, 'get_product_by_id', return_value=mock_product):
            self.repository.update_stock_quantity(1, 25)
            self.repository.delete_product(1)

        # Assert session methods were called directly
        # Query should be called for read operations
        assert self.mock_db_session.query.call_count >= 8  # At least 8 read operations
        # Add, commit should be called for write operations
        self.mock_db_session.add.assert_called()
        self.mock_db_session.commit.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List, Optional
import sys
import os

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from business.product_info_service import ProductInfoService, ProductInfoSearchInDto, ProductInfoOutDto
from domain.repository.test2.product_info_repository import ProductInfoRepository
from domain.model.test2.product_info import ProductInfo


class TestProductInfoService:
    """Unit tests for ProductInfoService class"""

    def setup_method(self):
        """Setup method called before each test"""
        # Create a mock ProductInfoRepository
        self.mock_repository = Mock(spec=ProductInfoRepository)

        # Create ProductInfoService instance with mocked dependencies
        self.service = ProductInfoService(product_info_repository=self.mock_repository)

    def create_mock_product_info(self, product_id: int, product_name: str, price: float = 99.99,
                                stock_quantity: int = 10, category_id: int = 1, category_name: str = "Electronics") -> ProductInfo:
        """Helper method to create mock ProductInfo objects"""
        product_info = Mock(spec=ProductInfo)
        product_info.product_id = product_id
        product_info.product_name = product_name
        product_info.description = f"Description for {product_name}"
        product_info.price = price
        product_info.stock_quantity = stock_quantity
        product_info.category_id = category_id
        product_info.category_name = category_name
        product_info.category_description = f"Description for {category_name}"
        product_info.parent_category_id = None
        product_info.created_at = "2025-09-17 17:47:03"
        product_info.updated_at = "2025-09-17 17:47:03"
        return product_info

    def test_get_all_product_info_success(self):
        """Test get_all_product_info returns all product info with correct count"""
        # Arrange
        mock_product_info_list = [
            self.create_mock_product_info(1, "Laptop Pro 15", 1299.99, 10, 1, "Electronics"),
            self.create_mock_product_info(2, "Wireless Mouse", 29.99, 50, 2, "Computer Accessories"),
            self.create_mock_product_info(3, "Monitor 24 inch", 349.99, 15, 3, "Monitors")
        ]
        self.mock_repository.get_all_product_info.return_value = mock_product_info_list

        # Act
        result = self.service.get_all_product_info()

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert result.product_info_list == mock_product_info_list
        assert result.total_count == 3
        self.mock_repository.get_all_product_info.assert_called_once()

    def test_get_all_product_info_empty_result(self):
        """Test get_all_product_info returns empty result with zero count"""
        # Arrange
        self.mock_repository.get_all_product_info.return_value = []

        # Act
        result = self.service.get_all_product_info()

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert result.product_info_list == []
        assert result.total_count == 0
        self.mock_repository.get_all_product_info.assert_called_once()

    def test_search_product_info_by_product_id_success(self):
        """Test search_product_info by product_id returns correct result"""
        # Arrange
        product_id = 1
        mock_product_info = self.create_mock_product_info(1, "Laptop Pro 15", 1299.99, 10, 1, "Electronics")
        self.mock_repository.get_product_info_by_id.return_value = mock_product_info
        search_dto = ProductInfoSearchInDto(product_id=product_id)

        # Act
        result = self.service.search_product_info(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert len(result.product_info_list) == 1
        assert result.product_info_list[0] == mock_product_info
        assert result.total_count == 1
        self.mock_repository.get_product_info_by_id.assert_called_once_with(product_id)

    def test_search_product_info_by_product_id_not_found(self):
        """Test search_product_info by product_id when product not found"""
        # Arrange
        product_id = 999
        self.mock_repository.get_product_info_by_id.return_value = None
        search_dto = ProductInfoSearchInDto(product_id=product_id)

        # Act
        result = self.service.search_product_info(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert result.product_info_list == []
        assert result.total_count == 0
        self.mock_repository.get_product_info_by_id.assert_called_once_with(product_id)

    def test_search_product_info_by_product_name_success(self):
        """Test search_product_info by product_name returns correct result"""
        # Arrange
        product_name = "Laptop Pro 15"
        mock_product_info = self.create_mock_product_info(1, product_name, 1299.99, 10, 1, "Electronics")
        self.mock_repository.get_product_info_by_name.return_value = mock_product_info
        search_dto = ProductInfoSearchInDto(product_name=product_name)

        # Act
        result = self.service.search_product_info(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert len(result.product_info_list) == 1
        assert result.product_info_list[0] == mock_product_info
        assert result.total_count == 1
        self.mock_repository.get_product_info_by_name.assert_called_once_with(product_name)

    def test_search_product_info_by_category_id_success(self):
        """Test search_product_info by category_id returns correct result"""
        # Arrange
        category_id = 1
        mock_product_info_list = [
            self.create_mock_product_info(1, "Laptop Pro 15", category_id=1, category_name="Electronics"),
            self.create_mock_product_info(7, "Smartphone Pro", category_id=1, category_name="Electronics")
        ]
        self.mock_repository.get_product_info_by_category.return_value = mock_product_info_list
        search_dto = ProductInfoSearchInDto(category_id=category_id)

        # Act
        result = self.service.search_product_info(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert result.product_info_list == mock_product_info_list
        assert result.total_count == 2
        self.mock_repository.get_product_info_by_category.assert_called_once_with(category_id)

    def test_search_product_info_by_category_name_success(self):
        """Test search_product_info by category_name returns correct result"""
        # Arrange
        category_name = "Electronics"
        mock_product_info_list = [
            self.create_mock_product_info(1, "Laptop Pro 15", category_name="Electronics"),
            self.create_mock_product_info(7, "Smartphone Pro", category_name="Electronics")
        ]
        self.mock_repository.get_product_info_by_category_name.return_value = mock_product_info_list
        search_dto = ProductInfoSearchInDto(category_name=category_name)

        # Act
        result = self.service.search_product_info(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert result.product_info_list == mock_product_info_list
        assert result.total_count == 2
        self.mock_repository.get_product_info_by_category_name.assert_called_once_with(category_name)

    def test_search_product_info_by_price_range_success(self):
        """Test search_product_info by price range returns correct result"""
        # Arrange
        min_price = 100.0
        max_price = 500.0
        mock_product_info_list = [
            self.create_mock_product_info(3, "Monitor 24 inch", 349.99),
            self.create_mock_product_info(10, "External SSD 1TB", 149.99)
        ]
        self.mock_repository.get_product_info_by_price_range.return_value = mock_product_info_list
        search_dto = ProductInfoSearchInDto(min_price=min_price, max_price=max_price)

        # Act
        result = self.service.search_product_info(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert result.product_info_list == mock_product_info_list
        assert result.total_count == 2
        self.mock_repository.get_product_info_by_price_range.assert_called_once_with(min_price, max_price)

    def test_search_product_info_by_price_range_min_only(self):
        """Test search_product_info with only min_price sets max_price default"""
        # Arrange
        min_price = 100.0
        mock_product_info_list = [self.create_mock_product_info(1, "Laptop Pro 15", 1299.99)]
        self.mock_repository.get_product_info_by_price_range.return_value = mock_product_info_list
        search_dto = ProductInfoSearchInDto(min_price=min_price)

        # Act
        result = self.service.search_product_info(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        self.mock_repository.get_product_info_by_price_range.assert_called_once_with(min_price, 999999.99)

    def test_search_product_info_by_search_term_success(self):
        """Test search_product_info by search_term combines name and description results"""
        # Arrange
        search_term = "Pro"
        name_results = [self.create_mock_product_info(1, "Laptop Pro 15")]
        desc_results = [self.create_mock_product_info(7, "Smartphone Pro")]
        self.mock_repository.search_product_info_by_name.return_value = name_results
        self.mock_repository.search_product_info_by_description.return_value = desc_results
        search_dto = ProductInfoSearchInDto(search_term=search_term)

        # Act
        result = self.service.search_product_info(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert result.total_count == 2
        self.mock_repository.search_product_info_by_name.assert_called_once_with(search_term)
        self.mock_repository.search_product_info_by_description.assert_called_once_with(search_term)

    def test_search_product_info_by_search_term_with_duplicates(self):
        """Test search_product_info by search_term deduplicates results"""
        # Arrange
        search_term = "Pro"
        duplicate_product = self.create_mock_product_info(1, "Laptop Pro 15")
        name_results = [duplicate_product]
        desc_results = [duplicate_product]  # Same product returned from both searches
        self.mock_repository.search_product_info_by_name.return_value = name_results
        self.mock_repository.search_product_info_by_description.return_value = desc_results
        search_dto = ProductInfoSearchInDto(search_term=search_term)

        # Act
        result = self.service.search_product_info(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert result.total_count == 1  # Deduplicated to 1 product

    def test_search_product_info_in_stock_only_true(self):
        """Test search_product_info with in_stock_only=True"""
        # Arrange
        mock_product_info_list = [
            self.create_mock_product_info(1, "Laptop Pro 15", stock_quantity=10),
            self.create_mock_product_info(2, "Wireless Mouse", stock_quantity=50)
        ]
        self.mock_repository.get_product_info_in_stock.return_value = mock_product_info_list
        search_dto = ProductInfoSearchInDto(in_stock_only=True)

        # Act
        result = self.service.search_product_info(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert result.product_info_list == mock_product_info_list
        assert result.total_count == 2
        self.mock_repository.get_product_info_in_stock.assert_called_once()

    def test_search_product_info_in_stock_only_false(self):
        """Test search_product_info with in_stock_only=False"""
        # Arrange
        mock_product_info_list = [
            self.create_mock_product_info(11, "Out of Stock Product", stock_quantity=0)
        ]
        self.mock_repository.get_product_info_out_of_stock.return_value = mock_product_info_list
        search_dto = ProductInfoSearchInDto(in_stock_only=False)

        # Act
        result = self.service.search_product_info(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert result.product_info_list == mock_product_info_list
        assert result.total_count == 1
        self.mock_repository.get_product_info_out_of_stock.assert_called_once()

    def test_search_product_info_no_criteria_calls_get_all(self):
        """Test search_product_info with no criteria falls back to get_all_product_info"""
        # Arrange
        mock_product_info_list = [
            self.create_mock_product_info(1, "Laptop Pro 15"),
            self.create_mock_product_info(2, "Wireless Mouse")
        ]
        self.mock_repository.get_all_product_info.return_value = mock_product_info_list
        search_dto = ProductInfoSearchInDto()  # No search criteria

        # Act
        result = self.service.search_product_info(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert result.product_info_list == mock_product_info_list
        assert result.total_count == 2
        self.mock_repository.get_all_product_info.assert_called_once()

    def test_search_product_info_with_sorting_price_asc(self):
        """Test search_product_info applies price sorting ascending"""
        # Arrange
        mock_product_info_list = [
            self.create_mock_product_info(1, "Laptop Pro 15", 1299.99),
            self.create_mock_product_info(2, "Wireless Mouse", 29.99)
        ]
        self.mock_repository.get_all_product_info.return_value = mock_product_info_list
        search_dto = ProductInfoSearchInDto(sort_by="price", sort_order="asc")

        # Act
        result = self.service.search_product_info(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert result.total_count == 2
        # Verify sorting was applied (cheaper item first)
        assert result.product_info_list[0].price == 29.99
        assert result.product_info_list[1].price == 1299.99

    def test_search_product_info_with_sorting_price_desc(self):
        """Test search_product_info applies price sorting descending"""
        # Arrange
        mock_product_info_list = [
            self.create_mock_product_info(2, "Wireless Mouse", 29.99),
            self.create_mock_product_info(1, "Laptop Pro 15", 1299.99)
        ]
        self.mock_repository.get_all_product_info.return_value = mock_product_info_list
        search_dto = ProductInfoSearchInDto(sort_by="price", sort_order="desc")

        # Act
        result = self.service.search_product_info(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert result.total_count == 2
        # Verify sorting was applied (expensive item first)
        assert result.product_info_list[0].price == 1299.99
        assert result.product_info_list[1].price == 29.99

    def test_search_product_info_priority_product_id_over_product_name(self):
        """Test search_product_info prioritizes product_id over product_name when both provided"""
        # Arrange
        product_id = 1
        product_name = "Laptop Pro 15"
        mock_product_info = self.create_mock_product_info(1, "Laptop Pro 15")
        self.mock_repository.get_product_info_by_id.return_value = mock_product_info
        search_dto = ProductInfoSearchInDto(product_id=product_id, product_name=product_name)

        # Act
        result = self.service.search_product_info(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert len(result.product_info_list) == 1
        assert result.total_count == 1
        self.mock_repository.get_product_info_by_id.assert_called_once_with(product_id)
        self.mock_repository.get_product_info_by_name.assert_not_called()

    def test_execute_delegates_to_search_product_info(self):
        """Test execute method delegates to search_product_info"""
        # Arrange
        product_name = "Laptop Pro 15"
        mock_product_info = self.create_mock_product_info(1, product_name)
        self.mock_repository.get_product_info_by_name.return_value = mock_product_info
        search_dto = ProductInfoSearchInDto(product_name=product_name)

        # Act
        result = self.service.execute(search_dto)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert len(result.product_info_list) == 1
        assert result.total_count == 1
        self.mock_repository.get_product_info_by_name.assert_called_once_with(product_name)

    def test_get_product_info_by_category_tree_success(self):
        """Test get_product_info_by_category_tree returns products for parent category"""
        # Arrange
        parent_category_id = 1
        mock_product_info_list = [
            self.create_mock_product_info(2, "Wireless Mouse", category_name="Computer Accessories"),
            self.create_mock_product_info(3, "Monitor 24 inch", category_name="Monitors")
        ]
        self.mock_repository.get_product_info_by_parent_category.return_value = mock_product_info_list

        # Act
        result = self.service.get_product_info_by_category_tree(parent_category_id)

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert result.product_info_list == mock_product_info_list
        assert result.total_count == 2
        self.mock_repository.get_product_info_by_parent_category.assert_called_once_with(parent_category_id)

    def test_get_uncategorized_products_success(self):
        """Test get_uncategorized_products returns products without category"""
        # Arrange
        mock_product_info_list = [
            self.create_mock_product_info(12, "Uncategorized Product", category_id=None, category_name=None)
        ]
        self.mock_repository.get_product_info_without_category.return_value = mock_product_info_list

        # Act
        result = self.service.get_uncategorized_products()

        # Assert
        assert isinstance(result, ProductInfoOutDto)
        assert result.product_info_list == mock_product_info_list
        assert result.total_count == 1
        self.mock_repository.get_product_info_without_category.assert_called_once()

    def test_get_product_statistics_by_category_success(self):
        """Test get_product_statistics_by_category returns category statistics"""
        # Arrange
        mock_category_stats = [
            ("Electronics", 5),
            ("Computer Accessories", 3),
            ("Office Supplies", 2)
        ]
        self.mock_repository.get_product_info_count_by_category.return_value = mock_category_stats

        # Act
        result = self.service.get_product_statistics_by_category()

        # Assert
        assert isinstance(result, dict)
        assert result["Electronics"] == 5
        assert result["Computer Accessories"] == 3
        assert result["Office Supplies"] == 2
        assert len(result) == 3
        self.mock_repository.get_product_info_count_by_category.assert_called_once()

    def test_post_init_method(self):
        """Test that __post_init__ method initializes logger correctly"""
        # Act & Assert - should not raise any exceptions
        self.service.__post_init__()
        assert hasattr(self.service, 'logger')

    @patch('business.product_info_service.logging.getLogger')
    def test_logging_calls(self, mock_get_logger):
        """Test that appropriate logging calls are made"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        self.service.__post_init__()
        self.mock_repository.get_all_product_info.return_value = []

        # Act
        self.service.get_all_product_info()

        # Assert
        mock_logger.info.assert_called()
        assert mock_logger.info.call_count >= 3  # At least start, count, and end log messages

    def test_deduplicate_product_info_list(self):
        """Test _deduplicate_product_info_list removes duplicates based on product_id"""
        # Arrange
        product1 = self.create_mock_product_info(1, "Product 1")
        product2 = self.create_mock_product_info(2, "Product 2")
        product1_duplicate = self.create_mock_product_info(1, "Product 1 Duplicate")
        product_list = [product1, product2, product1_duplicate]

        # Act
        result = self.service._deduplicate_product_info_list(product_list)

        # Assert
        assert len(result) == 2
        assert result[0].product_id == 1
        assert result[1].product_id == 2

    def test_apply_sorting_by_name(self):
        """Test _apply_sorting sorts by product name"""
        # Arrange
        product_a = self.create_mock_product_info(1, "A Product")
        product_z = self.create_mock_product_info(2, "Z Product")
        product_list = [product_z, product_a]

        # Act
        result = self.service._apply_sorting(product_list, "name", "asc")

        # Assert
        assert len(result) == 2
        assert result[0].product_name == "A Product"
        assert result[1].product_name == "Z Product"

    def test_apply_sorting_unknown_sort_by(self):
        """Test _apply_sorting returns unsorted list for unknown sort_by"""
        # Arrange
        product_list = [self.create_mock_product_info(1, "Product 1")]

        # Act
        result = self.service._apply_sorting(product_list, "unknown", "asc")

        # Assert
        assert result == product_list


if __name__ == "__main__":
    pytest.main([__file__])
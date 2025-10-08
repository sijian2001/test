import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List
import sys
import os

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.business.category_regist_service import CategoryRegistService, CategoryRegistInDto, CategoryRegistOutDto
from app.domain.repository.test2.category_repository import CategoryRepository
from app.domain.model.test2.category import Category
from app.business.vo.category_vo import CategoryVo
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


class TestCategoryRegistService:
    """Unit tests for CategoryRegistService class"""

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

        # Create a mock CategoryRepository
        self.mock_repository = Mock(spec=CategoryRepository)

        # Create CategoryRegistService instance with mocked dependencies
        self.service = CategoryRegistService(category_repository=self.mock_repository)

    def teardown_method(self):
        """Teardown method called after each test"""
        SessionHolder.clear()

    def create_category_vo(self, category_name: str, category_description: str = None, parent_category_id: int = None) -> CategoryVo:
        """Helper method to create CategoryVo objects"""
        return CategoryVo(
            category_name=category_name,
            category_description=category_description or f"Description for {category_name}",
            parent_category_id=parent_category_id
        )

    def test_execute_single_category_success(self):
        """Test execute with single category registration success"""
        # Arrange
        category_vo = self.create_category_vo("Electronics", "Electronic devices and gadgets")
        in_dto = CategoryRegistInDto(categoryList=[category_vo])

        # Mock repository to return successfully created category
        mock_category = Mock(spec=Category)
        self.mock_repository.create_category.return_value = mock_category

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, CategoryRegistOutDto)
        assert result.categoryCount == 1
        self.mock_repository.create_category.assert_called_once()

        # Verify the Category object was created with correct parameters
        call_args = self.mock_repository.create_category.call_args[0][0]
        assert call_args.category_name == "Electronics"
        assert call_args.category_description == "Electronic devices and gadgets"
        assert call_args.parent_category_id is None

    def test_execute_multiple_categories_success(self):
        """Test execute with multiple categories registration success"""
        # Arrange
        category_vo_list = [
            self.create_category_vo("Electronics", "Electronic devices"),
            self.create_category_vo("Computer Accessories", "Accessories for computers", 1),
            self.create_category_vo("Office Supplies", "General office supplies")
        ]
        in_dto = CategoryRegistInDto(categoryList=category_vo_list)

        # Mock repository to return successfully created categories
        mock_category = Mock(spec=Category)
        self.mock_repository.create_category.return_value = mock_category

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, CategoryRegistOutDto)
        assert result.categoryCount == 3
        assert self.mock_repository.create_category.call_count == 3

        # Verify each category was created with correct parameters
        call_args_list = self.mock_repository.create_category.call_args_list

        # First category
        first_call = call_args_list[0][0][0]
        assert first_call.category_name == "Electronics"
        assert first_call.category_description == "Electronic devices"
        assert first_call.parent_category_id is None

        # Second category (with parent)
        second_call = call_args_list[1][0][0]
        assert second_call.category_name == "Computer Accessories"
        assert second_call.category_description == "Accessories for computers"
        assert second_call.parent_category_id == 1

        # Third category
        third_call = call_args_list[2][0][0]
        assert third_call.category_name == "Office Supplies"
        assert third_call.category_description == "General office supplies"
        assert third_call.parent_category_id is None

    def test_execute_empty_category_list(self):
        """Test execute with empty category list"""
        # Arrange
        in_dto = CategoryRegistInDto(categoryList=[])

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, CategoryRegistOutDto)
        assert result.categoryCount == 0
        self.mock_repository.create_category.assert_not_called()

    def test_execute_category_with_none_description(self):
        """Test execute with category having None description"""
        # Arrange
        category_vo = CategoryVo(
            category_name="Test Category",
            category_description=None,
            parent_category_id=None
        )
        in_dto = CategoryRegistInDto(categoryList=[category_vo])

        # Mock repository
        mock_category = Mock(spec=Category)
        self.mock_repository.create_category.return_value = mock_category

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, CategoryRegistOutDto)
        assert result.categoryCount == 1

        # Verify the Category object was created with None description
        call_args = self.mock_repository.create_category.call_args[0][0]
        assert call_args.category_name == "Test Category"
        assert call_args.category_description is None
        assert call_args.parent_category_id is None

    def test_execute_category_repository_exception(self):
        """Test execute handles repository exceptions correctly"""
        # Arrange
        category_vo = self.create_category_vo("Test Category")
        in_dto = CategoryRegistInDto(categoryList=[category_vo])

        # Mock repository to raise exception
        self.mock_repository.create_category.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.execute(in_dto)

        assert str(exc_info.value) == "Database error"
        self.mock_repository.create_category.assert_called_once()

    def test_execute_partial_failure_with_multiple_categories(self):
        """Test execute with partial failure in multiple categories"""
        # Arrange
        category_vo_list = [
            self.create_category_vo("Electronics"),
            self.create_category_vo("Failing Category"),
            self.create_category_vo("Office Supplies")
        ]
        in_dto = CategoryRegistInDto(categoryList=category_vo_list)

        # Mock repository: first succeeds, second fails, third never called due to exception
        mock_category = Mock(spec=Category)
        self.mock_repository.create_category.side_effect = [
            mock_category,  # First call succeeds
            Exception("Database error"),  # Second call fails
        ]

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.execute(in_dto)

        assert str(exc_info.value) == "Database error"
        # Only first two categories should have been attempted
        assert self.mock_repository.create_category.call_count == 2

    def test_execute_with_hierarchical_categories(self):
        """Test execute with parent-child category relationships"""
        # Arrange
        category_vo_list = [
            self.create_category_vo("Electronics", "Root category", None),  # Parent
            self.create_category_vo("Computers", "Computer products", 1),   # Child of Electronics
            self.create_category_vo("Laptops", "Laptop computers", 2)       # Child of Computers
        ]
        in_dto = CategoryRegistInDto(categoryList=category_vo_list)

        # Mock repository
        mock_category = Mock(spec=Category)
        self.mock_repository.create_category.return_value = mock_category

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, CategoryRegistOutDto)
        assert result.categoryCount == 3
        assert self.mock_repository.create_category.call_count == 3

        # Verify hierarchy is preserved in the calls
        call_args_list = self.mock_repository.create_category.call_args_list

        # Parent category
        parent_call = call_args_list[0][0][0]
        assert parent_call.category_name == "Electronics"
        assert parent_call.parent_category_id is None

        # First child
        child1_call = call_args_list[1][0][0]
        assert child1_call.category_name == "Computers"
        assert child1_call.parent_category_id == 1

        # Second level child
        child2_call = call_args_list[2][0][0]
        assert child2_call.category_name == "Laptops"
        assert child2_call.parent_category_id == 2

    def test_post_init_method(self):
        """Test that __post_init__ method initializes logger correctly"""
        # Act & Assert - should not raise any exceptions
        self.service.__post_init__()
        assert hasattr(self.service, 'logger')

    @patch('app.business.category_regist_service.logging.getLogger')
    def test_logging_calls_success(self, mock_get_logger):
        """Test that appropriate logging calls are made for successful registration"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        self.service.__post_init__()

        category_vo = self.create_category_vo("Electronics")
        in_dto = CategoryRegistInDto(categoryList=[category_vo])

        mock_category = Mock(spec=Category)
        self.mock_repository.create_category.return_value = mock_category

        # Act
        self.service.execute(in_dto)

        # Assert
        mock_logger.info.assert_called()
        # Should have at least: start, per-category, count, and completion messages
        assert mock_logger.info.call_count >= 4

    @patch('app.business.category_regist_service.logging.getLogger')
    def test_logging_calls_failure(self, mock_get_logger):
        """Test that appropriate logging calls are made for failed registration"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        self.service.__post_init__()

        category_vo = self.create_category_vo("Failing Category")
        in_dto = CategoryRegistInDto(categoryList=[category_vo])

        # Mock repository to raise exception
        self.mock_repository.create_category.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            self.service.execute(in_dto)

        # Verify error logging was called
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        assert "Failed to register category Failing Category" in error_call_args
        assert "Database error" in error_call_args

    def test_category_entity_creation(self):
        """Test that Category entities are created correctly from CategoryVo objects"""
        # Arrange
        category_vo = CategoryVo(
            category_name="Test Category",
            category_description="Test Description",
            parent_category_id=5
        )
        in_dto = CategoryRegistInDto(categoryList=[category_vo])

        # Mock repository
        mock_category = Mock(spec=Category)
        self.mock_repository.create_category.return_value = mock_category

        # Act
        result = self.service.execute(in_dto)

        # Assert
        self.mock_repository.create_category.assert_called_once()

        # Get the Category object that was passed to create_category
        created_category = self.mock_repository.create_category.call_args[0][0]

        # Verify it's a Category instance (or at least has the expected attributes)
        assert hasattr(created_category, 'category_name')
        assert hasattr(created_category, 'category_description')
        assert hasattr(created_category, 'parent_category_id')

        # Verify the values were correctly transferred from VO to entity
        assert created_category.category_name == "Test Category"
        assert created_category.category_description == "Test Description"
        assert created_category.parent_category_id == 5

    def test_in_dto_validation(self):
        """Test that CategoryRegistInDto accepts the expected structure"""
        # Arrange
        category_vo_list = [
            self.create_category_vo("Category 1"),
            self.create_category_vo("Category 2")
        ]

        # Act
        in_dto = CategoryRegistInDto(categoryList=category_vo_list)

        # Assert
        assert isinstance(in_dto, CategoryRegistInDto)
        assert len(in_dto.categoryList) == 2
        assert in_dto.categoryList[0].category_name == "Category 1"
        assert in_dto.categoryList[1].category_name == "Category 2"

    def test_out_dto_structure(self):
        """Test that CategoryRegistOutDto has the expected structure"""
        # Act
        out_dto = CategoryRegistOutDto(categoryCount=5)

        # Assert
        assert isinstance(out_dto, CategoryRegistOutDto)
        assert out_dto.categoryCount == 5


if __name__ == "__main__":
    pytest.main([__file__])
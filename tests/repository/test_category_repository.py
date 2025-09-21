import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List, Optional
import sys
import os

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from domain.repository.test2.category_repository import CategoryRepository
from domain.model.test2.category import Category
from sqlalchemy.orm import Session


class TestCategoryRepository:
    """Unit tests for CategoryRepository class"""

    def setup_method(self):
        """Setup method called before each test"""
        # Create a mock Session (since Test2DatabaseSession now inherits from Session)
        self.mock_db_session = Mock(spec=Session)

        # Create CategoryRepository instance with mocked dependencies
        self.repository = CategoryRepository(db_session=self.mock_db_session)

    def create_mock_category(self, category_id: int, category_name: str,
                           category_description: str = None, parent_category_id: int = None) -> Category:
        """Helper method to create mock Category objects"""
        category = Mock(spec=Category)
        category.category_id = category_id
        category.category_name = category_name
        category.category_description = category_description or f"Description for {category_name}"
        category.parent_category_id = parent_category_id
        category.created_at = "2025-09-17 17:47:03"
        category.updated_at = "2025-09-17 17:47:03"
        return category

    def test_get_all_categories_success(self):
        """Test get_all_categories returns all categories"""
        # Arrange
        mock_categories = [
            self.create_mock_category(1, "Electronics", "Electronic devices"),
            self.create_mock_category(2, "Computer Accessories", "Accessories for computers", 1),
            self.create_mock_category(3, "Office Supplies", "General office supplies")
        ]
        self.mock_db_session.query.return_value.all.return_value = mock_categories

        # Act
        result = self.repository.get_all_categories()

        # Assert
        assert result == mock_categories
        assert len(result) == 3
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()
        self.mock_db_session.query.assert_called_with(Category)
        self.mock_db_session.query.return_value.all.assert_called_once()

    def test_get_all_categories_empty_result(self):
        """Test get_all_categories returns empty list when no categories found"""
        # Arrange
        self.mock_db_session.query.return_value.all.return_value = []

        # Act
        result = self.repository.get_all_categories()

        # Assert
        assert result == []
        assert len(result) == 0
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_category_by_id_success(self):
        """Test get_category_by_id returns category when found"""
        # Arrange
        category_id = 1
        mock_category = self.create_mock_category(1, "Electronics")
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_category

        # Act
        result = self.repository.get_category_by_id(category_id)

        # Assert
        assert result == mock_category
        assert result.category_id == category_id
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()
        self.mock_db_session.query.assert_called_once_with(Category)

    def test_get_category_by_id_not_found(self):
        """Test get_category_by_id returns None when category not found"""
        # Arrange
        category_id = 999
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.repository.get_category_by_id(category_id)

        # Assert
        assert result is None
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_category_by_name_success(self):
        """Test get_category_by_name returns category when found"""
        # Arrange
        category_name = "Electronics"
        mock_category = self.create_mock_category(1, category_name)
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_category

        # Act
        result = self.repository.get_category_by_name(category_name)

        # Assert
        assert result == mock_category
        assert result.category_name == category_name
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_category_by_name_not_found(self):
        """Test get_category_by_name returns None when category not found"""
        # Arrange
        category_name = "NonexistentCategory"
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.repository.get_category_by_name(category_name)

        # Assert
        assert result is None
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_categories_by_parent_success(self):
        """Test get_categories_by_parent returns categories with specified parent"""
        # Arrange
        parent_category_id = 1
        mock_categories = [
            self.create_mock_category(2, "Computer Accessories", parent_category_id=1),
            self.create_mock_category(3, "Monitors", parent_category_id=1)
        ]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_categories

        # Act
        result = self.repository.get_categories_by_parent(parent_category_id)

        # Assert
        assert result == mock_categories
        assert len(result) == 2
        for category in result:
            assert category.parent_category_id == parent_category_id
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_categories_by_parent_empty_result(self):
        """Test get_categories_by_parent returns empty list when no subcategories found"""
        # Arrange
        parent_category_id = 999
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = []

        # Act
        result = self.repository.get_categories_by_parent(parent_category_id)

        # Assert
        assert result == []
        assert len(result) == 0
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_categories_by_parent_none(self):
        """Test get_categories_by_parent with None parent_category_id"""
        # Arrange
        mock_categories = [self.create_mock_category(1, "Electronics")]
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = mock_categories

        # Act
        result = self.repository.get_categories_by_parent(None)

        # Assert
        assert result == mock_categories
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_root_categories_success(self):
        """Test get_root_categories returns categories with no parent"""
        # Arrange
        mock_categories = [
            self.create_mock_category(1, "Electronics"),
            self.create_mock_category(11, "Office Supplies")
        ]
        mock_filter = Mock()
        self.mock_db_session.query.return_value.filter.return_value = mock_filter
        mock_filter.all.return_value = mock_categories

        # Act
        result = self.repository.get_root_categories()

        # Assert
        assert result == mock_categories
        assert len(result) == 2
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_create_category_success(self):
        """Test create_category creates new category successfully"""
        # Arrange
        mock_category = self.create_mock_category(4, "New Category", "A new category")

        # Mock session.add, commit, refresh
        self.mock_db_session.add = Mock()
        self.mock_db_session.flush = Mock()
        self.mock_db_session.refresh = Mock()

        # Act
        result = self.repository.create_category(mock_category)

        # Assert
        assert result == mock_category
        self.mock_db_session.add.assert_called_once_with(mock_category)
        self.mock_db_session.flush.assert_called_once()
        self.mock_db_session.refresh.assert_called_once_with(mock_category)

    def test_update_category_success(self):
        """Test update_category updates existing category successfully"""
        # Arrange
        mock_category = self.create_mock_category(1, "Updated Category", "Updated description")

        # Mock session.merge, commit
        self.mock_db_session.merge = Mock(return_value=mock_category)
        self.mock_db_session.flush = Mock()

        # Act
        result = self.repository.update_category(mock_category)

        # Assert
        assert result == mock_category
        self.mock_db_session.merge.assert_called_once_with(mock_category)
        self.mock_db_session.flush.assert_called_once()

    def test_delete_category_success(self):
        """Test delete_category deletes existing category successfully"""
        # Arrange
        category_id = 1
        mock_category = self.create_mock_category(category_id, "Category to Delete")

        # Mock get_category_by_id to return the category
        with patch.object(self.repository, 'get_category_by_id', return_value=mock_category):
            self.mock_db_session.delete = Mock()
            self.mock_db_session.flush = Mock()

            # Act
            result = self.repository.delete_category(category_id)

            # Assert
            assert result is True
            self.mock_db_session.delete.assert_called_once_with(mock_category)
            self.mock_db_session.flush.assert_called_once()

    def test_delete_category_not_found(self):
        """Test delete_category returns False when category not found"""
        # Arrange
        category_id = 999

        # Mock get_category_by_id to return None
        with patch.object(self.repository, 'get_category_by_id', return_value=None):
            # Act
            result = self.repository.delete_category(category_id)

            # Assert
            assert result is False
            # delete and commit should not be called
            assert not hasattr(self.mock_db_session, 'delete') or not self.mock_db_session.delete.called

    def test_post_init_method(self):
        """Test that __post_init__ method can be called without errors"""
        # Act & Assert - should not raise any exceptions
        self.repository.__post_init__()

    def test_db_session_called_for_all_methods(self):
        """Test that db_session.get_session() is called for all methods"""
        # Setup mocks
        self.mock_db_session.query.return_value.all.return_value = []
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
        self.mock_db_session.query.return_value.filter.return_value.all.return_value = []
        self.mock_db_session.add = Mock()
        self.mock_db_session.flush = Mock()
        self.mock_db_session.refresh = Mock()
        self.mock_db_session.merge = Mock()
        self.mock_db_session.delete = Mock()

        mock_category = self.create_mock_category(1, "Test")

        # Call all methods
        self.repository.get_all_categories()
        self.repository.get_category_by_id(1)
        self.repository.get_category_by_name("Test")
        self.repository.get_categories_by_parent(1)
        self.repository.get_root_categories()
        self.repository.create_category(mock_category)
        self.repository.update_category(mock_category)

        with patch.object(self.repository, 'get_category_by_id', return_value=mock_category):
            self.repository.delete_category(1)

        # Assert session methods were called directly
        # Query should be called for read operations
        assert self.mock_db_session.query.call_count >= 5  # At least 5 read operations
        # Add, merge, commit should be called for write operations
        self.mock_db_session.add.assert_called()
        self.mock_db_session.merge.assert_called()
        self.mock_db_session.flush.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
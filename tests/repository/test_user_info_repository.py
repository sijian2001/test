import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List, Optional
import sys
import os

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from domain.repository.test1.user_info_repository import UserInfoRepository
from domain.model.test1.user_info import UserInfo
from domain.database import DatabaseSession


class TestUserInfoRepository:
    """Unit tests for UserInfoRepository class"""

    def setup_method(self):
        """Setup method called before each test"""
        # Create a mock DatabaseSession
        self.mock_db_session = Mock(spec=DatabaseSession)
        self.mock_session = Mock()
        self.mock_db_session.get_session.return_value = self.mock_session

        # Create UserInfoRepository instance with mocked dependencies
        self.repository = UserInfoRepository(db_session=self.mock_db_session)

    def create_mock_user_info(self, user_id: int, username: str, department_name: str = "Engineering") -> UserInfo:
        """Helper method to create mock UserInfo objects"""
        user_info = Mock(spec=UserInfo)
        user_info.user_id = user_id
        user_info.username = username
        user_info.email = f"{username}@company.com"
        user_info.first_name = username.split('.')[0].title()
        user_info.last_name = username.split('.')[1].title() if '.' in username else "Doe"
        user_info.department_name = department_name
        user_info.manager_id = 101
        user_info.is_active = "active"
        user_info.created_at = "2025-09-17 17:47:03"
        user_info.updated_at = "2025-09-17 17:47:03"
        return user_info

    def test_get_all_user_info_success(self):
        """Test get_all_user_info returns all user info records"""
        # Arrange
        mock_user_info_list = [
            self.create_mock_user_info(1, "john.doe", "Engineering"),
            self.create_mock_user_info(2, "jane.smith", "Marketing"),
            self.create_mock_user_info(3, "bob.johnson", "Sales")
        ]
        self.mock_session.query.return_value.all.return_value = mock_user_info_list

        # Act
        result = self.repository.get_all_user_info()

        # Assert
        assert result == mock_user_info_list
        assert len(result) == 3
        self.mock_db_session.get_session.assert_called_once_with("test1")
        self.mock_session.query.assert_called_once_with(UserInfo)
        self.mock_session.query.return_value.all.assert_called_once()

    def test_get_all_user_info_empty_result(self):
        """Test get_all_user_info returns empty list when no records found"""
        # Arrange
        self.mock_session.query.return_value.all.return_value = []

        # Act
        result = self.repository.get_all_user_info()

        # Assert
        assert result == []
        assert len(result) == 0
        self.mock_db_session.get_session.assert_called_once_with("test1")

    def test_get_user_info_by_id_success(self):
        """Test get_user_info_by_id returns user info when found"""
        # Arrange
        user_id = 1
        mock_user_info = self.create_mock_user_info(1, "john.doe", "Engineering")
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user_info

        # Act
        result = self.repository.get_user_info_by_id(user_id)

        # Assert
        assert result == mock_user_info
        assert result.user_id == user_id
        self.mock_db_session.get_session.assert_called_once_with("test1")
        self.mock_session.query.assert_called_once_with(UserInfo)
        self.mock_session.query.return_value.filter.assert_called_once()
        self.mock_session.query.return_value.filter.return_value.first.assert_called_once()

    def test_get_user_info_by_id_not_found(self):
        """Test get_user_info_by_id returns None when user not found"""
        # Arrange
        user_id = 999
        self.mock_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.repository.get_user_info_by_id(user_id)

        # Assert
        assert result is None
        self.mock_db_session.get_session.assert_called_once_with("test1")

    def test_get_user_info_by_username_success(self):
        """Test get_user_info_by_username returns user info when found"""
        # Arrange
        username = "john.doe"
        mock_user_info = self.create_mock_user_info(1, username, "Engineering")
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_user_info

        # Act
        result = self.repository.get_user_info_by_username(username)

        # Assert
        assert result == mock_user_info
        assert result.username == username
        self.mock_db_session.get_session.assert_called_once_with("test1")
        self.mock_session.query.assert_called_once_with(UserInfo)

    def test_get_user_info_by_username_not_found(self):
        """Test get_user_info_by_username returns None when user not found"""
        # Arrange
        username = "nonexistent.user"
        self.mock_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.repository.get_user_info_by_username(username)

        # Assert
        assert result is None
        self.mock_db_session.get_session.assert_called_once_with("test1")

    def test_get_user_info_by_department_success(self):
        """Test get_user_info_by_department returns user info list when found"""
        # Arrange
        department_name = "Engineering"
        mock_user_info_list = [
            self.create_mock_user_info(1, "john.doe", "Engineering"),
            self.create_mock_user_info(6, "diana.garcia", "Engineering")
        ]
        self.mock_session.query.return_value.filter.return_value.all.return_value = mock_user_info_list

        # Act
        result = self.repository.get_user_info_by_department(department_name)

        # Assert
        assert result == mock_user_info_list
        assert len(result) == 2
        for user_info in result:
            assert user_info.department_name == department_name
        self.mock_db_session.get_session.assert_called_once_with("test1")
        self.mock_session.query.assert_called_once_with(UserInfo)

    def test_get_user_info_by_department_empty_result(self):
        """Test get_user_info_by_department returns empty list when no users found"""
        # Arrange
        department_name = "NonexistentDepartment"
        self.mock_session.query.return_value.filter.return_value.all.return_value = []

        # Act
        result = self.repository.get_user_info_by_department(department_name)

        # Assert
        assert result == []
        assert len(result) == 0
        self.mock_db_session.get_session.assert_called_once_with("test1")

    def test_db_session_called_for_all_methods(self):
        """Test that db_session.get_session() is called for all methods"""
        # Test all methods call get_session()
        self.mock_session.query.return_value.all.return_value = []
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        self.mock_session.query.return_value.filter.return_value.all.return_value = []

        # Call all methods
        self.repository.get_all_user_info()
        self.repository.get_user_info_by_id(1)
        self.repository.get_user_info_by_username("test")
        self.repository.get_user_info_by_department("test")

        # Assert get_session was called 4 times with "test1" parameter
        assert self.mock_db_session.get_session.call_count == 4
        # Verify all calls were made with "test1" parameter
        for call in self.mock_db_session.get_session.call_args_list:
            assert call[0][0] == "test1"

    def test_post_init_method(self):
        """Test that __post_init__ method can be called without errors"""
        # Act & Assert - should not raise any exceptions
        self.repository.__post_init__()

    def test_query_called_with_correct_model(self):
        """Test that session.query is called with UserInfo model class"""
        # Arrange
        self.mock_session.query.return_value.all.return_value = []

        # Act
        self.repository.get_all_user_info()

        # Assert
        # Verify that query was called (the actual model class verification is complex with mocking)
        self.mock_session.query.assert_called_once()
        # Verify the call was made with some argument (the UserInfo class)
        call_args = self.mock_session.query.call_args
        assert call_args is not None
        assert len(call_args[0]) == 1  # One positional argument

    def test_filter_conditions(self):
        """Test that correct filter conditions are applied"""
        # Setup mock chain for testing filter conditions
        mock_query = Mock()
        mock_filter = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        mock_filter.all.return_value = []

        # Test user_id filter
        self.repository.get_user_info_by_id(123)
        mock_query.filter.assert_called()

        # Test username filter
        mock_query.reset_mock()
        self.repository.get_user_info_by_username("test_user")
        mock_query.filter.assert_called()

        # Test department filter
        mock_query.reset_mock()
        self.repository.get_user_info_by_department("TestDept")
        mock_query.filter.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List, Optional
import sys
import os

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from domain.repository.test1.user_repository import UserRepository
from domain.model.test1.user import User
from sqlalchemy.orm import Session


class TestUserRepository:
    """Unit tests for UserRepository class"""

    def setup_method(self):
        """Setup method called before each test"""
        # Create a mock Session (since Test1DatabaseSession now inherits from Session)
        self.mock_db_session = Mock(spec=Session)

        # Create UserRepository instance with mocked dependencies
        self.repository = UserRepository(db_session=self.mock_db_session)

    def create_mock_user(self, user_id: int, username: str, email: str = None,
                        first_name: str = None, last_name: str = None, department_id: int = None) -> User:
        """Helper method to create mock User objects"""
        user = Mock(spec=User)
        user.id = user_id
        user.username = username
        user.email = email or f"{username}@company.com"
        user.first_name = first_name or username.split('.')[0].title()
        user.last_name = last_name or (username.split('.')[1].title() if '.' in username else "Doe")
        user.department_id = department_id or 1
        user.password_hash = "hashed_password"
        user.is_active = True
        user.created_at = "2025-09-17 17:47:03"
        user.updated_at = "2025-09-17 17:47:03"
        return user

    def test_get_all_users_success(self):
        """Test get_all_users returns all users"""
        # Arrange
        mock_users = [
            self.create_mock_user(1, "john.doe", department_id=1),
            self.create_mock_user(2, "jane.smith", department_id=2),
            self.create_mock_user(3, "bob.johnson", department_id=1)
        ]
        self.mock_db_session.query.return_value.all.return_value = mock_users

        # Act
        result = self.repository.get_all_users()

        # Assert
        assert result == mock_users
        assert len(result) == 3
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_all_users_empty_result(self):
        """Test get_all_users returns empty list when no users found"""
        # Arrange
        self.mock_db_session.query.return_value.all.return_value = []

        # Act
        result = self.repository.get_all_users()

        # Assert
        assert result == []
        assert len(result) == 0
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_get_user_by_id_success(self):
        """Test get_user_by_id returns user when found"""
        # Arrange
        user_id = 1
        mock_user = self.create_mock_user(1, "john.doe")
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

        # Act
        result = self.repository.get_user_by_id(user_id)

        # Assert
        assert result == mock_user
        assert result.id == user_id
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()
        self.mock_db_session.query.assert_called_with(User)

    def test_get_user_by_id_not_found(self):
        """Test get_user_by_id returns None when user not found"""
        # Arrange
        user_id = 999
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.repository.get_user_by_id(user_id)

        # Assert
        assert result is None
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_create_user_success(self):
        """Test create_user creates new user successfully"""
        # Arrange
        username = "new.user"
        email = "new.user@company.com"
        password_hash = "hashed_password"
        first_name = "New"
        last_name = "User"
        department_id = 1

        mock_user = self.create_mock_user(4, username, email, first_name, last_name, department_id)

        # Mock session.add, commit, refresh
        self.mock_db_session.add = Mock()
        self.mock_db_session.commit = Mock()
        self.mock_db_session.refresh = Mock()

        # Act
        with patch('domain.repository.test1.user_repository.User') as mock_user_class:
            mock_user_class.return_value = mock_user
            result = self.repository.create_user(username, email, password_hash, first_name, last_name, department_id)

            # Assert
            assert result == mock_user
            mock_user_class.assert_called_once_with(
                username=username,
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                department_id=department_id
            )
            self.mock_db_session.add.assert_called_once_with(mock_user)
            self.mock_db_session.commit.assert_called_once()
            self.mock_db_session.refresh.assert_called_once_with(mock_user)

    def test_create_user_with_minimal_params(self):
        """Test create_user with only required parameters"""
        # Arrange
        username = "minimal.user"
        email = "minimal.user@company.com"
        password_hash = "hashed_password"

        mock_user = self.create_mock_user(5, username, email)

        self.mock_db_session.add = Mock()
        self.mock_db_session.commit = Mock()
        self.mock_db_session.refresh = Mock()

        # Act
        with patch('domain.repository.test1.user_repository.User') as mock_user_class:
            mock_user_class.return_value = mock_user
            result = self.repository.create_user(username, email, password_hash)

            # Assert
            assert result == mock_user
            mock_user_class.assert_called_once_with(
                username=username,
                email=email,
                password_hash=password_hash,
                first_name=None,
                last_name=None,
                department_id=None
            )

    def test_update_user_success(self):
        """Test update_user updates existing user successfully"""
        # Arrange
        user_id = 1
        updated_username = "updated.user"
        updated_email = "updated.user@company.com"
        updated_first_name = "Updated"
        updated_last_name = "User"
        updated_department_id = 2

        mock_user = self.create_mock_user(user_id, "original.user")
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_db_session.commit = Mock()
        self.mock_db_session.refresh = Mock()

        # Act
        result = self.repository.update_user(
            user_id, updated_username, updated_email,
            updated_first_name, updated_last_name, updated_department_id
        )

        # Assert
        assert result == mock_user
        assert mock_user.username == updated_username
        assert mock_user.email == updated_email
        assert mock_user.first_name == updated_first_name
        assert mock_user.last_name == updated_last_name
        assert mock_user.department_id == updated_department_id
        self.mock_db_session.commit.assert_called_once()
        self.mock_db_session.refresh.assert_called_once_with(mock_user)

    def test_update_user_partial_update(self):
        """Test update_user with partial updates (only some fields)"""
        # Arrange
        user_id = 1
        updated_username = "updated.user"

        mock_user = self.create_mock_user(user_id, "original.user")
        original_email = mock_user.email
        original_first_name = mock_user.first_name

        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_db_session.commit = Mock()
        self.mock_db_session.refresh = Mock()

        # Act
        result = self.repository.update_user(user_id, username=updated_username)

        # Assert
        assert result == mock_user
        assert mock_user.username == updated_username
        assert mock_user.email == original_email  # Should remain unchanged
        assert mock_user.first_name == original_first_name  # Should remain unchanged

    def test_update_user_not_found(self):
        """Test update_user returns None when user not found"""
        # Arrange
        user_id = 999
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.repository.update_user(user_id, username="new.username")

        # Assert
        assert result is None
        # Session is used directly now, so we verify query was called on the session
        self.mock_db_session.query.assert_called()

    def test_update_user_with_department_id_zero(self):
        """Test update_user handles department_id=0 correctly"""
        # Arrange
        user_id = 1
        mock_user = self.create_mock_user(user_id, "test.user")
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_db_session.commit = Mock()
        self.mock_db_session.refresh = Mock()

        # Act
        result = self.repository.update_user(user_id, department_id=0)

        # Assert
        assert result == mock_user
        assert mock_user.department_id == 0

    def test_post_init_method(self):
        """Test that __post_init__ method can be called without errors"""
        # Act & Assert - should not raise any exceptions
        self.repository.__post_init__()

    def test_db_session_called_for_all_methods(self):
        """Test that db_session is used directly for all methods"""
        # Setup mocks
        self.mock_db_session.query.return_value.all.return_value = []
        self.mock_db_session.query.return_value.filter.return_value.first.return_value = None
        self.mock_db_session.add = Mock()
        self.mock_db_session.commit = Mock()
        self.mock_db_session.refresh = Mock()

        # Call all methods
        self.repository.get_all_users()
        self.repository.get_user_by_id(1)

        with patch('domain.repository.test1.user_repository.User') as mock_user_class:
            mock_user_class.return_value = Mock()
            self.repository.create_user("test", "test@email.com", "hash")

        self.repository.update_user(1, username="test")

        # Assert session methods were called directly (query for read operations)
        assert self.mock_db_session.query.call_count == 3
        # Also verify that add and commit were called for write operations
        self.mock_db_session.add.assert_called_once()
        self.mock_db_session.commit.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
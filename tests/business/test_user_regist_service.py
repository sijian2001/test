import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List
import sys
import os

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from business.user_regist_service import UserRegistService, UserRegistInDto, UserRegistOutDto
from domain.repository.test1.user_repository import UserRepository
from domain.model.test1.user import User
from business.vo.user_vo import UserVo


class TestUserRegistService:
    """Unit tests for UserRegistService class"""

    def setup_method(self):
        """Setup method called before each test"""
        # Create a mock UserRepository
        self.mock_repository = Mock(spec=UserRepository)

        # Create UserRegistService instance with mocked dependencies
        self.service = UserRegistService(user_repository=self.mock_repository)

    def create_user_vo(self, username: str, email: str = None, password_hash: str = "hashed_password",
                      first_name: str = None, last_name: str = None, department_id: int = None,
                      is_active: bool = True) -> UserVo:
        """Helper method to create UserVo objects"""
        return UserVo(
            username=username,
            email=email or f"{username}@company.com",
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            department_id=department_id,
            is_active=is_active
        )

    def test_execute_single_user_success(self):
        """Test execute with single user registration success"""
        # Arrange
        user_vo = self.create_user_vo("john.doe", "john.doe@company.com", "hashed_password",
                                     "John", "Doe", 1, True)
        in_dto = UserRegistInDto(userList=[user_vo])

        # Mock repository to return successfully created user
        mock_user = Mock(spec=User)
        self.mock_repository.create_user.return_value = mock_user

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, UserRegistOutDto)
        assert result.userCount == 1
        self.mock_repository.create_user.assert_called_once_with(
            username="john.doe",
            email="john.doe@company.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            department_id=1
        )

    def test_execute_multiple_users_success(self):
        """Test execute with multiple users registration success"""
        # Arrange
        user_vo_list = [
            self.create_user_vo("john.doe", "john.doe@company.com", "hash1", "John", "Doe", 1),
            self.create_user_vo("jane.smith", "jane.smith@company.com", "hash2", "Jane", "Smith", 2),
            self.create_user_vo("bob.johnson", "bob.johnson@company.com", "hash3", "Bob", "Johnson", 1)
        ]
        in_dto = UserRegistInDto(userList=user_vo_list)

        # Mock repository to return successfully created users
        mock_user = Mock(spec=User)
        self.mock_repository.create_user.return_value = mock_user

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, UserRegistOutDto)
        assert result.userCount == 3
        assert self.mock_repository.create_user.call_count == 3

        # Verify each user was created with correct parameters
        call_args_list = self.mock_repository.create_user.call_args_list

        # First user
        first_call = call_args_list[0][1]  # kwargs
        assert first_call['username'] == "john.doe"
        assert first_call['email'] == "john.doe@company.com"
        assert first_call['password_hash'] == "hash1"
        assert first_call['first_name'] == "John"
        assert first_call['last_name'] == "Doe"
        assert first_call['department_id'] == 1

        # Second user
        second_call = call_args_list[1][1]  # kwargs
        assert second_call['username'] == "jane.smith"
        assert second_call['email'] == "jane.smith@company.com"
        assert second_call['password_hash'] == "hash2"
        assert second_call['first_name'] == "Jane"
        assert second_call['last_name'] == "Smith"
        assert second_call['department_id'] == 2

        # Third user
        third_call = call_args_list[2][1]  # kwargs
        assert third_call['username'] == "bob.johnson"
        assert third_call['email'] == "bob.johnson@company.com"
        assert third_call['password_hash'] == "hash3"
        assert third_call['first_name'] == "Bob"
        assert third_call['last_name'] == "Johnson"
        assert third_call['department_id'] == 1

    def test_execute_empty_user_list(self):
        """Test execute with empty user list"""
        # Arrange
        in_dto = UserRegistInDto(userList=[])

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, UserRegistOutDto)
        assert result.userCount == 0
        self.mock_repository.create_user.assert_not_called()

    def test_execute_user_with_minimal_fields(self):
        """Test execute with user having only required fields"""
        # Arrange
        user_vo = UserVo(
            username="minimal.user",
            email="minimal.user@company.com",
            password_hash="hashed_password"
            # first_name, last_name, department_id default to None
            # is_active defaults to True
        )
        in_dto = UserRegistInDto(userList=[user_vo])

        # Mock repository
        mock_user = Mock(spec=User)
        self.mock_repository.create_user.return_value = mock_user

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, UserRegistOutDto)
        assert result.userCount == 1

        # Verify the repository was called with None values for optional fields
        call_kwargs = self.mock_repository.create_user.call_args[1]
        assert call_kwargs['username'] == "minimal.user"
        assert call_kwargs['email'] == "minimal.user@company.com"
        assert call_kwargs['password_hash'] == "hashed_password"
        assert call_kwargs['first_name'] is None
        assert call_kwargs['last_name'] is None
        assert call_kwargs['department_id'] is None

    def test_execute_user_with_none_department_id(self):
        """Test execute with user having None department_id"""
        # Arrange
        user_vo = self.create_user_vo("no.department", department_id=None)
        in_dto = UserRegistInDto(userList=[user_vo])

        # Mock repository
        mock_user = Mock(spec=User)
        self.mock_repository.create_user.return_value = mock_user

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, UserRegistOutDto)
        assert result.userCount == 1

        # Verify department_id is None
        call_kwargs = self.mock_repository.create_user.call_args[1]
        assert call_kwargs['department_id'] is None

    def test_execute_user_repository_exception(self):
        """Test execute handles repository exceptions correctly"""
        # Arrange
        user_vo = self.create_user_vo("test.user")
        in_dto = UserRegistInDto(userList=[user_vo])

        # Mock repository to raise exception
        self.mock_repository.create_user.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.execute(in_dto)

        assert str(exc_info.value) == "Database error"
        self.mock_repository.create_user.assert_called_once()

    def test_execute_partial_failure_with_multiple_users(self):
        """Test execute with partial failure in multiple users"""
        # Arrange
        user_vo_list = [
            self.create_user_vo("user1"),
            self.create_user_vo("failing.user"),
            self.create_user_vo("user3")
        ]
        in_dto = UserRegistInDto(userList=user_vo_list)

        # Mock repository: first succeeds, second fails, third never called due to exception
        mock_user = Mock(spec=User)
        self.mock_repository.create_user.side_effect = [
            mock_user,  # First call succeeds
            Exception("Database error"),  # Second call fails
        ]

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.execute(in_dto)

        assert str(exc_info.value) == "Database error"
        # Only first two users should have been attempted
        assert self.mock_repository.create_user.call_count == 2

    def test_execute_with_special_characters_in_fields(self):
        """Test execute with special characters in user fields"""
        # Arrange
        user_vo = self.create_user_vo(
            username="user.with-special_chars123",
            email="user+test@company-name.com",
            first_name="José",
            last_name="O'Connor"
        )
        in_dto = UserRegistInDto(userList=[user_vo])

        # Mock repository
        mock_user = Mock(spec=User)
        self.mock_repository.create_user.return_value = mock_user

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, UserRegistOutDto)
        assert result.userCount == 1

        # Verify special characters are preserved
        call_kwargs = self.mock_repository.create_user.call_args[1]
        assert call_kwargs['username'] == "user.with-special_chars123"
        assert call_kwargs['email'] == "user+test@company-name.com"
        assert call_kwargs['first_name'] == "José"
        assert call_kwargs['last_name'] == "O'Connor"

    def test_execute_with_different_department_ids(self):
        """Test execute with various department ID values"""
        # Arrange
        user_vo_list = [
            self.create_user_vo("user1", department_id=1),
            self.create_user_vo("user2", department_id=999),
            self.create_user_vo("user3", department_id=0),
            self.create_user_vo("user4", department_id=None)
        ]
        in_dto = UserRegistInDto(userList=user_vo_list)

        # Mock repository
        mock_user = Mock(spec=User)
        self.mock_repository.create_user.return_value = mock_user

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, UserRegistOutDto)
        assert result.userCount == 4

        # Verify department IDs are preserved correctly
        call_args_list = self.mock_repository.create_user.call_args_list
        assert call_args_list[0][1]['department_id'] == 1
        assert call_args_list[1][1]['department_id'] == 999
        assert call_args_list[2][1]['department_id'] == 0
        assert call_args_list[3][1]['department_id'] is None

    def test_post_init_method(self):
        """Test that __post_init__ method initializes logger correctly"""
        # Act & Assert - should not raise any exceptions
        self.service.__post_init__()
        assert hasattr(self.service, 'logger')

    @patch('business.user_regist_service.logging.getLogger')
    def test_logging_calls_success(self, mock_get_logger):
        """Test that appropriate logging calls are made for successful registration"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        self.service.__post_init__()

        user_vo = self.create_user_vo("test.user")
        in_dto = UserRegistInDto(userList=[user_vo])

        mock_user = Mock(spec=User)
        self.mock_repository.create_user.return_value = mock_user

        # Act
        self.service.execute(in_dto)

        # Assert
        mock_logger.info.assert_called()
        # Should have at least: start, per-user, count, and completion messages
        assert mock_logger.info.call_count >= 4

    @patch('business.user_regist_service.logging.getLogger')
    def test_logging_calls_failure(self, mock_get_logger):
        """Test that appropriate logging calls are made for failed registration"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        self.service.__post_init__()

        user_vo = self.create_user_vo("failing.user")
        in_dto = UserRegistInDto(userList=[user_vo])

        # Mock repository to raise exception
        self.mock_repository.create_user.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            self.service.execute(in_dto)

        # Verify error logging was called
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        assert "Failed to register user failing.user" in error_call_args
        assert "Database error" in error_call_args

    def test_repository_method_call_parameters(self):
        """Test that repository create_user method is called with correct parameter types"""
        # Arrange
        user_vo = UserVo(
            username="test.user",
            email="test.user@company.com",
            password_hash="hashed_password_123",
            first_name="Test",
            last_name="User",
            department_id=5,
            is_active=True
        )
        in_dto = UserRegistInDto(userList=[user_vo])

        # Mock repository
        mock_user = Mock(spec=User)
        self.mock_repository.create_user.return_value = mock_user

        # Act
        result = self.service.execute(in_dto)

        # Assert
        self.mock_repository.create_user.assert_called_once()

        # Get the parameters that were passed to create_user
        call_kwargs = self.mock_repository.create_user.call_args[1]

        # Verify parameter types and values
        assert isinstance(call_kwargs['username'], str)
        assert isinstance(call_kwargs['email'], str)
        assert isinstance(call_kwargs['password_hash'], str)
        assert isinstance(call_kwargs['first_name'], str)
        assert isinstance(call_kwargs['last_name'], str)
        assert isinstance(call_kwargs['department_id'], int)

        assert call_kwargs['username'] == "test.user"
        assert call_kwargs['email'] == "test.user@company.com"
        assert call_kwargs['password_hash'] == "hashed_password_123"
        assert call_kwargs['first_name'] == "Test"
        assert call_kwargs['last_name'] == "User"
        assert call_kwargs['department_id'] == 5

    def test_in_dto_validation(self):
        """Test that UserRegistInDto accepts the expected structure"""
        # Arrange
        user_vo_list = [
            self.create_user_vo("user1"),
            self.create_user_vo("user2")
        ]

        # Act
        in_dto = UserRegistInDto(userList=user_vo_list)

        # Assert
        assert isinstance(in_dto, UserRegistInDto)
        assert len(in_dto.userList) == 2
        assert in_dto.userList[0].username == "user1"
        assert in_dto.userList[1].username == "user2"

    def test_out_dto_structure(self):
        """Test that UserRegistOutDto has the expected structure"""
        # Act
        out_dto = UserRegistOutDto(userCount=15)

        # Assert
        assert isinstance(out_dto, UserRegistOutDto)
        assert out_dto.userCount == 15


if __name__ == "__main__":
    pytest.main([__file__])
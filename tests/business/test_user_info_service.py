import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List, Optional
import sys
import os

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.business.user_info_service import UserInfoService, UserInfoSearchInDto, UserInfoOutDto
from app.domain.repository.test1.user_info_repository import UserInfoRepository
from app.domain.model.test1.user_info import UserInfo


class TestUserInfoService:
    """Unit tests for UserInfoService class"""

    def setup_method(self):
        """Setup method called before each test"""
        # Create a mock UserInfoRepository
        self.mock_repository = Mock(spec=UserInfoRepository)

        # Create UserInfoService instance with mocked dependencies
        self.service = UserInfoService(user_info_repository=self.mock_repository)

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
        """Test get_all_user_info returns all user info with correct count"""
        # Arrange
        mock_user_info_list = [
            self.create_mock_user_info(1, "john.doe", "Engineering"),
            self.create_mock_user_info(2, "jane.smith", "Marketing"),
            self.create_mock_user_info(3, "bob.johnson", "Sales")
        ]
        self.mock_repository.get_all_user_info.return_value = mock_user_info_list

        # Act
        result = self.service.get_all_user_info()

        # Assert
        assert isinstance(result, UserInfoOutDto)
        assert result.user_info_list == mock_user_info_list
        assert result.total_count == 3
        self.mock_repository.get_all_user_info.assert_called_once()

    def test_get_all_user_info_empty_result(self):
        """Test get_all_user_info returns empty result with zero count"""
        # Arrange
        self.mock_repository.get_all_user_info.return_value = []

        # Act
        result = self.service.get_all_user_info()

        # Assert
        assert isinstance(result, UserInfoOutDto)
        assert result.user_info_list == []
        assert result.total_count == 0
        self.mock_repository.get_all_user_info.assert_called_once()

    def test_search_user_info_by_user_id_success(self):
        """Test search_user_info by user_id returns correct result"""
        # Arrange
        user_id = 1
        mock_user_info = self.create_mock_user_info(1, "john.doe", "Engineering")
        self.mock_repository.get_user_info_by_id.return_value = mock_user_info
        search_dto = UserInfoSearchInDto(user_id=user_id)

        # Act
        result = self.service.search_user_info(search_dto)

        # Assert
        assert isinstance(result, UserInfoOutDto)
        assert len(result.user_info_list) == 1
        assert result.user_info_list[0] == mock_user_info
        assert result.total_count == 1
        self.mock_repository.get_user_info_by_id.assert_called_once_with(user_id)

    def test_search_user_info_by_user_id_not_found(self):
        """Test search_user_info by user_id when user not found"""
        # Arrange
        user_id = 999
        self.mock_repository.get_user_info_by_id.return_value = None
        search_dto = UserInfoSearchInDto(user_id=user_id)

        # Act
        result = self.service.search_user_info(search_dto)

        # Assert
        assert isinstance(result, UserInfoOutDto)
        assert result.user_info_list == []
        assert result.total_count == 0
        self.mock_repository.get_user_info_by_id.assert_called_once_with(user_id)

    def test_search_user_info_by_username_success(self):
        """Test search_user_info by username returns correct result"""
        # Arrange
        username = "john.doe"
        mock_user_info = self.create_mock_user_info(1, username, "Engineering")
        self.mock_repository.get_user_info_by_username.return_value = mock_user_info
        search_dto = UserInfoSearchInDto(username=username)

        # Act
        result = self.service.search_user_info(search_dto)

        # Assert
        assert isinstance(result, UserInfoOutDto)
        assert len(result.user_info_list) == 1
        assert result.user_info_list[0] == mock_user_info
        assert result.total_count == 1
        self.mock_repository.get_user_info_by_username.assert_called_once_with(username)

    def test_search_user_info_by_username_not_found(self):
        """Test search_user_info by username when user not found"""
        # Arrange
        username = "nonexistent.user"
        self.mock_repository.get_user_info_by_username.return_value = None
        search_dto = UserInfoSearchInDto(username=username)

        # Act
        result = self.service.search_user_info(search_dto)

        # Assert
        assert isinstance(result, UserInfoOutDto)
        assert result.user_info_list == []
        assert result.total_count == 0
        self.mock_repository.get_user_info_by_username.assert_called_once_with(username)

    def test_search_user_info_by_department_success(self):
        """Test search_user_info by department returns correct result"""
        # Arrange
        department_name = "Engineering"
        mock_user_info_list = [
            self.create_mock_user_info(1, "john.doe", "Engineering"),
            self.create_mock_user_info(6, "diana.garcia", "Engineering")
        ]
        self.mock_repository.get_user_info_by_department.return_value = mock_user_info_list
        search_dto = UserInfoSearchInDto(department_name=department_name)

        # Act
        result = self.service.search_user_info(search_dto)

        # Assert
        assert isinstance(result, UserInfoOutDto)
        assert result.user_info_list == mock_user_info_list
        assert result.total_count == 2
        self.mock_repository.get_user_info_by_department.assert_called_once_with(department_name)

    def test_search_user_info_by_department_empty_result(self):
        """Test search_user_info by department when no users found"""
        # Arrange
        department_name = "NonexistentDepartment"
        self.mock_repository.get_user_info_by_department.return_value = []
        search_dto = UserInfoSearchInDto(department_name=department_name)

        # Act
        result = self.service.search_user_info(search_dto)

        # Assert
        assert isinstance(result, UserInfoOutDto)
        assert result.user_info_list == []
        assert result.total_count == 0
        self.mock_repository.get_user_info_by_department.assert_called_once_with(department_name)

    def test_search_user_info_no_criteria_calls_get_all(self):
        """Test search_user_info with no criteria falls back to get_all_user_info"""
        # Arrange
        mock_user_info_list = [
            self.create_mock_user_info(1, "john.doe", "Engineering"),
            self.create_mock_user_info(2, "jane.smith", "Marketing")
        ]
        self.mock_repository.get_all_user_info.return_value = mock_user_info_list
        search_dto = UserInfoSearchInDto()  # No search criteria

        # Act
        result = self.service.search_user_info(search_dto)

        # Assert
        assert isinstance(result, UserInfoOutDto)
        assert result.user_info_list == mock_user_info_list
        assert result.total_count == 2
        self.mock_repository.get_all_user_info.assert_called_once()

    def test_search_user_info_priority_user_id_over_username(self):
        """Test search_user_info prioritizes user_id over username when both provided"""
        # Arrange
        user_id = 1
        username = "john.doe"
        mock_user_info = self.create_mock_user_info(1, "john.doe", "Engineering")
        self.mock_repository.get_user_info_by_id.return_value = mock_user_info
        search_dto = UserInfoSearchInDto(user_id=user_id, username=username)

        # Act
        result = self.service.search_user_info(search_dto)

        # Assert
        assert isinstance(result, UserInfoOutDto)
        assert len(result.user_info_list) == 1
        assert result.total_count == 1
        self.mock_repository.get_user_info_by_id.assert_called_once_with(user_id)
        self.mock_repository.get_user_info_by_username.assert_not_called()

    def test_search_user_info_priority_username_over_department(self):
        """Test search_user_info prioritizes username over department when both provided"""
        # Arrange
        username = "john.doe"
        department_name = "Engineering"
        mock_user_info = self.create_mock_user_info(1, "john.doe", "Engineering")
        self.mock_repository.get_user_info_by_username.return_value = mock_user_info
        search_dto = UserInfoSearchInDto(username=username, department_name=department_name)

        # Act
        result = self.service.search_user_info(search_dto)

        # Assert
        assert isinstance(result, UserInfoOutDto)
        assert len(result.user_info_list) == 1
        assert result.total_count == 1
        self.mock_repository.get_user_info_by_username.assert_called_once_with(username)
        self.mock_repository.get_user_info_by_department.assert_not_called()

    def test_execute_delegates_to_search_user_info(self):
        """Test execute method delegates to search_user_info"""
        # Arrange
        username = "john.doe"
        mock_user_info = self.create_mock_user_info(1, "john.doe", "Engineering")
        self.mock_repository.get_user_info_by_username.return_value = mock_user_info
        search_dto = UserInfoSearchInDto(username=username)

        # Act
        result = self.service.execute(search_dto)

        # Assert
        assert isinstance(result, UserInfoOutDto)
        assert len(result.user_info_list) == 1
        assert result.total_count == 1
        self.mock_repository.get_user_info_by_username.assert_called_once_with(username)

    def test_post_init_method(self):
        """Test that __post_init__ method initializes logger correctly"""
        # Act & Assert - should not raise any exceptions
        self.service.__post_init__()
        assert hasattr(self.service, 'logger')

    @patch('app.business.user_info_service.logging.getLogger')
    def test_logging_calls(self, mock_get_logger):
        """Test that appropriate logging calls are made"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        self.service.__post_init__()
        self.mock_repository.get_all_user_info.return_value = []

        # Act
        self.service.get_all_user_info()

        # Assert
        mock_logger.info.assert_called()
        assert mock_logger.info.call_count >= 2  # At least start and end log messages

    def test_user_info_search_in_dto_creation(self):
        """Test UserInfoSearchInDto can be created with various parameters"""
        # Test creation with different parameters
        dto1 = UserInfoSearchInDto()
        assert dto1.user_id is None
        assert dto1.username is None
        assert dto1.department_name is None

        dto2 = UserInfoSearchInDto(user_id=1)
        assert dto2.user_id == 1
        assert dto2.username is None

        dto3 = UserInfoSearchInDto(username="test")
        assert dto3.username == "test"
        assert dto3.user_id is None

        dto4 = UserInfoSearchInDto(department_name="Engineering")
        assert dto4.department_name == "Engineering"

    def test_user_info_out_dto_creation(self):
        """Test UserInfoOutDto can be created correctly"""
        # Arrange
        mock_user_list = [self.create_mock_user_info(1, "test", "Engineering")]

        # Act
        dto = UserInfoOutDto(user_info_list=mock_user_list, total_count=1)

        # Assert
        assert dto.user_info_list == mock_user_list
        assert dto.total_count == 1

    def test_repository_method_calls_verification(self):
        """Test that repository methods are called correctly for different search scenarios"""
        # Test user_id search
        search_dto = UserInfoSearchInDto(user_id=1)
        self.mock_repository.get_user_info_by_id.return_value = None
        self.service.search_user_info(search_dto)
        self.mock_repository.get_user_info_by_id.assert_called_once_with(1)

        # Reset mock
        self.mock_repository.reset_mock()

        # Test username search
        search_dto = UserInfoSearchInDto(username="test")
        self.mock_repository.get_user_info_by_username.return_value = None
        self.service.search_user_info(search_dto)
        self.mock_repository.get_user_info_by_username.assert_called_once_with("test")

        # Reset mock
        self.mock_repository.reset_mock()

        # Test department search
        search_dto = UserInfoSearchInDto(department_name="Engineering")
        self.mock_repository.get_user_info_by_department.return_value = []
        self.service.search_user_info(search_dto)
        self.mock_repository.get_user_info_by_department.assert_called_once_with("Engineering")


if __name__ == "__main__":
    pytest.main([__file__])
import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List
import sys
import os

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from business.department_regist_service import DepartmentRegistService, DepartmentRegistInDto, DepartmentRegistOutDto
from domain.repository.test1.department_repository import DepartmentRepository
from domain.model.test1.department import Department
from domain.vo.department_vo import DepartmentVo


class TestDepartmentRegistService:
    """Unit tests for DepartmentRegistService class"""

    def setup_method(self):
        """Setup method called before each test"""
        # Create a mock DepartmentRepository
        self.mock_repository = Mock(spec=DepartmentRepository)

        # Create DepartmentRegistService instance with mocked dependencies
        self.service = DepartmentRegistService(department_repository=self.mock_repository)

    def create_department_vo(self, name: str, description: str = None, manager_id: int = None,
                            is_active: bool = True) -> DepartmentVo:
        """Helper method to create DepartmentVo objects"""
        return DepartmentVo(
            name=name,
            description=description or f"Description for {name}",
            manager_id=manager_id,
            is_active=is_active
        )

    def test_execute_single_department_success(self):
        """Test execute with single department registration success"""
        # Arrange
        department_vo = self.create_department_vo("Engineering", "Software development department", 101)
        in_dto = DepartmentRegistInDto(departmentList=[department_vo])

        # Mock repository to return successfully created department
        mock_department = Mock(spec=Department)
        self.mock_repository.create_department.return_value = mock_department

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, DepartmentRegistOutDto)
        assert result.departmentCount == 1
        self.mock_repository.create_department.assert_called_once_with(
            name="Engineering",
            description="Software development department",
            manager_id=101
        )

    def test_execute_multiple_departments_success(self):
        """Test execute with multiple departments registration success"""
        # Arrange
        department_vo_list = [
            self.create_department_vo("Engineering", "Software development", 101),
            self.create_department_vo("Marketing", "Marketing and sales", 102),
            self.create_department_vo("HR", "Human resources", 103)
        ]
        in_dto = DepartmentRegistInDto(departmentList=department_vo_list)

        # Mock repository to return successfully created departments
        mock_department = Mock(spec=Department)
        self.mock_repository.create_department.return_value = mock_department

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, DepartmentRegistOutDto)
        assert result.departmentCount == 3
        assert self.mock_repository.create_department.call_count == 3

        # Verify each department was created with correct parameters
        call_args_list = self.mock_repository.create_department.call_args_list

        # First department
        first_call = call_args_list[0][1]  # kwargs
        assert first_call['name'] == "Engineering"
        assert first_call['description'] == "Software development"
        assert first_call['manager_id'] == 101

        # Second department
        second_call = call_args_list[1][1]  # kwargs
        assert second_call['name'] == "Marketing"
        assert second_call['description'] == "Marketing and sales"
        assert second_call['manager_id'] == 102

        # Third department
        third_call = call_args_list[2][1]  # kwargs
        assert third_call['name'] == "HR"
        assert third_call['description'] == "Human resources"
        assert third_call['manager_id'] == 103

    def test_execute_empty_department_list(self):
        """Test execute with empty department list"""
        # Arrange
        in_dto = DepartmentRegistInDto(departmentList=[])

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, DepartmentRegistOutDto)
        assert result.departmentCount == 0
        self.mock_repository.create_department.assert_not_called()

    def test_execute_department_with_minimal_fields(self):
        """Test execute with department having only required fields"""
        # Arrange
        department_vo = DepartmentVo(
            name="Minimal Department"
            # description and manager_id default to None
            # is_active defaults to True
        )
        in_dto = DepartmentRegistInDto(departmentList=[department_vo])

        # Mock repository
        mock_department = Mock(spec=Department)
        self.mock_repository.create_department.return_value = mock_department

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, DepartmentRegistOutDto)
        assert result.departmentCount == 1

        # Verify the repository was called with None values for optional fields
        call_kwargs = self.mock_repository.create_department.call_args[1]
        assert call_kwargs['name'] == "Minimal Department"
        assert call_kwargs['description'] is None
        assert call_kwargs['manager_id'] is None

    def test_execute_department_with_none_description(self):
        """Test execute with department having None description"""
        # Arrange
        department_vo = DepartmentVo(
            name="Test Department",
            description=None,
            manager_id=101
        )
        in_dto = DepartmentRegistInDto(departmentList=[department_vo])

        # Mock repository
        mock_department = Mock(spec=Department)
        self.mock_repository.create_department.return_value = mock_department

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, DepartmentRegistOutDto)
        assert result.departmentCount == 1

        # Verify description is None
        call_kwargs = self.mock_repository.create_department.call_args[1]
        assert call_kwargs['name'] == "Test Department"
        assert call_kwargs['description'] is None
        assert call_kwargs['manager_id'] == 101

    def test_execute_department_with_none_manager_id(self):
        """Test execute with department having None manager_id"""
        # Arrange
        department_vo = self.create_department_vo("No Manager Department", manager_id=None)
        in_dto = DepartmentRegistInDto(departmentList=[department_vo])

        # Mock repository
        mock_department = Mock(spec=Department)
        self.mock_repository.create_department.return_value = mock_department

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, DepartmentRegistOutDto)
        assert result.departmentCount == 1

        # Verify manager_id is None
        call_kwargs = self.mock_repository.create_department.call_args[1]
        assert call_kwargs['manager_id'] is None

    def test_execute_department_repository_exception(self):
        """Test execute handles repository exceptions correctly"""
        # Arrange
        department_vo = self.create_department_vo("Test Department")
        in_dto = DepartmentRegistInDto(departmentList=[department_vo])

        # Mock repository to raise exception
        self.mock_repository.create_department.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.execute(in_dto)

        assert str(exc_info.value) == "Database error"
        self.mock_repository.create_department.assert_called_once()

    def test_execute_partial_failure_with_multiple_departments(self):
        """Test execute with partial failure in multiple departments"""
        # Arrange
        department_vo_list = [
            self.create_department_vo("Engineering"),
            self.create_department_vo("Failing Department"),
            self.create_department_vo("HR")
        ]
        in_dto = DepartmentRegistInDto(departmentList=department_vo_list)

        # Mock repository: first succeeds, second fails, third never called due to exception
        mock_department = Mock(spec=Department)
        self.mock_repository.create_department.side_effect = [
            mock_department,  # First call succeeds
            Exception("Database error"),  # Second call fails
        ]

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.service.execute(in_dto)

        assert str(exc_info.value) == "Database error"
        # Only first two departments should have been attempted
        assert self.mock_repository.create_department.call_count == 2

    def test_execute_with_special_characters_in_names(self):
        """Test execute with special characters in department names"""
        # Arrange
        department_vo_list = [
            self.create_department_vo("R&D Department", "Research & Development"),
            self.create_department_vo("Sales/Marketing", "Sales and Marketing combined"),
            self.create_department_vo("IT-Support", "Information Technology Support")
        ]
        in_dto = DepartmentRegistInDto(departmentList=department_vo_list)

        # Mock repository
        mock_department = Mock(spec=Department)
        self.mock_repository.create_department.return_value = mock_department

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, DepartmentRegistOutDto)
        assert result.departmentCount == 3

        # Verify special characters are preserved
        call_args_list = self.mock_repository.create_department.call_args_list
        assert call_args_list[0][1]['name'] == "R&D Department"
        assert call_args_list[0][1]['description'] == "Research & Development"
        assert call_args_list[1][1]['name'] == "Sales/Marketing"
        assert call_args_list[1][1]['description'] == "Sales and Marketing combined"
        assert call_args_list[2][1]['name'] == "IT-Support"
        assert call_args_list[2][1]['description'] == "Information Technology Support"

    def test_execute_with_different_manager_ids(self):
        """Test execute with various manager ID values"""
        # Arrange
        department_vo_list = [
            self.create_department_vo("Dept1", manager_id=1),
            self.create_department_vo("Dept2", manager_id=999),
            self.create_department_vo("Dept3", manager_id=0),
            self.create_department_vo("Dept4", manager_id=None)
        ]
        in_dto = DepartmentRegistInDto(departmentList=department_vo_list)

        # Mock repository
        mock_department = Mock(spec=Department)
        self.mock_repository.create_department.return_value = mock_department

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, DepartmentRegistOutDto)
        assert result.departmentCount == 4

        # Verify manager IDs are preserved correctly
        call_args_list = self.mock_repository.create_department.call_args_list
        assert call_args_list[0][1]['manager_id'] == 1
        assert call_args_list[1][1]['manager_id'] == 999
        assert call_args_list[2][1]['manager_id'] == 0
        assert call_args_list[3][1]['manager_id'] is None

    def test_post_init_method(self):
        """Test that __post_init__ method initializes logger correctly"""
        # Act & Assert - should not raise any exceptions
        self.service.__post_init__()
        assert hasattr(self.service, 'logger')

    @patch('business.department_regist_service.logging.getLogger')
    def test_logging_calls_success(self, mock_get_logger):
        """Test that appropriate logging calls are made for successful registration"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        self.service.__post_init__()

        department_vo = self.create_department_vo("Engineering")
        in_dto = DepartmentRegistInDto(departmentList=[department_vo])

        mock_department = Mock(spec=Department)
        self.mock_repository.create_department.return_value = mock_department

        # Act
        self.service.execute(in_dto)

        # Assert
        mock_logger.info.assert_called()
        # Should have at least: start, per-department, count, and completion messages
        assert mock_logger.info.call_count >= 4

    @patch('business.department_regist_service.logging.getLogger')
    def test_logging_calls_failure(self, mock_get_logger):
        """Test that appropriate logging calls are made for failed registration"""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        self.service.__post_init__()

        department_vo = self.create_department_vo("Failing Department")
        in_dto = DepartmentRegistInDto(departmentList=[department_vo])

        # Mock repository to raise exception
        self.mock_repository.create_department.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            self.service.execute(in_dto)

        # Verify error logging was called
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        assert "Failed to register department Failing Department" in error_call_args
        assert "Database error" in error_call_args

    def test_repository_method_call_parameters(self):
        """Test that repository create_department method is called with correct parameter types"""
        # Arrange
        department_vo = DepartmentVo(
            name="Test Department",
            description="Test Description",
            manager_id=5,
            is_active=True
        )
        in_dto = DepartmentRegistInDto(departmentList=[department_vo])

        # Mock repository
        mock_department = Mock(spec=Department)
        self.mock_repository.create_department.return_value = mock_department

        # Act
        result = self.service.execute(in_dto)

        # Assert
        self.mock_repository.create_department.assert_called_once()

        # Get the parameters that were passed to create_department
        call_kwargs = self.mock_repository.create_department.call_args[1]

        # Verify parameter types and values
        assert isinstance(call_kwargs['name'], str)
        assert isinstance(call_kwargs['description'], str)
        assert isinstance(call_kwargs['manager_id'], int)

        assert call_kwargs['name'] == "Test Department"
        assert call_kwargs['description'] == "Test Description"
        assert call_kwargs['manager_id'] == 5

    def test_long_department_names_and_descriptions(self):
        """Test execute with long department names and descriptions"""
        # Arrange
        long_name = "Very Long Department Name With Multiple Words And Details" * 3
        long_description = "This is a very long description for a department that contains many details about what this department does and its responsibilities." * 5

        department_vo = DepartmentVo(
            name=long_name,
            description=long_description,
            manager_id=101
        )
        in_dto = DepartmentRegistInDto(departmentList=[department_vo])

        # Mock repository
        mock_department = Mock(spec=Department)
        self.mock_repository.create_department.return_value = mock_department

        # Act
        result = self.service.execute(in_dto)

        # Assert
        assert isinstance(result, DepartmentRegistOutDto)
        assert result.departmentCount == 1

        # Verify long strings are preserved
        call_kwargs = self.mock_repository.create_department.call_args[1]
        assert call_kwargs['name'] == long_name
        assert call_kwargs['description'] == long_description

    def test_in_dto_validation(self):
        """Test that DepartmentRegistInDto accepts the expected structure"""
        # Arrange
        department_vo_list = [
            self.create_department_vo("Dept1"),
            self.create_department_vo("Dept2")
        ]

        # Act
        in_dto = DepartmentRegistInDto(departmentList=department_vo_list)

        # Assert
        assert isinstance(in_dto, DepartmentRegistInDto)
        assert len(in_dto.departmentList) == 2
        assert in_dto.departmentList[0].name == "Dept1"
        assert in_dto.departmentList[1].name == "Dept2"

    def test_out_dto_structure(self):
        """Test that DepartmentRegistOutDto has the expected structure"""
        # Act
        out_dto = DepartmentRegistOutDto(departmentCount=8)

        # Assert
        assert isinstance(out_dto, DepartmentRegistOutDto)
        assert out_dto.departmentCount == 8


if __name__ == "__main__":
    pytest.main([__file__])
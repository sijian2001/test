import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List, Optional
import sys
import os
from sqlalchemy.orm import Session

# Add the project root directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.domain.repository.test1.department_repository import DepartmentRepository
from app.domain.model.test1.department import Department


class TestDepartmentRepository:
    """Unit tests for DepartmentRepository class"""

    def setup_method(self):
        """Setup method called before each test"""
        # Create a mock Session directly
        self.mock_session = Mock(spec=Session)

        # Create DepartmentRepository instance with mocked session
        self.repository = DepartmentRepository(session=self.mock_session)

    def create_mock_department(self, dept_id: int, name: str, description: str = None, manager_id: int = None) -> Department:
        """Helper method to create mock Department objects"""
        department = Mock(spec=Department)
        department.id = dept_id
        department.name = name
        department.description = description or f"Description for {name}"
        department.manager_id = manager_id
        department.is_active = True
        department.created_at = "2025-09-17 17:47:03"
        department.updated_at = "2025-09-17 17:47:03"
        return department

    def test_get_all_departments_success(self):
        """Test get_all_departments returns all departments"""
        # Arrange
        mock_departments = [
            self.create_mock_department(1, "Engineering", "Software development", 101),
            self.create_mock_department(2, "Marketing", "Marketing and sales", 102),
            self.create_mock_department(3, "HR", "Human resources", 103)
        ]
        self.mock_session.query.return_value.all.return_value = mock_departments

        # Act
        result = self.repository.get_all_departments()

        # Assert
        assert result == mock_departments
        assert len(result) == 3
        # Verify session.query was called with Department model
        self.mock_session.query.assert_called_once()
        self.mock_session.query.return_value.all.assert_called_once()

    def test_get_all_departments_empty_result(self):
        """Test get_all_departments returns empty list when no departments found"""
        # Arrange
        self.mock_session.query.return_value.all.return_value = []

        # Act
        result = self.repository.get_all_departments()

        # Assert
        assert result == []
        assert len(result) == 0
        # Verify session.query was called with Department model
        self.mock_session.query.assert_called_once()

    def test_get_department_by_id_success(self):
        """Test get_department_by_id returns department when found"""
        # Arrange
        dept_id = 1
        mock_department = self.create_mock_department(1, "Engineering")
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_department

        # Act
        result = self.repository.get_department_by_id(dept_id)

        # Assert
        assert result == mock_department
        assert result.id == dept_id
        # Verify session.query was called with Department model
        self.mock_session.query.assert_called_once()
        self.mock_session.query.assert_called_once_with(Department)

    def test_get_department_by_id_not_found(self):
        """Test get_department_by_id returns None when department not found"""
        # Arrange
        dept_id = 999
        self.mock_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.repository.get_department_by_id(dept_id)

        # Assert
        assert result is None
        # Verify session.query was called with Department model
        self.mock_session.query.assert_called_once()

    def test_create_department_success(self):
        """Test create_department creates new department successfully"""
        # Arrange
        name = "New Department"
        description = "A new department"
        manager_id = 101

        mock_department = self.create_mock_department(4, name, description, manager_id)

        # Mock session.add, commit, refresh
        self.mock_session.add = Mock()
        self.mock_session.flush = Mock()
        self.mock_session.refresh = Mock()

        # Act
        with patch('app.domain.repository.test1.department_repository.Department') as mock_dept_class:
            mock_dept_class.return_value = mock_department
            result = self.repository.create_department(name, description, manager_id)

            # Assert
            assert result == mock_department
            mock_dept_class.assert_called_once_with(
                name=name,
                description=description,
                manager_id=manager_id
            )
            self.mock_session.add.assert_called_once_with(mock_department)
            self.mock_session.flush.assert_called_once()
            self.mock_session.refresh.assert_called_once_with(mock_department)

    def test_create_department_with_minimal_params(self):
        """Test create_department with only required parameters"""
        # Arrange
        name = "Minimal Department"

        mock_department = self.create_mock_department(5, name)

        self.mock_session.add = Mock()
        self.mock_session.flush = Mock()
        self.mock_session.refresh = Mock()

        # Act
        with patch('app.domain.repository.test1.department_repository.Department') as mock_dept_class:
            mock_dept_class.return_value = mock_department
            result = self.repository.create_department(name)

            # Assert
            assert result == mock_department
            mock_dept_class.assert_called_once_with(
                name=name,
                description=None,
                manager_id=None
            )

    def test_update_department_success(self):
        """Test update_department updates existing department successfully"""
        # Arrange
        dept_id = 1
        updated_name = "Updated Department"
        updated_description = "Updated description"
        updated_manager_id = 102

        mock_department = self.create_mock_department(dept_id, "Original Department")
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_department
        self.mock_session.flush = Mock()
        self.mock_session.refresh = Mock()

        # Act
        result = self.repository.update_department(
            dept_id, updated_name, updated_description, updated_manager_id
        )

        # Assert
        assert result == mock_department
        assert mock_department.name == updated_name
        assert mock_department.description == updated_description
        assert mock_department.manager_id == updated_manager_id
        self.mock_session.flush.assert_called_once()
        self.mock_session.refresh.assert_called_once_with(mock_department)

    def test_update_department_partial_update(self):
        """Test update_department with partial updates (only some fields)"""
        # Arrange
        dept_id = 1
        updated_name = "Updated Department"

        mock_department = self.create_mock_department(dept_id, "Original Department")
        original_description = mock_department.description
        original_manager_id = mock_department.manager_id

        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_department
        self.mock_session.flush = Mock()
        self.mock_session.refresh = Mock()

        # Act
        result = self.repository.update_department(dept_id, name=updated_name)

        # Assert
        assert result == mock_department
        assert mock_department.name == updated_name
        assert mock_department.description == original_description  # Should remain unchanged
        assert mock_department.manager_id == original_manager_id  # Should remain unchanged

    def test_update_department_not_found(self):
        """Test update_department returns None when department not found"""
        # Arrange
        dept_id = 999
        self.mock_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.repository.update_department(dept_id, name="New Name")

        # Assert
        assert result is None
        # Verify session.query was called with Department model
        self.mock_session.query.assert_called_once()

    def test_update_department_with_none_description(self):
        """Test update_department handles description=None correctly"""
        # Arrange
        dept_id = 1
        # Create a real-like object to track attribute changes
        class MockDepartment:
            def __init__(self):
                self.id = dept_id
                self.name = "Test Department"
                self.description = "Original description"
                self.manager_id = 101

        mock_department = MockDepartment()
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_department
        self.mock_session.flush = Mock()
        self.mock_session.refresh = Mock()

        # Act
        result = self.repository.update_department(dept_id, description=None)

        # Assert
        assert result == mock_department
        # When description=None is explicitly passed, the condition "if description is not None" is False
        # So the description is NOT updated and remains at its original value
        assert mock_department.description == "Original description"
        self.mock_session.flush.assert_called_once()
        self.mock_session.refresh.assert_called_once_with(mock_department)

    def test_update_department_with_manager_id_none(self):
        """Test update_department handles manager_id=None correctly"""
        # Arrange
        dept_id = 1
        mock_department = self.create_mock_department(dept_id, "Test Department")
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_department
        self.mock_session.flush = Mock()
        self.mock_session.refresh = Mock()

        # Act
        result = self.repository.update_department(dept_id, manager_id=None)

        # Assert
        assert result == mock_department
        assert mock_department.manager_id is None

    def test_delete_department_success(self):
        """Test delete_department marks department as inactive successfully"""
        # Arrange
        dept_id = 1
        mock_department = self.create_mock_department(dept_id, "Test Department")
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_department
        self.mock_session.flush = Mock()

        # Act
        result = self.repository.delete_department(dept_id)

        # Assert
        assert result is True
        assert mock_department.is_active is False
        self.mock_session.flush.assert_called_once()

    def test_delete_department_not_found(self):
        """Test delete_department returns False when department not found"""
        # Arrange
        dept_id = 999
        self.mock_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.repository.delete_department(dept_id)

        # Assert
        assert result is False
        # Session is directly injected, so no get_session call needed
        self.mock_session.query.assert_called_once()

    def test_post_init_method(self):
        """Test that __post_init__ method can be called without errors"""
        # Act & Assert - should not raise any exceptions
        self.repository.__post_init__()

    def test_session_called_for_all_methods(self):
        """Test that session methods are called correctly for all repository methods"""
        # Setup mocks for read operations
        self.mock_session.query.return_value.all.return_value = []

        # Create a mock department for update and delete operations
        mock_department = Mock()
        mock_department.id = 1
        mock_department.name = "Test Department"

        # Set up different return values for different calls
        query_mock = Mock()
        filter_mock = Mock()
        first_mock = Mock()

        # For get_department_by_id - return None (not found)
        # For update_department and delete_department - return mock_department (found)
        first_mock.side_effect = [None, mock_department, mock_department]
        filter_mock.first = first_mock
        query_mock.filter.return_value = filter_mock
        query_mock.all.return_value = []
        self.mock_session.query.return_value = query_mock

        # Call all methods
        self.repository.get_all_departments()
        self.repository.get_department_by_id(1)

        with patch('app.domain.repository.test1.department_repository.Department') as mock_dept_class:
            mock_dept_class.return_value = Mock()
            self.repository.create_department("Test")

        self.repository.update_department(1, name="Test")
        self.repository.delete_department(1)

        # Assert session methods were called appropriately
        # query should be called for read operations and update/delete (4 times total):
        # get_all_departments, get_department_by_id, update_department, delete_department
        assert self.mock_session.query.call_count == 4
        # add should be called once (create_department)
        self.mock_session.add.assert_called_once()
        # commit should be called for create, update, and delete (3 times)
        assert self.mock_session.flush.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__])
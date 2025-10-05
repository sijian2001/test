import pytest
from unittest.mock import Mock, MagicMock, patch, call
import sys
import os

# Add the project root directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.business.decorators.transactional import Transactional
from app.business.decorators.database_enum import Database


class TestTransactional:
    """Unit tests for Transactional decorator"""

    def setup_method(self):
        """Setup method called before each test"""
        # モックセッションの作成
        self.mock_session = Mock()
        self.mock_session.begin = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.rollback = Mock()
        self.mock_session.close = Mock()

    def test_init_with_database_enum(self):
        """Test initialization with Database enum"""
        # Act
        decorator = Transactional(database=Database.TEST1)

        # Assert
        assert decorator.database == Database.TEST1
        assert decorator.read_only is False
        assert decorator.rollback_for == (Exception,)
        assert decorator.no_rollback_for == ()

    def test_init_with_database_string(self):
        """Test initialization with database string"""
        # Act
        decorator = Transactional(database='test1')

        # Assert
        assert decorator.database == Database.TEST1

    def test_init_with_invalid_database_string(self):
        """Test initialization with invalid database string raises ValueError"""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            Transactional(database='invalid_db')

        assert "Invalid database name: invalid_db" in str(exc_info.value)

    def test_init_with_invalid_database_type(self):
        """Test initialization with invalid database type raises TypeError"""
        # Act & Assert
        with pytest.raises(TypeError) as exc_info:
            Transactional(database=123)

        assert "database must be Database enum or str" in str(exc_info.value)

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters"""
        # Act
        decorator = Transactional(
            database=Database.TEST2,
            read_only=True,
            rollback_for=(ValueError, TypeError),
            no_rollback_for=(KeyError,)
        )

        # Assert
        assert decorator.database == Database.TEST2
        assert decorator.read_only is True
        assert decorator.rollback_for == (ValueError, TypeError)
        assert decorator.no_rollback_for == (KeyError,)

    def test_should_rollback_with_rollback_for_exception(self):
        """Test _should_rollback returns True for exception in rollback_for"""
        # Arrange
        decorator = Transactional(
            database=Database.TEST1,
            rollback_for=(ValueError, TypeError)
        )

        # Act & Assert
        assert decorator._should_rollback(ValueError("test")) is True
        assert decorator._should_rollback(TypeError("test")) is True

    def test_should_rollback_with_no_rollback_for_exception(self):
        """Test _should_rollback returns False for exception in no_rollback_for"""
        # Arrange
        decorator = Transactional(
            database=Database.TEST1,
            rollback_for=(Exception,),
            no_rollback_for=(KeyError,)
        )

        # Act & Assert
        # no_rollback_forが優先される
        assert decorator._should_rollback(KeyError("test")) is False

    def test_should_rollback_with_unspecified_exception(self):
        """Test _should_rollback returns False for exception not in rollback_for"""
        # Arrange
        decorator = Transactional(
            database=Database.TEST1,
            rollback_for=(ValueError,)
        )

        # Act & Assert
        # rollback_forに含まれないのでFalse
        assert decorator._should_rollback(TypeError("test")) is False

    def test_successful_execution_commits_transaction(self):
        """Test that successful method execution commits the transaction"""
        # Arrange
        with patch('app.business.decorators.transactional.SessionHolder') as mock_holder:
            mock_holder.get_session.return_value = self.mock_session

            @Transactional(database=Database.TEST1)
            def test_method(self):
                return "success"

            instance = Mock()

            # Act
            result = test_method(instance)

            # Assert
            assert result == "success"
            self.mock_session.begin.assert_called_once()
            self.mock_session.commit.assert_called_once()
            self.mock_session.rollback.assert_not_called()
            self.mock_session.close.assert_called_once()

    def test_exception_triggers_rollback(self):
        """Test that exception triggers rollback when in rollback_for"""
        # Arrange
        with patch('app.business.decorators.transactional.SessionHolder') as mock_holder:
            mock_holder.get_session.return_value = self.mock_session

            @Transactional(database=Database.TEST1, rollback_for=(ValueError,))
            def test_method(self):
                raise ValueError("test error")

            instance = Mock()

            # Act & Assert
            with pytest.raises(ValueError):
                test_method(instance)

            self.mock_session.begin.assert_called_once()
            self.mock_session.commit.assert_not_called()
            self.mock_session.rollback.assert_called_once()
            self.mock_session.close.assert_called_once()

    def test_exception_not_in_rollback_for_does_not_rollback(self):
        """Test that exception not in rollback_for does not trigger rollback"""
        # Arrange
        with patch('app.business.decorators.transactional.SessionHolder') as mock_holder:
            mock_holder.get_session.return_value = self.mock_session

            @Transactional(database=Database.TEST1, rollback_for=(ValueError,))
            def test_method(self):
                raise TypeError("test error")

            instance = Mock()

            # Act & Assert
            with pytest.raises(TypeError):
                test_method(instance)

            self.mock_session.begin.assert_called_once()
            # rollback_forに含まれないのでコミットを試みる
            self.mock_session.commit.assert_called_once()
            self.mock_session.rollback.assert_not_called()
            self.mock_session.close.assert_called_once()

    def test_no_rollback_for_takes_precedence(self):
        """Test that no_rollback_for takes precedence over rollback_for"""
        # Arrange
        with patch('app.business.decorators.transactional.SessionHolder') as mock_holder:
            mock_holder.get_session.return_value = self.mock_session

            @Transactional(
                database=Database.TEST1,
                rollback_for=(Exception,),
                no_rollback_for=(KeyError,)
            )
            def test_method(self):
                raise KeyError("test error")

            instance = Mock()

            # Act & Assert
            with pytest.raises(KeyError):
                test_method(instance)

            self.mock_session.begin.assert_called_once()
            # no_rollback_forが優先されるのでコミット
            self.mock_session.commit.assert_called_once()
            self.mock_session.rollback.assert_not_called()
            self.mock_session.close.assert_called_once()

    def test_session_closed_even_on_exception(self):
        """Test that session is closed even when exception occurs"""
        # Arrange
        with patch('app.business.decorators.transactional.SessionHolder') as mock_holder:
            mock_holder.get_session.return_value = self.mock_session

            @Transactional(database=Database.TEST1)
            def test_method(self):
                raise RuntimeError("test error")

            instance = Mock()

            # Act & Assert
            with pytest.raises(RuntimeError):
                test_method(instance)

            # finallyブロックでクローズされる
            self.mock_session.close.assert_called_once()

    def test_read_only_parameter(self):
        """Test that read_only parameter is properly set"""
        # Arrange
        decorator = Transactional(database=Database.TEST1, read_only=True)

        # Assert
        assert decorator.read_only is True

    def test_decorator_with_test2_database(self):
        """Test decorator works with TEST2 database"""
        # Arrange
        with patch('app.business.decorators.transactional.SessionHolder') as mock_holder:
            mock_holder.get_session.return_value = self.mock_session

            @Transactional(database=Database.TEST2)
            def test_method(self):
                return "test2_result"

            instance = Mock()

            # Act
            result = test_method(instance)

            # Assert
            assert result == "test2_result"
            mock_holder.get_session.assert_called_once_with('test2')
            self.mock_session.commit.assert_called_once()
            self.mock_session.close.assert_called_once()

    def test_method_arguments_are_preserved(self):
        """Test that decorated method receives all arguments correctly"""
        # Arrange
        with patch('app.business.decorators.transactional.SessionHolder') as mock_holder:
            mock_holder.get_session.return_value = self.mock_session

            @Transactional(database=Database.TEST1)
            def test_method(self, arg1, arg2, kwarg1=None):
                return f"{arg1}-{arg2}-{kwarg1}"

            instance = Mock()

            # Act
            result = test_method(instance, "a", "b", kwarg1="c")

            # Assert
            assert result == "a-b-c"

    def test_functools_wraps_preserves_metadata(self):
        """Test that functools.wraps preserves function metadata"""
        # Arrange
        @Transactional(database=Database.TEST1)
        def test_method(self):
            """Test method docstring"""
            pass

        # Assert
        assert test_method.__name__ == "test_method"
        assert test_method.__doc__ == "Test method docstring"

    def test_multiple_exceptions_in_rollback_for(self):
        """Test decorator with multiple exception types in rollback_for"""
        # Arrange
        with patch('app.business.decorators.transactional.SessionHolder') as mock_holder:
            mock_holder.get_session.return_value = self.mock_session

            @Transactional(
                database=Database.TEST1,
                rollback_for=(ValueError, TypeError, KeyError)
            )
            def test_method_value_error(self):
                raise ValueError("test")

            @Transactional(
                database=Database.TEST1,
                rollback_for=(ValueError, TypeError, KeyError)
            )
            def test_method_type_error(self):
                raise TypeError("test")

            instance = Mock()

            # Act & Assert - ValueError
            with pytest.raises(ValueError):
                test_method_value_error(instance)
            assert self.mock_session.rollback.call_count == 1

            # Reset mock
            self.mock_session.reset_mock()

            # Act & Assert - TypeError
            with pytest.raises(TypeError):
                test_method_type_error(instance)
            assert self.mock_session.rollback.call_count == 1

    def test_default_rollback_for_catches_all_exceptions(self):
        """Test that default rollback_for=(Exception,) catches all exceptions"""
        # Arrange
        with patch('app.business.decorators.transactional.SessionHolder') as mock_holder:
            mock_holder.get_session.return_value = self.mock_session

            @Transactional(database=Database.TEST1)
            def test_method(self):
                raise RuntimeError("unexpected error")

            instance = Mock()

            # Act & Assert
            with pytest.raises(RuntimeError):
                test_method(instance)

            # デフォルトのrollback_for=(Exception,)ですべての例外でロールバック
            self.mock_session.rollback.assert_called_once()

    def test_session_holder_called_with_correct_database(self):
        """Test that SessionHolder is called with correct database identifier"""
        # Arrange
        with patch('app.business.decorators.transactional.SessionHolder') as mock_holder:
            mock_holder.get_session.return_value = self.mock_session

            @Transactional(database=Database.TEST1)
            def test_method(self):
                return "result"

            instance = Mock()

            # Act
            test_method(instance)

            # Assert
            mock_holder.get_session.assert_called_once_with('test1')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

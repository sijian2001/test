import pytest
from unittest.mock import Mock, MagicMock, patch
from business.decorators.session_manager import SessionManager
from business.decorators.database_enum import Database
from domain.session_holder import SessionHolder


class TestSessionManager:
    """SessionManagerデコレーターの単体テスト"""

    def setup_method(self):
        """各テストの前にSessionHolderをクリア"""
        SessionHolder.clear()

    def teardown_method(self):
        """各テストの後にSessionHolderをクリア"""
        SessionHolder.clear()

    def test_session_manager_with_enum_test1(self):
        """TEST1 Enumを使用した正常系テスト"""
        # Arrange
        mock_instance = Mock()
        mock_session = Mock()

        # SessionHolderにモックセッションファクトリーを登録
        SessionHolder.register('test1', lambda: mock_session)

        @SessionManager(database=Database.TEST1)
        def dummy_method(self):
            return "success"

        # Act
        result = dummy_method(mock_instance)

        # Assert
        assert result == "success"
        mock_session.begin.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_session_manager_with_enum_test2(self):
        """TEST2 Enumを使用した正常系テスト"""
        # Arrange
        mock_instance = Mock()
        mock_session = Mock()

        # SessionHolderにモックセッションファクトリーを登録
        SessionHolder.register('test2', lambda: mock_session)

        @SessionManager(database=Database.TEST2)
        def dummy_method(self):
            return "success"

        # Act
        result = dummy_method(mock_instance)

        # Assert
        assert result == "success"
        mock_session.begin.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_session_manager_with_string_test1(self):
        """文字列'test1'を使用した正常系テスト（後方互換性）"""
        # Arrange
        mock_instance = Mock()
        mock_session = Mock()

        # SessionHolderにモックセッションファクトリーを登録
        SessionHolder.register('test1', lambda: mock_session)

        @SessionManager(database='test1')
        def dummy_method(self):
            return "success"

        # Act
        result = dummy_method(mock_instance)

        # Assert
        assert result == "success"
        mock_session.begin.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_session_manager_with_string_test2(self):
        """文字列'test2'を使用した正常系テスト（後方互換性）"""
        # Arrange
        mock_instance = Mock()
        mock_session = Mock()

        # SessionHolderにモックセッションファクトリーを登録
        SessionHolder.register('test2', lambda: mock_session)

        @SessionManager(database='test2')
        def dummy_method(self):
            return "success"

        # Act
        result = dummy_method(mock_instance)

        # Assert
        assert result == "success"
        mock_session.begin.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_session_manager_invalid_string_database(self):
        """無効な文字列データベース名のテスト"""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid database name: invalid"):
            @SessionManager(database='invalid')
            def dummy_method(self):
                pass

    def test_session_manager_invalid_type(self):
        """無効な型のデータベース指定のテスト"""
        # Act & Assert
        with pytest.raises(TypeError, match="database must be Database enum or str"):
            @SessionManager(database=123)
            def dummy_method(self):
                pass

    def test_session_manager_rollback_on_exception(self):
        """例外発生時のロールバックテスト"""
        # Arrange
        mock_instance = Mock()
        mock_session = Mock()

        # SessionHolderにモックセッションファクトリーを登録
        SessionHolder.register('test1', lambda: mock_session)

        @SessionManager(database=Database.TEST1)
        def dummy_method(self):
            raise RuntimeError("Test error")

        # Act & Assert
        with pytest.raises(RuntimeError, match="Test error"):
            dummy_method(mock_instance)

        mock_session.begin.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()
        mock_session.close.assert_called_once()

    def test_session_manager_logging_test1(self, caplog):
        """TEST1データベースのログ出力テスト"""
        # Arrange
        mock_instance = Mock()
        mock_session = Mock()

        # SessionHolderにモックセッションファクトリーを登録
        SessionHolder.register('test1', lambda: mock_session)

        @SessionManager(database=Database.TEST1)
        def dummy_method(self):
            return "success"

        # Act
        with caplog.at_level('INFO'):
            dummy_method(mock_instance)

        # Assert
        assert "Session started for test1 and transaction began" in caplog.text
        assert "Transaction committed successfully for test1" in caplog.text
        assert "Session closed for test1" in caplog.text

    def test_session_manager_logging_test2(self, caplog):
        """TEST2データベースのログ出力テスト"""
        # Arrange
        mock_instance = Mock()
        mock_session = Mock()

        # SessionHolderにモックセッションファクトリーを登録
        SessionHolder.register('test2', lambda: mock_session)

        @SessionManager(database=Database.TEST2)
        def dummy_method(self):
            return "success"

        # Act
        with caplog.at_level('INFO'):
            dummy_method(mock_instance)

        # Assert
        assert "Session started for test2 and transaction began" in caplog.text
        assert "Transaction committed successfully for test2" in caplog.text
        assert "Session closed for test2" in caplog.text

    def test_session_manager_logging_on_error(self, caplog):
        """エラー発生時のログ出力テスト"""
        # Arrange
        mock_instance = Mock()
        mock_session = Mock()

        # SessionHolderにモックセッションファクトリーを登録
        SessionHolder.register('test1', lambda: mock_session)

        @SessionManager(database=Database.TEST1)
        def dummy_method(self):
            raise ValueError("Test error")

        # Act & Assert
        with caplog.at_level('ERROR'):
            with pytest.raises(ValueError):
                dummy_method(mock_instance)

        assert "Transaction rolled back due to error for test1" in caplog.text
        assert "Error in dummy_method: Test error" in caplog.text

    def test_session_manager_with_args_and_kwargs(self):
        """引数とキーワード引数を持つメソッドのテスト"""
        # Arrange
        mock_instance = Mock()
        mock_session = Mock()

        # SessionHolderにモックセッションファクトリーを登録
        SessionHolder.register('test1', lambda: mock_session)

        @SessionManager(database=Database.TEST1)
        def dummy_method(self, arg1, arg2, kwarg1=None, kwarg2=None):
            return f"{arg1}-{arg2}-{kwarg1}-{kwarg2}"

        # Act
        result = dummy_method(mock_instance, "a", "b", kwarg1="c", kwarg2="d")

        # Assert
        assert result == "a-b-c-d"
        mock_session.begin.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_session_manager_preserves_function_metadata(self):
        """デコレートされた関数のメタデータが保持されることを確認"""
        # Arrange & Act
        @SessionManager(database=Database.TEST1)
        def dummy_method(self):
            """Test docstring"""
            pass

        # Assert
        assert dummy_method.__name__ == "dummy_method"
        assert dummy_method.__doc__ == "Test docstring"

    def test_session_manager_session_close_on_commit_error(self):
        """コミット時にエラーが発生してもセッションがクローズされることを確認"""
        # Arrange
        mock_instance = Mock()
        mock_session = Mock()
        mock_session.commit.side_effect = RuntimeError("Commit failed")

        # SessionHolderにモックセッションファクトリーを登録
        SessionHolder.register('test1', lambda: mock_session)

        @SessionManager(database=Database.TEST1)
        def dummy_method(self):
            return "success"

        # Act & Assert
        with pytest.raises(RuntimeError, match="Commit failed"):
            dummy_method(mock_instance)

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_session_manager_valid_database_names_in_error_message(self):
        """エラーメッセージに有効なデータベース名が含まれることを確認"""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            @SessionManager(database='invalid_db')
            def dummy_method(self):
                pass

        error_message = str(exc_info.value)
        assert "Invalid database name: invalid_db" in error_message
        assert "test1" in error_message
        assert "test2" in error_message

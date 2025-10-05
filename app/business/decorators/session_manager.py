import functools
import logging
from typing import Callable, Any, Union
from sqlalchemy.orm import Session
from app.business.decorators.database_enum import Database
from app.domain.session_holder import SessionHolder

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Decorator for automatic session and transaction management

    This decorator provides automatic transaction management for service methods.
    It eliminates the need for manual session handling in business logic.

    The decorator automatically:
    - Starts a session before method execution
    - Commits the transaction on successful completion
    - Rolls back the transaction on error
    - Closes the session in all cases

    Usage:
        @SessionManager(database=Database.TEST1)
        def some_method(self, input_dto: InDto) -> OutDto:
            # Your business logic here
            # Session is automatically managed
            pass

    Args:
        database: Database identifier (Database.TEST1 for user management,
                  Database.TEST2 for product management)

    Raises:
        ValueError: If an invalid database name is provided

    Example:
        @dataclass
        class UserService:
            db_session: DatabaseSession = inject

            @SessionManager(database=Database.TEST1)
            def create_user(self, user_dto: UserDto) -> UserDto:
                # Session lifecycle is managed automatically
                return self.user_repository.create(user_dto)
    """

    def __init__(self, database: Union[Database, str]) -> None:
        """
        Initialize SessionManager decorator

        Args:
            database: Database identifier (Database enum or string 'test1'/'test2')

        Raises:
            ValueError: If database name is invalid
        """
        # 文字列の場合はEnumに変換を試みる
        if isinstance(database, str):
            try:
                self.database = Database(database)
            except ValueError:
                valid_options = [db.value for db in Database]
                raise ValueError(
                    f"Invalid database name: {database}. "
                    f"Valid options: {valid_options}"
                )
        elif isinstance(database, Database):
            self.database = database
        else:
            raise TypeError(
                f"database must be Database enum or str, got {type(database).__name__}"
            )

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator implementation

        Args:
            func: Function to be decorated

        Returns:
            Wrapped function
        """
        @functools.wraps(func)
        def wrapper(instance: Any, *args, **kwargs) -> Any:
            """
            Execute the decorated method with session management

            Args:
                instance: Instance that owns the decorated method
                *args: Method arguments
                **kwargs: Method keyword arguments

            Returns:
                Method execution result
            """
            session = None
            try:
                # Get session from SessionHolder
                session = SessionHolder.get_session(self.database.value)
                session.begin()
                logger.info(
                    f"Session started for {self.database.value} and transaction began"
                )

                # Execute the decorated method
                result = func(instance, *args, **kwargs)

                # Commit on success
                session.commit()
                logger.info(
                    f"Transaction committed successfully for {self.database.value}"
                )
                return result

            except Exception as e:
                # Rollback on error
                if session:
                    session.rollback()
                    logger.error(
                        f"Transaction rolled back due to error for {self.database.value}"
                    )
                logger.error(f"Error in {func.__name__}: {str(e)}")
                raise
            finally:
                # Close session
                if session:
                    session.close()
                    logger.info(f"Session closed for {self.database.value}")

        return wrapper

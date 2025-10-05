import functools
import logging
from typing import Callable, Any, Union, Tuple, Type
from sqlalchemy.orm import Session
from app.business.decorators.database_enum import Database
from app.domain.session_holder import SessionHolder

logger = logging.getLogger(__name__)


class Transactional:
    """
    Decorator for declarative transaction management (inspired by Spring @Transactional)

    This decorator provides Spring Boot-like declarative transaction management
    for service methods. It offers more fine-grained control over transaction
    behavior compared to SessionManager.

    Key features:
    - Automatic transaction begin/commit/rollback
    - Read-only transaction optimization hints
    - Custom rollback rules for specific exceptions
    - Explicit transaction boundary declaration

    The decorator automatically:
    - Starts a transaction before method execution
    - Commits the transaction on successful completion
    - Rolls back on specified exceptions
    - Closes the session in all cases (finally block)

    IMPORTANT - no_rollback_for behavior:
        When an exception in no_rollback_for occurs, the decorator will:
        1. COMMIT the transaction (preserving database changes)
        2. RE-RAISE the exception to the caller

        This allows business logic to handle "expected" exceptions while
        preserving partial database changes. Use with caution.

        Example:
            @Transactional(
                database=Database.TEST1,
                rollback_for=(Exception,),
                no_rollback_for=(KeyError,)
            )
            def process_optional_data(self, dto):
                self.repository.save_required_data(dto.required)  # This commits
                self.repository.save_optional_data(dto.optional)  # May raise KeyError

            # Result: required_data is committed, KeyError propagates to caller

    IMPORTANT - read_only parameter:
        Currently used for logging and documentation purposes only.
        SQLAlchemy does not have explicit read-only transaction support.

        Future enhancements may include:
        - Using read-only database connections
        - Disabling flush operations
        - Optimizing query execution plans

        For now, treat this as a hint for developers and future optimization.

    Usage:
        @Transactional(database=Database.TEST1)
        def create_user(self, input_dto: CreateUserDto) -> UserDto:
            # Transaction is automatically managed
            # Commits on success, rolls back on exception
            pass

        @Transactional(database=Database.TEST1, read_only=True)
        def get_users(self, input_dto: GetUsersDto) -> List[UserDto]:
            # Read-only transaction (optimization hint for future use)
            pass

        @Transactional(
            database=Database.TEST1,
            rollback_for=(ValueError, TypeError),
            no_rollback_for=(KeyError,)
        )
        def process_data(self, dto: DataDto) -> ResultDto:
            # Rolls back only for ValueError and TypeError
            # KeyError commits changes but still propagates exception
            pass

    Args:
        database: Database identifier (Database.TEST1 or Database.TEST2)
        read_only: If True, marks transaction as read-only (currently logging only)
        rollback_for: Tuple of exception types that trigger rollback
        no_rollback_for: Tuple of exception types that should NOT trigger rollback
                        (takes precedence over rollback_for; commits but re-raises)

    Raises:
        ValueError: If an invalid database name is provided
        TypeError: If database parameter has invalid type

    Comparison with SessionManager:
    - SessionManager: Simple automatic session/transaction management (deprecated)
    - Transactional: Spring-like declarative transaction control with custom rules

    Example:
        @dataclass
        class UserService:
            user_repository: UserRepository = inject

            @Transactional(database=Database.TEST1)
            def create_user(self, dto: CreateUserDto) -> UserDto:
                # Explicit transaction boundary
                # Auto-commit on success, auto-rollback on exception
                return self.user_repository.create(dto)

            @Transactional(database=Database.TEST1, read_only=True)
            def get_all_users(self) -> List[UserDto]:
                # Read-only hint (future optimization)
                return self.user_repository.get_all()
    """

    def __init__(
        self,
        database: Union[Database, str],
        read_only: bool = False,
        rollback_for: Tuple[Type[Exception], ...] = (Exception,),
        no_rollback_for: Tuple[Type[Exception], ...] = ()
    ) -> None:
        """
        Initialize Transactional decorator

        Args:
            database: Database identifier
                     RECOMMENDED: Use Database.TEST1 or Database.TEST2 enum
                     LEGACY: String 'test1' or 'test2' (for backward compatibility)
            read_only: If True, marks transaction as read-only
                      NOTE: Currently used for logging only, not enforced by SQLAlchemy
            rollback_for: Exception types that trigger rollback (default: all Exception)
            no_rollback_for: Exception types that should NOT trigger rollback
                            WARNING: Commits transaction but re-raises exception

        Raises:
            ValueError: If database name is invalid
            TypeError: If database parameter has invalid type
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

        self.read_only = read_only
        self.rollback_for = rollback_for
        self.no_rollback_for = no_rollback_for

    def _should_rollback(self, exception: Exception) -> bool:
        """
        Determine if the given exception should trigger a rollback

        Rollback decision logic:
        1. If exception is in no_rollback_for -> Do NOT rollback
        2. If exception is in rollback_for -> DO rollback
        3. Otherwise -> Do NOT rollback

        Args:
            exception: Exception instance to check

        Returns:
            True if should rollback, False otherwise

        Example:
            >>> decorator = Transactional(
            ...     database=Database.TEST1,
            ...     rollback_for=(ValueError,),
            ...     no_rollback_for=(KeyError,)
            ... )
            >>> decorator._should_rollback(KeyError())  # False (no_rollback_for)
            >>> decorator._should_rollback(ValueError())  # True (rollback_for)
            >>> decorator._should_rollback(TypeError())  # False (not in rollback_for)
        """
        # no_rollback_forが最優先（ロールバックしない）
        if isinstance(exception, self.no_rollback_for):
            logger.debug(
                f"Exception {type(exception).__name__} is in no_rollback_for, "
                f"will NOT rollback"
            )
            return False

        # rollback_forに該当すればロールバック
        if isinstance(exception, self.rollback_for):
            logger.debug(
                f"Exception {type(exception).__name__} is in rollback_for, "
                f"will rollback"
            )
            return True

        # どちらにも該当しなければロールバックしない
        logger.debug(
            f"Exception {type(exception).__name__} is not in rollback rules, "
            f"will NOT rollback"
        )
        return False

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator implementation

        Args:
            func: Function to be decorated

        Returns:
            Wrapped function with transaction management

        Implementation follows Spring @Transactional pattern:
        1. Begin transaction
        2. Execute method
        3. Commit on success / Rollback on exception
        4. Close session (finally)
        """
        @functools.wraps(func)
        def wrapper(instance: Any, *args, **kwargs) -> Any:
            """
            Execute the decorated method with transaction management

            Args:
                instance: Instance that owns the decorated method
                *args: Method arguments
                **kwargs: Method keyword arguments

            Returns:
                Method execution result

            Raises:
                Any exception raised by the decorated method
            """
            session = None
            try:
                # Get session from SessionHolder
                session = SessionHolder.get_session(self.database.value)
                session.begin()

                # ログ出力: トランザクション開始
                mode = "read-only" if self.read_only else "read-write"
                logger.info(
                    f"Transaction started for {self.database.value} "
                    f"(mode: {mode}, method: {func.__name__})"
                )

                # Execute the decorated method
                result = func(instance, *args, **kwargs)

                # Commit on success
                session.commit()
                logger.info(
                    f"Transaction committed successfully for {self.database.value} "
                    f"(method: {func.__name__})"
                )
                return result

            except Exception as e:
                # ロールバック判定
                if session and self._should_rollback(e):
                    session.rollback()
                    # rollback_forに含まれる例外は想定内のロールバック（INFO）
                    # それ以外は予期しないロールバック（WARNING）
                    log_level = logging.INFO if isinstance(e, self.rollback_for) else logging.WARNING
                    logger.log(
                        log_level,
                        f"Transaction rolled back due to {type(e).__name__} "
                        f"for {self.database.value} (method: {func.__name__}): {str(e)}"
                    )
                elif session:
                    # ロールバックしない場合でもコミットは試みる
                    try:
                        session.commit()
                        logger.info(
                            f"Transaction committed despite {type(e).__name__} "
                            f"(exception in no_rollback_for) for {self.database.value}"
                        )
                    except Exception as commit_error:
                        logger.error(
                            f"Failed to commit after no-rollback exception: "
                            f"{str(commit_error)}"
                        )

                # 元の例外を再送出
                logger.error(f"Error in {func.__name__}: {str(e)}")
                raise

            finally:
                # セッションクローズ（Spring BootのEntityManager.close()に相当）
                if session:
                    session.close()
                    logger.info(
                        f"Session closed for {self.database.value} "
                        f"(method: {func.__name__})"
                    )

        return wrapper

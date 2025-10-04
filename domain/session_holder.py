from typing import Dict, Callable
from sqlalchemy.orm import Session


class SessionHolder:
    """
    Singleton class for centralized session factory management

    This class provides centralized session factory management.
    Each database registers its session factory, which can then be
    accessed by SessionManager and other components.

    Example:
        # Register session factories during initialization
        SessionHolder.register('test1', test1_session.get_session)
        SessionHolder.register('test2', test2_session.get_session)

        # Get session in SessionManager
        session = SessionHolder.get_session('test1')
    """

    _session_factories: Dict[str, Callable[[], Session]] = {}

    @classmethod
    def register(cls, database: str, session_factory: Callable[[], Session]) -> None:
        """
        Register a session factory for a specific database

        Args:
            database: Database identifier (e.g., 'test1', 'test2')
            session_factory: Callable that returns a Session instance

        Raises:
            ValueError: If database is already registered
        """
        if database in cls._session_factories:
            raise ValueError(
                f"Session factory for database '{database}' is already registered"
            )
        cls._session_factories[database] = session_factory

    @classmethod
    def get_session(cls, database: str) -> Session:
        """
        Get a session for the specified database

        Args:
            database: Database identifier

        Returns:
            Session instance

        Raises:
            ValueError: If database is not registered
        """
        if database not in cls._session_factories:
            raise ValueError(
                f"No session factory registered for database '{database}'. "
                f"Available databases: {list(cls._session_factories.keys())}"
            )
        return cls._session_factories[database]()

    @classmethod
    def is_registered(cls, database: str) -> bool:
        """
        Check if a database is registered

        Args:
            database: Database identifier

        Returns:
            True if registered, False otherwise
        """
        return database in cls._session_factories

    @classmethod
    def clear(cls) -> None:
        """
        Clear all registered session factories (mainly for testing)
        """
        cls._session_factories.clear()

    @classmethod
    def get_registered_databases(cls) -> list:
        """
        Get list of registered databases

        Returns:
            List of registered database identifiers
        """
        return list(cls._session_factories.keys())

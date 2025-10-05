import warnings
import functools
from injector import inject, singleton
from dataclasses import dataclass
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from .model.test1.base import Base as Test1Base
from .model.test1.user import User
from .model.test1.department import Department
from .model.test1.user_info import UserInfo
from .model.test2.base import Base as Test2Base
from .model.test2.category import Category
from .model.test2.product import Product
from .session_holder import SessionHolder
import yaml
import os


def deprecated(reason):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """
    def decorator(func_or_class):
        if isinstance(func_or_class, type):
            # If it's a class, warn when it's instantiated
            original_init = func_or_class.__init__

            @functools.wraps(original_init)
            def new_init(self, *args, **kwargs):
                warnings.warn(
                    f"{func_or_class.__name__} is deprecated: {reason}",
                    DeprecationWarning,
                    stacklevel=2
                )
                original_init(self, *args, **kwargs)

            func_or_class.__init__ = new_init
            return func_or_class
        else:
            # If it's a function
            @functools.wraps(func_or_class)
            def new_func(*args, **kwargs):
                warnings.warn(
                    f"{func_or_class.__name__} is deprecated: {reason}",
                    DeprecationWarning,
                    stacklevel=2
                )
                return func_or_class(*args, **kwargs)
            return new_func
    return decorator


@singleton
class DatabaseConfig:
    def __init__(self, config_path: str = "db.yaml"):
        self.config_path = config_path
        self._load_config()

    def _load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                # Support both old and new config format
                db_config = config.get('database', {})
                if 'test1' in db_config:
                    # New format with multiple databases
                    self.test1_url = db_config.get('test1', {}).get('url', "mysql+pymysql://user1:1234@localhost:3306/test1")
                    self.test1_echo = db_config.get('test1', {}).get('echo', True)
                    self.test2_url = db_config.get('test2', {}).get('url', "mysql+pymysql://user2:1234@localhost:3306/test2")
                    self.test2_echo = db_config.get('test2', {}).get('echo', True)
                else:
                    # Old format for backward compatibility
                    self.test1_url = db_config.get('url', "mysql+pymysql://user1:1234@localhost:3306/test1")
                    self.test1_echo = db_config.get('echo', True)
                    self.test2_url = "mysql+pymysql://user2:1234@localhost:3306/test2"
                    self.test2_echo = True
        else:
            self.test1_url = "mysql+pymysql://user1:1234@localhost:3306/test1"
            self.test1_echo = True
            self.test2_url = "mysql+pymysql://user2:1234@localhost:3306/test2"
            self.test2_echo = True

# Test1 Database Classes
@inject
@singleton
@dataclass
class Test1DatabaseEngine:
    config: DatabaseConfig

    def __post_init__(self):
        # Create engine for test1 database
        self.engine = create_engine(self.config.test1_url, echo=self.config.test1_echo)
        # Create tables for test1 database
        Test1Base.metadata.create_all(self.engine)

    def get_engine(self) -> Engine:
        return self.engine

@inject
@singleton
class Test1DatabaseSession(Session):
    def __init__(self, engine: Test1DatabaseEngine):
        super().__init__(bind=engine.get_engine())
        self.engine = engine
        # SessionHolderに登録
        self._register_to_session_holder()

    def _register_to_session_holder(self):
        """Register session factory to SessionHolder"""
        if not SessionHolder.is_registered('test1'):
            session_factory = sessionmaker(bind=self.engine.get_engine())
            SessionHolder.register('test1', session_factory)

# Test2 Database Classes
@inject
@singleton
@dataclass
class Test2DatabaseEngine:
    config: DatabaseConfig

    def __post_init__(self):
        # Create engine for test2 database
        self.engine = create_engine(self.config.test2_url, echo=self.config.test2_echo)
        # Create tables for test2 database
        Test2Base.metadata.create_all(self.engine)

    def get_engine(self) -> Engine:
        return self.engine

@inject
@singleton
class Test2DatabaseSession(Session):
    def __init__(self, engine: Test2DatabaseEngine):
        super().__init__(bind=engine.get_engine())
        self.engine = engine
        # SessionHolderに登録
        self._register_to_session_holder()

    def _register_to_session_holder(self):
        """Register session factory to SessionHolder"""
        if not SessionHolder.is_registered('test2'):
            session_factory = sessionmaker(bind=self.engine.get_engine())
            SessionHolder.register('test2', session_factory)

# Legacy classes for backward compatibility (deprecated)
#
# MIGRATION GUIDE:
# ================
# The DatabaseEngine and DatabaseSession classes are deprecated and will be removed in a future version.
# Please migrate to the new session classes as follows:
#
# OLD WAY (deprecated):
# ```python
# from app.domain.database import DatabaseSession
#
# @inject
# @dataclass
# class SomeRepository:
#     db_session: DatabaseSession
#
#     def some_method(self):
#         session = self.db_session.get_session("test1")  # or "test2"
#         return session.query(SomeModel).all()
# ```
#
# NEW WAY (recommended):
# ```python
# from app.domain.database import Test1DatabaseSession, Test2DatabaseSession
#
# @inject
# @dataclass
# class SomeRepository:
#     session: Test1DatabaseSession  # or Test2DatabaseSession
#
#     def some_method(self):
#         return self.session.query(SomeModel).all()
# ```
#
# Benefits of the new approach:
# - Better type safety and IDE support
# - Simplified code with direct session access
# - Clearer separation between different databases
# - Follows modern SQLAlchemy patterns
#
# Migration steps:
# 1. Replace DatabaseSession with Test1DatabaseSession or Test2DatabaseSession
# 2. Change parameter name from 'db_session' to 'session' for consistency
# 3. Remove get_session() calls and use the session directly
# 4. Update unit tests to mock Session directly instead of DatabaseSession
@deprecated("Use Test1DatabaseEngine and Test2DatabaseEngine instead. This class will be removed in a future version.")
@inject
@singleton
@dataclass
class DatabaseEngine:
    config: DatabaseConfig

    def __post_init__(self):
        # Create engines for both databases
        self.test1_engine = create_engine(self.config.test1_url, echo=self.config.test1_echo)
        self.test2_engine = create_engine(self.config.test2_url, echo=self.config.test2_echo)

        # Create tables for both databases
        Test1Base.metadata.create_all(self.test1_engine)
        Test2Base.metadata.create_all(self.test2_engine)

    def get_engine(self, database: str = "test1") -> Engine:
        if database == "test1":
            return self.test1_engine
        elif database == "test2":
            return self.test2_engine
        else:
            raise ValueError(f"Unknown database: {database}")

@deprecated("Use Test1DatabaseSession and Test2DatabaseSession instead. This class will be removed in a future version.")
@inject
@singleton
@dataclass
class DatabaseSession:
    engine: DatabaseEngine

    def __post_init__(self):
        self.test1_session_factory = sessionmaker(bind=self.engine.get_engine("test1"))
        self.test2_session_factory = sessionmaker(bind=self.engine.get_engine("test2"))

    def get_session(self, database: str = "test1") -> Session:
        if database == "test1":
            return self.test1_session_factory()
        elif database == "test2":
            return self.test2_session_factory()
        else:
            raise ValueError(f"Unknown database: {database}")


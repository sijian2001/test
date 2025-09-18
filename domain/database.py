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
import yaml
import os

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


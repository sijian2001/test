from injector import inject, singleton
from dataclasses import dataclass
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from .model.base import Base
from .model.user import User
from .model.department import Department
from .model.user_info import UserInfo
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
                self.database_url = config.get('database', {}).get('url', "mysql+pymysql://user1:1234@localhost:3306/test1")
                self.echo = config.get('database', {}).get('echo', True)
        else:
            self.database_url = "mysql+pymysql://user1:1234@localhost:3306/test1"
            self.echo = True

@inject
@singleton
@dataclass
class DatabaseEngine:
    config: DatabaseConfig

    def __post_init__(self):
        self.engine = create_engine(self.config.database_url, echo=self.config.echo)
        Base.metadata.create_all(self.engine)
    
    def get_engine(self) -> Engine:
        return self.engine

@inject
@singleton
@dataclass
class DatabaseSession:
    engine: DatabaseEngine

    def __post_init__(self):
        self.session_factory = sessionmaker(bind=self.engine.get_engine())
    
    def get_session(self) -> Session:
        return self.session_factory()


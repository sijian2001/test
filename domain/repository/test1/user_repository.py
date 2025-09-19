from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from injector import inject

from domain.database import Test1DatabaseSession
from domain.model.test1.user import User


class AbstractUserRepository(ABC):
    @abstractmethod
    def get_all_users(self) -> List[User]:
        pass
    
    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def create_user(self, username: str, email: str, password_hash: str, first_name: str = None, last_name: str = None, department_id: int = None) -> User:
        pass
    
    @abstractmethod
    def update_user(self, user_id: int, username: str = None, email: str = None, first_name: str = None, last_name: str = None, department_id: int = None) -> Optional[User]:
        pass


@inject
@dataclass
class UserRepository(AbstractUserRepository):
    db_session: Test1DatabaseSession

    def __post_init__(self):
        pass
    
    def get_all_users(self) -> List[User]:
        session = self.db_session
        return session.query(User).all()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        session = self.db_session
        return session.query(User).filter(User.id == user_id).first()
    
    def create_user(self, username: str, email: str, password_hash: str, first_name: str = None, last_name: str = None, department_id: int = None) -> User:
        session = self.db_session
        user = User(username=username, email=email, password_hash=password_hash, first_name=first_name, last_name=last_name, department_id=department_id)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    def update_user(self, user_id: int, username: str = None, email: str = None, first_name: str = None, last_name: str = None, department_id: int = None) -> Optional[User]:
        session = self.db_session
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            if username:
                user.username = username
            if email:
                user.email = email
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if department_id is not None:
                user.department_id = department_id
            session.commit()
            session.refresh(user)
        return user
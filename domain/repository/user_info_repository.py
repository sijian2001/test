from abc import ABC, abstractmethod
from typing import List, Optional
from injector import inject
from dataclasses import dataclass
from ..model.user_info import UserInfo
from ..database import DatabaseSession


class AbstractUserInfoRepository(ABC):
    @abstractmethod
    def get_all_user_info(self) -> List[UserInfo]:
        pass

    @abstractmethod
    def get_user_info_by_id(self, user_id: int) -> Optional[UserInfo]:
        pass

    @abstractmethod
    def get_user_info_by_username(self, username: str) -> Optional[UserInfo]:
        pass

    @abstractmethod
    def get_user_info_by_department(self, department_name: str) -> List[UserInfo]:
        pass


@inject
@dataclass
class UserInfoRepository(AbstractUserInfoRepository):
    db_session: DatabaseSession

    def __post_init__(self):
        pass

    def get_all_user_info(self) -> List[UserInfo]:
        session = self.db_session.get_session()
        return session.query(UserInfo).all()

    def get_user_info_by_id(self, user_id: int) -> Optional[UserInfo]:
        session = self.db_session.get_session()
        return session.query(UserInfo).filter(UserInfo.user_id == user_id).first()

    def get_user_info_by_username(self, username: str) -> Optional[UserInfo]:
        session = self.db_session.get_session()
        return session.query(UserInfo).filter(UserInfo.username == username).first()

    def get_user_info_by_department(self, department_name: str) -> List[UserInfo]:
        session = self.db_session.get_session()
        return session.query(UserInfo).filter(UserInfo.department_name == department_name).all()
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from injector import inject

from domain.database import Test1DatabaseSession
from domain.model.test1.user_info import UserInfo


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
    session: Test1DatabaseSession

    def __post_init__(self):
        pass

    def get_all_user_info(self) -> List[UserInfo]:
        return self.session.query(UserInfo).all()

    def get_user_info_by_id(self, user_id: int) -> Optional[UserInfo]:
        return self.session.query(UserInfo).filter(UserInfo.user_id == user_id).first()

    def get_user_info_by_username(self, username: str) -> Optional[UserInfo]:
        return self.session.query(UserInfo).filter(UserInfo.username == username).first()

    def get_user_info_by_department(self, department_name: str) -> List[UserInfo]:
        return self.session.query(UserInfo).filter(UserInfo.department_name == department_name).all()
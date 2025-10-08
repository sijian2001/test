from dataclasses import dataclass
from typing import Optional


@dataclass
class ActiveUserVo:
    """Value Object for ActiveUser"""
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department_id: Optional[int] = None

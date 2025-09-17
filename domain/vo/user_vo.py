from dataclasses import dataclass
from typing import Optional

@dataclass
class UserVo:
    username: str
    email: str
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department_id: Optional[int] = None
    is_active: bool = True
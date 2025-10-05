from dataclasses import dataclass
from typing import Optional

@dataclass
class DepartmentVo:
    name: str
    description: Optional[str] = None
    manager_id: Optional[int] = None
    is_active: bool = True
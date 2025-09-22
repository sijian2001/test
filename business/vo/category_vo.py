from dataclasses import dataclass
from typing import Optional


@dataclass
class CategoryVo:
    category_name: str
    category_description: Optional[str]
    parent_category_id: Optional[int]
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from injector import inject
import logging
from business.abstract_service import AbstractService, AbstractInDto, AbstractOutDto
from domain.repository.test2.category_repository import CategoryRepository
from domain.model.test2.category import Category
from domain.vo.category_vo import CategoryVo

logging.basicConfig(level=logging.INFO)

@dataclass
class CategoryRegistInDto(AbstractInDto):
    categoryList: List[CategoryVo]

@dataclass
class CategoryRegistOutDto(AbstractOutDto):
    categoryCount: int

class AbstractCategoryRegistService(AbstractService):
    @abstractmethod
    def execute(self, in_dto: CategoryRegistInDto) -> CategoryRegistOutDto:
        pass

@inject
@dataclass
class CategoryRegistService(AbstractCategoryRegistService):
    category_repository: CategoryRepository

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    def execute(self, in_dto: CategoryRegistInDto) -> CategoryRegistOutDto:
        self.logger.info("=== Starting Category Registration ===")

        categories_registered = 0
        for category_vo in in_dto.categoryList:
            try:
                # Create Category entity from VO
                category = Category(
                    category_name=category_vo.category_name,
                    category_description=category_vo.category_description,
                    parent_category_id=category_vo.parent_category_id
                )

                self.category_repository.create_category(category)
                categories_registered += 1
                self.logger.info(f"Registered category: {category_vo.category_name}")
            except Exception as e:
                self.logger.error(f"Failed to register category {category_vo.category_name}: {str(e)}")
                raise

        self.logger.info(f"Successfully registered {categories_registered} categories")
        self.logger.info("=== Category Registration Completed Successfully ===")

        # Create and return result DTO
        result_dto = CategoryRegistOutDto(
            categoryCount=categories_registered
        )

        return result_dto
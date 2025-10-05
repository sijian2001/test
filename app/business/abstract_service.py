from abc import ABC, abstractmethod

class AbstractInDto(ABC):
    """Base class for all input DTOs"""
    pass

class AbstractOutDto(ABC):
    """Base class for all output DTOs"""
    pass

class AbstractService(ABC):
    @abstractmethod
    def execute(self, in_dto: AbstractInDto) -> AbstractOutDto:
        pass
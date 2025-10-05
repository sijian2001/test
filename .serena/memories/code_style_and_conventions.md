# Code Style and Conventions

## Language-Specific Rules

### Documentation and Comments
1. **Docstrings**: Must be written in **English**
2. **Embedded code descriptions** (e.g., for pytest, validation): Written in **English**
3. **Implementation comments** (explaining background/reasoning): Written in **Japanese**
4. **No emojis** should be used

### Japanese Text Formatting
- Do not include unnecessary spaces
- Correct: "Claude Code入門"
- Incorrect: "Claude Code 入門"

## Code Structure

### Service Layer (`business/`)
- All services inherit from `AbstractService`
- Implement unified interface: `execute(in_dto: AbstractInDto) -> AbstractOutDto`
- Use `@SessionManager` decorator for transaction management
- Use `@inject` and `@dataclass` for dependency injection

Example:
```python
from dataclasses import dataclass
from injector import inject
from business.decorators.session_manager import SessionManager

@dataclass
class UserRegistService(AbstractService):
    user_repository: UserRepository = inject
    
    @SessionManager(database='test1')
    def execute(self, in_dto: UserRegistInDto) -> UserRegistOutDto:
        # Implementation
        pass
```

### Repository Layer (`domain/repository/`)
- Organized by database: `test1/` and `test2/` subdirectories
- Use SQLAlchemy ORM for data access
- Inject appropriate database session: `Test1DatabaseSession` or `Test2DatabaseSession`

### Batch Layer (`batch/`)
- Inherit from base `Processor` class
- Handle CSV import/export operations

### Value Objects (`business/vo/`)
- Use `@dataclass` for DTOs
- Located in `business/vo/` directory
- Examples: `user_vo.py`, `product_vo.py`, `category_vo.py`, `department_vo.py`

## Dependency Injection
- Use `injector` library with `@inject` decorator
- Use `@dataclass` for class definition
- Singleton pattern for database connections and configurations
- Type-based dependency resolution

## Session Management
- Use `@SessionManager` decorator for database transactions
- Specify database: `@SessionManager(database='test1')` or `@SessionManager(database='test2')`
- Automatic commit/rollback with proper error handling
- Located in `business/decorators/session_manager.py`

## Database Session Migration
- Migrating from legacy `DatabaseSession.get_session(database)` pattern
- Use direct `Test1DatabaseSession` / `Test2DatabaseSession` injection in new code

## Naming Conventions
- Test files: `test_<component_name>.py`
- Repository files: `<entity>_repository.py`
- Service files: `<entity>_service.py` or `<action>_service.py`
- VO files: `<entity>_vo.py`
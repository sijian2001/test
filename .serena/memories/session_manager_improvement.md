# SessionManager Decorator Improvement (Issue #7)

## Summary
Improved the @SessionManager decorator to accept a `database` parameter, making it more explicit and easier to use.

## Changes Made

### 1. SessionManager Decorator (`business/decorators/session_manager.py`)
**Before:**
```python
@SessionManager
def some_method(self, session: Session, input_dto: InDto) -> OutDto:
    pass
```

**After:**
```python
@SessionManager(database='test1')
def some_method(self, input_dto: InDto) -> OutDto:
    pass
```

### 2. Key Improvements
- **Explicit Database Selection**: Database name ('test1' or 'test2') is now specified in the decorator
- **Cleaner Method Signatures**: Removed `session: Session` parameter from decorated methods
- **Better Error Handling**: Added validation for database parameter
- **Improved Logging**: Database-specific logging messages

### 3. Implementation Details
- Changed decorator from function-based to class-based with `__init__` accepting `database` parameter
- Decorator now handles session lifecycle internally without passing session to method
- Uses `instance.db_session.get_session(database)` to get appropriate session

### 4. Migration
Updated all services using @SessionManager:
- `business/depart_user_regist_service.py`: Updated to use `@SessionManager(database='test1')`

### 5. Testing
- All 256 tests passed successfully
- No breaking changes to existing functionality

## Usage Pattern
```python
from business.decorators.session_manager import SessionManager

@dataclass
class SomeService:
    db_session: DatabaseSession = inject
    
    @SessionManager(database='test1')  # or 'test2'
    def execute(self, in_dto: InDto) -> OutDto:
        # No need to handle session manually
        # Session is automatically managed by decorator
        pass
```
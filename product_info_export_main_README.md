# Product Info CSV Export - Logging Guide

## Overview

The `product_info_export_main.py` script supports detailed logging for debugging and understanding the application's behavior:
- **Injector Logging**: Trace dependency injection operations
- **SQLAlchemy Logging**: Trace SQL execution and database operations

Logging is configured via `logger.yaml` and controlled by environment variables.

## Configuration File: logger.yaml

The `logger.yaml` file centralizes all logging configurations:

```yaml
logger:
  # Root logger configuration
  root:
    level: INFO
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

  # Injector logger configuration
  # Enable with DEBUG_INJECTOR=true environment variable
  injector:
    level: DEBUG
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

  # SQLAlchemy logger configuration
  # Enable with DEBUG_SQL=true environment variable
  sqlalchemy:
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    # Engine logger: outputs SQL statements
    engine:
      level: INFO  # INFO: SQL statements only, DEBUG: SQL + result sets
    # Pool logger: outputs connection pool events
    pool:
      level: DEBUG
    # Dialects logger: outputs SQL dialect details
    dialects:
      level: DEBUG
    # ORM logger: outputs ORM internal operations
    orm:
      level: DEBUG
```

## Usage

### Normal Execution (Without Debug Logging)

```bash
python product_info_export_main.py
```

Output:
```
INFO:__main__:Starting Product Info CSV Export Application...
INFO:batch.product_info_csv_export_processor:=== Starting Product Info CSV Export Process ===
...
```

### Injector Debug Mode

Enable dependency injection tracing:

```bash
# On Linux/macOS/Git Bash
export DEBUG_INJECTOR=true && python product_info_export_main.py

# On Windows CMD
set DEBUG_INJECTOR=true && python product_info_export_main.py

# On Windows PowerShell
$env:DEBUG_INJECTOR="true"; python product_info_export_main.py
```

### SQLAlchemy Debug Mode

Enable SQL execution tracing:

```bash
# On Linux/macOS/Git Bash
export DEBUG_SQL=true && python product_info_export_main.py

# On Windows CMD
set DEBUG_SQL=true && python product_info_export_main.py

# On Windows PowerShell
$env:DEBUG_SQL="true"; python product_info_export_main.py
```

### Combined Debug Mode

Enable both Injector and SQLAlchemy logging:

```bash
# On Linux/macOS/Git Bash
export DEBUG_INJECTOR=true && export DEBUG_SQL=true && python product_info_export_main.py

# On Windows CMD
set DEBUG_INJECTOR=true && set DEBUG_SQL=true && python product_info_export_main.py

# On Windows PowerShell
$env:DEBUG_INJECTOR="true"; $env:DEBUG_SQL="true"; python product_info_export_main.py
```

## Debug Output Examples

### Injector Logging Output

When `DEBUG_INJECTOR=true` is set, you'll see detailed dependency injection traces:

```
INFO:__main__:Starting Product Info CSV Export Application...
INFO:__main__:Injector debug logging enabled

> Injector.get(<class 'ProductInfoCsvExportProcessorImpl'>) using <ClassProvider>
> Creating <class 'ProductInfoCsvExportProcessorImpl'> object
> Providing {'product_info_service': <class 'ProductInfoService'>}
>> Injector.get(<class 'ProductInfoService'>) using <ClassProvider>
>> Creating <class 'ProductInfoService'> object
>> Providing {'product_info_repository': <class 'ProductInfoRepository'>}
>>> Injector.get(<class 'ProductInfoRepository'>) using <ClassProvider>
>>> Creating <class 'ProductInfoRepository'> object
>>> Providing {'db_session': <class 'Test2DatabaseSession'>}
>>>> Injector.get(<class 'Test2DatabaseSession'>, scope=SingletonScope) using <ClassProvider>
>>>> Creating <class 'Test2DatabaseSession'> object
>>>> Providing {'engine': <class 'Test2DatabaseEngine'>}
>>>>> Injector.get(<class 'Test2DatabaseEngine'>, scope=SingletonScope) using <ClassProvider>
>>>>> Creating <class 'Test2DatabaseEngine'> object
>>>>> Providing {'config': <class 'DatabaseConfig'>}
>>>>>> Injector.get(<class 'DatabaseConfig'>, scope=SingletonScope) using <ClassProvider>
>>>>>> Creating <class 'DatabaseConfig'> object
>>>>>>  -> <DatabaseConfig object>
>>>>>  -> Test2DatabaseEngine(config=<DatabaseConfig object>)
>>>>  -> <Test2DatabaseSession object>
>>>  -> ProductInfoRepository(db_session=<Test2DatabaseSession object>)
>>  -> ProductInfoService(product_info_repository=ProductInfoRepository(...))
>  -> ProductInfoCsvExportProcessorImpl(product_info_service=ProductInfoService(...))
```

### SQLAlchemy Logging Output

When `DEBUG_SQL=true` is set, you'll see SQL execution details:

```
INFO:__main__:Starting Product Info CSV Export Application...
INFO:__main__:SQLAlchemy debug logging enabled

2025-10-05 01:00:00 - sqlalchemy.engine - INFO - SELECT DATABASE()
2025-10-05 01:00:00 - sqlalchemy.engine - INFO - [raw sql] {}
2025-10-05 01:00:00 - sqlalchemy.engine - INFO - SELECT @@sql_mode
2025-10-05 01:00:00 - sqlalchemy.engine - INFO - [raw sql] {}
2025-10-05 01:00:00 - sqlalchemy.engine - INFO - SELECT @@lower_case_table_names
2025-10-05 01:00:00 - sqlalchemy.engine - INFO - [raw sql] {}
2025-10-05 01:00:00 - sqlalchemy.pool - DEBUG - Created new connection <pymysql.connections.Connection object at 0x...>
2025-10-05 01:00:00 - sqlalchemy.engine - INFO - BEGIN (implicit)
2025-10-05 01:00:00 - sqlalchemy.engine - INFO - SELECT products.id, products.name, products.price, products.category_id
FROM products
2025-10-05 01:00:00 - sqlalchemy.engine - INFO - [generated in 0.00123s] {}
2025-10-05 01:00:00 - sqlalchemy.engine - INFO - COMMIT
2025-10-05 01:00:00 - sqlalchemy.pool - DEBUG - Connection <pymysql.connections.Connection object at 0x...> being returned to pool
```

## Dependency Tree Visualization

The injector logging indentation (`>`, `>>`, `>>>`, etc.) shows the depth of dependency injection:

```
ProductInfoCsvExportProcessorImpl
└── ProductInfoService
    └── ProductInfoRepository
        └── Test2DatabaseSession (Singleton)
            └── Test2DatabaseEngine (Singleton)
                └── DatabaseConfig (Singleton)
```

## Understanding the Logs

### Injector Logs

1. **Injector.get()**: Shows what's being requested
   - Interface/Class being resolved
   - Scope (NoScope, SingletonScope)
   - Provider type (ClassProvider, CallableProvider)

2. **Creating object**: Shows object instantiation
   - Class being created
   - Additional kwargs passed

3. **Providing**: Shows dependencies being injected
   - Parameter name and type
   - Function receiving the injection

4. **Result (->)**: Shows the created instance

5. **Singleton Behavior**: Notice that `DatabaseConfig`, `Test2DatabaseEngine`, and `Test2DatabaseSession` are created with `SingletonScope`:
   - They are created only once
   - Subsequent requests return the same instance

### SQLAlchemy Logs

1. **sqlalchemy.engine (INFO)**: SQL statements executed
   - Raw SQL queries
   - Query parameters
   - Execution time

2. **sqlalchemy.pool (DEBUG)**: Connection pool management
   - Connection creation
   - Connection checkout/checkin
   - Pool size changes

## Use Cases

### 1. Debugging Injection Issues

If you encounter dependency injection errors, enable injector logging:

```bash
DEBUG_INJECTOR=true python product_info_export_main.py
```

### 2. SQL Performance Analysis

Identify slow queries and optimize database access:

```bash
DEBUG_SQL=true python product_info_export_main.py
```

### 3. Understanding Application Architecture

Use both logs to visualize the complete application flow:

```bash
DEBUG_INJECTOR=true DEBUG_SQL=true python product_info_export_main.py
```

### 4. Troubleshooting Database Issues

Debug connection pool issues or transaction problems:

```bash
DEBUG_SQL=true python product_info_export_main.py
```

## Customizing Log Levels

Edit `logger.yaml` to customize logging behavior:

```yaml
logger:
  sqlalchemy:
    engine:
      level: DEBUG  # Change to DEBUG for detailed SQL + result sets
    pool:
      level: INFO   # Change to INFO to reduce connection pool noise
```

After editing, restart the application to apply changes.

## Disabling Logging

To disable debug logging, simply run without the environment variables:

```bash
python product_info_export_main.py
```

Or explicitly set to false:

```bash
DEBUG_INJECTOR=false DEBUG_SQL=false python product_info_export_main.py
```

## Integration with Other Tools

The logging system integrates seamlessly with:
- Application logging (batch processor logs)
- Custom business logic logging
- External log aggregation tools (e.g., ELK stack)

## Best Practices

1. **Development**: Enable `DEBUG_INJECTOR=true` and `DEBUG_SQL=true` during development
2. **Testing**: Use logging to verify dependency wiring and SQL execution
3. **Production**: Disable debug logging for performance
4. **Performance Tuning**: Use `DEBUG_SQL=true` to identify slow queries
5. **CI/CD**: Use debug logs in failing test cases for diagnosis

## Configuration Management

### Environment Variables Priority

Environment variables override `logger.yaml` settings:
1. `DEBUG_INJECTOR=true` → Enables injector logging regardless of `logger.yaml`
2. `DEBUG_SQL=true` → Enables SQLAlchemy logging regardless of `logger.yaml`

### Configuration File Location

The `logger.yaml` file must be in the same directory as `product_info_export_main.py`.

If the file is not found, default configurations are used with a warning:
```
WARNING:__main__:logger.yaml not found, using default configuration
```

## Related Files

- `logger.yaml` - Centralized logging configuration
- `examples/injector_logging_example.py` - Basic injector logging example
- `examples/README.md` - Comprehensive injector logging guide
- `product_info_export_main.py` - Main script with logging support

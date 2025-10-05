# Product Info CSV Export - Logging Guide

## Overview

The `product_info_export_main.py` script supports detailed logging for debugging and understanding the application's behavior:
- **Injector Logging**: Trace dependency injection operations
- **SQLAlchemy Logging**: Trace SQL execution and database operations

Logging is configured via `logger.yaml`.

## Configuration File: logger.yaml

The `logger.yaml` file centralizes all logging configurations:

```yaml
logger:
  # Root logger configuration
  root:
    level: INFO
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

  # File logging configuration (optional)
  file:
    enable: false  # Set to true to enable file logging with rotation
    path: "logs/application.log"
    max_bytes: 10485760  # 10MB
    backup_count: 5
    level: INFO
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

  # Injector logger configuration
  injector:
    enable: false  # Set to true to enable injector debug logging
    level: DEBUG
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

  # SQLAlchemy logger configuration
  sqlalchemy:
    enable: false  # Set to true to enable SQLAlchemy debug logging
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

## File Logging with Rotation

### Enable File Logging

To enable persistent file logging with automatic rotation:

```yaml
file:
  enable: true  # Change from false to true
  path: "logs/application.log"
  max_bytes: 10485760  # 10MB per file
  backup_count: 5  # Keep 5 backup files
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Rotation Behavior

- **Size-based rotation**: When the log file reaches `max_bytes`, it's automatically rotated
- **Backup files**: Old logs are renamed to `application.log.1`, `application.log.2`, etc.
- **Automatic cleanup**: Only `backup_count` files are kept; oldest are deleted
- **Total storage**: Maximum disk usage = `max_bytes × (backup_count + 1)`

Example with default settings:
- Max file size: 10MB
- Backup count: 5
- Total storage: 60MB (10MB × 6 files)

### Use Cases

- **Production environments**: Persistent logging for auditing and troubleshooting
- **Long-running processes**: Automatic log management without manual intervention
- **Compliance**: Maintaining historical logs for regulatory requirements

## Enabling Debug Logging

To enable debug logging, edit `logger.yaml` and set `enable: true`:

### Enable Injector Logging

```yaml
injector:
  enable: true  # Change from false to true
  level: DEBUG
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Enable SQLAlchemy Logging

```yaml
sqlalchemy:
  enable: true  # Change from false to true
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  # ...
```

### Enable Both Loggers

```yaml
injector:
  enable: true

sqlalchemy:
  enable: true
```

## Usage

### Normal Execution (Without Debug Logging)

```bash
python batch/product_info_export_main.py
```

Output:
```
INFO:__main__:Starting Product Info CSV Export Application...
INFO:batch.product_info_csv_export_processor:=== Starting Product Info CSV Export Process ===
...
```

### With Injector Logging Enabled

After setting `injector.enable: true` in `logger.yaml`:

```bash
python batch/product_info_export_main.py
```

Output will include detailed dependency injection traces:
```
INFO:__main__:Starting Product Info CSV Export Application...
INFO:utils.logger_utils:Injector debug logging enabled

> Injector.get(<class 'ProductInfoCsvExportProcessorImpl'>) using <ClassProvider>
> Creating <class 'ProductInfoCsvExportProcessorImpl'> object
> Providing {'product_info_service': <class 'ProductInfoService'>}
...
```

### With SQLAlchemy Logging Enabled

After setting `sqlalchemy.enable: true` in `logger.yaml`:

```bash
python batch/product_info_export_main.py
```

Output will include SQL execution details:
```
INFO:__main__:Starting Product Info CSV Export Application...
INFO:utils.logger_utils:SQLAlchemy debug logging enabled

2025-10-05 01:00:00 - sqlalchemy.engine - INFO - SELECT DATABASE()
2025-10-05 01:00:00 - sqlalchemy.engine - INFO - [raw sql] {}
2025-10-05 01:00:00 - sqlalchemy.pool - DEBUG - Created new connection <pymysql.connections.Connection object at 0x...>
...
```

## Debug Output Examples

### Injector Logging Output

When `injector.enable: true`, you'll see detailed dependency injection traces showing the complete dependency tree with indentation.

### SQLAlchemy Logging Output

When `sqlalchemy.enable: true`, you'll see SQL execution details including:
- SQL statements
- Query parameters
- Connection pool events
- Transaction management

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

Enable `injector.enable: true` in logger.yaml to trace dependency resolution.

### 2. SQL Performance Analysis

Enable `sqlalchemy.enable: true` to identify slow queries and optimize database access.

### 3. Understanding Application Architecture

Enable both loggers to visualize the complete application flow.

### 4. Troubleshooting Database Issues

Use SQLAlchemy logging to debug connection pool issues or transaction problems.

## Customizing Log Levels

Edit `logger.yaml` to customize logging behavior:

```yaml
logger:
  sqlalchemy:
    enable: true
    engine:
      level: DEBUG  # Change to DEBUG for detailed SQL + result sets
    pool:
      level: INFO   # Change to INFO to reduce connection pool noise
```

After editing, restart the application to apply changes.

## Disabling Logging

To disable debug logging, edit `logger.yaml` and set `enable: false`:

```yaml
injector:
  enable: false

sqlalchemy:
  enable: false
```

No need to change environment variables or restart the system—just edit the config file and run the application.

## Performance Impact

### SQLAlchemy Logging

**⚠️ Important Performance Considerations:**

- **DEBUG Level**: Setting `sqlalchemy.engine.level` to `DEBUG` outputs both SQL statements AND result sets
  - This can significantly impact performance when handling large datasets
  - Result set output adds substantial overhead for queries returning many rows
  - Memory usage increases as all results are formatted for logging

- **INFO Level**: Only outputs SQL statements (recommended for most debugging)
  - Minimal performance impact
  - Sufficient for identifying slow queries and execution patterns

**Performance Impact Examples:**

| Dataset Size | INFO Level Impact | DEBUG Level Impact |
|--------------|-------------------|-------------------|
| Small (< 100 rows) | Negligible (< 1%) | Minor (~5-10%) |
| Medium (100-1000 rows) | Negligible (< 2%) | Moderate (~15-25%) |
| Large (> 1000 rows) | Minor (~2-5%) | Significant (~30-50%) |

### Injector Logging

- **Minimal Impact**: Dependency injection logging occurs only during object creation
- Safe to enable in most scenarios
- Primary impact is increased log volume, not execution time

### Recommendations

1. **Development**: Enable both loggers with appropriate levels
2. **Testing**: Use INFO level for SQLAlchemy to verify query execution
3. **Production**: **ALWAYS set `enable: false`** for both loggers
4. **Performance Tuning**: Temporarily enable with INFO level to identify bottlenecks
5. **Large Datasets**: Avoid DEBUG level for SQLAlchemy engine logger

## Best Practices

1. **Development**: Enable both loggers during development for full visibility
2. **Testing**: Use logging to verify dependency wiring and SQL execution
3. **Production**: **Disable all debug logging** (`enable: false`) for optimal performance
4. **Performance Tuning**: Enable SQLAlchemy logging at INFO level to identify slow queries
5. **Debugging**: Enable specific loggers based on the issue type
6. **Large Datasets**: Never use DEBUG level for `sqlalchemy.engine` when processing large result sets

## Configuration Management

### Configuration File Location

The `logger.yaml` file must be in the project root directory (same directory as the main scripts).

If the file is not found, all debug logging is disabled with a warning:
```
WARNING:utils.logger_utils:logger.yaml not found, using default configuration
```

### Default Behavior

- If `logger.yaml` is missing: No debug logging
- If `enable` field is missing: Default is `false` (disabled)
- If level/format is missing: Uses sensible defaults

## Related Files

- `logger.yaml` - Centralized logging configuration
- `utils/logger_utils.py` - Shared logger utilities module
- `examples/injector_logging_example.py` - Basic injector logging example
- `examples/README.md` - Comprehensive injector logging guide

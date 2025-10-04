# Injector Logging Examples

## Overview

This directory contains examples demonstrating how to enable and use debug logging in the `python-injector` library for tracing dependency injection operations.

## Injector Logging Configuration

### Enable Debug Logging

```python
import logging

# Get the injector logger
injector_logger = logging.getLogger('injector')

# Set level to DEBUG
injector_logger.setLevel(logging.DEBUG)

# Add a handler
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
injector_logger.addHandler(handler)
```

### Available Log Messages

The injector library provides detailed debug logs for:

1. **`Injector.get()`** - Shows:
   - Interface being requested
   - Scope being used
   - Provider handling the request
   - Resolved result

2. **`create_object()`** - Shows:
   - Class being instantiated
   - Additional kwargs being passed

3. **`args_to_inject()`** - Shows:
   - Bindings being provided
   - Functions receiving injection

### Log Output Format

The debug logs use indentation (`>`, `>>`, `>>>`, etc.) to show the depth of the dependency tree:

```
> Injector.get(<class 'UserService'>) using <ClassProvider>
> Creating <class 'UserService'> object with {}
> Providing {'user_repository': <class 'UserRepository'>} for __init__
>> Injector.get(<class 'UserRepository'>) using <ClassProvider>
>> Creating <class 'UserRepository'> object with {}
>>> Injector.get(<class 'DatabaseConnection'>) using CallableProvider
>>>>Injector.get(<class 'DatabaseConfig'>) using CallableProvider (Singleton)
```

## Running the Examples

### Example 1: Basic Logging

```bash
python examples/injector_logging_example.py
```

This demonstrates:
- Dependency injection without logging
- Dependency injection with DEBUG logging enabled
- Singleton behavior verification

### Expected Output

```
=== Example 1: Without logging ===
Providing DatabaseConfig
Providing DatabaseConnection
Creating DB connection to prod-db.example.com:3306/production
Fetching users from database

=== Example 2: With DEBUG logging ===
Providing DatabaseConfig
Providing DatabaseConnection
Creating DB connection to prod-db.example.com:3306/production
Fetching users from database
2025-10-05 00:24:24 - injector - DEBUG - > Injector.get(<class 'UserService'>)
2025-10-05 00:24:24 - injector - DEBUG - > Creating <class 'UserService'> object
...
```

## Use Cases

### 1. Debugging Injection Issues

Enable logging to see exactly how dependencies are being resolved:

```python
logging.getLogger('injector').setLevel(logging.DEBUG)
injector = Injector([MyModule()])
service = injector.get(MyService)  # See full injection trace
```

### 2. Verifying Singleton Behavior

Check if singletons are being reused correctly:

```python
config1 = injector.get(DatabaseConfig)  # First creation logged
config2 = injector.get(DatabaseConfig)  # Reuse logged (no re-creation)
```

### 3. Understanding Dependency Trees

Visualize complex dependency hierarchies:

```
> UserService
>> UserRepository
>>> DatabaseConnection
>>>> DatabaseConfig (Singleton)
```

## Best Practices

1. **Development Only**: Enable debug logging only in development/testing environments
2. **Performance**: DEBUG logging adds overhead - disable in production
3. **Log Levels**: Use different levels for different scenarios:
   - `DEBUG`: Full injection traces
   - `INFO`: High-level dependency creation
   - `WARNING`: Default (minimal logging)

## Integration with Project

To enable injector logging in your application:

```python
# In your main.py or application setup
import logging

# Configure injector logging
if os.getenv('DEBUG', 'false').lower() == 'true':
    logging.getLogger('injector').setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logging.getLogger('injector').addHandler(handler)
```

## References

- [python-injector GitHub](https://github.com/python-injector/injector)
- [python-injector Documentation](https://injector.readthedocs.io/)
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)

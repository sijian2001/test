# Product Info CSV Export - Injector Logging Guide

## Overview

The `product_info_export_main.py` script now supports detailed dependency injection logging for debugging and understanding the application's dependency tree.

## Usage

### Normal Execution (Without Logging)

```bash
python product_info_export_main.py
```

Output:
```
INFO:__main__:Starting Product Info CSV Export Application...
INFO:batch.product_info_csv_export_processor:=== Starting Product Info CSV Export Process ===
...
```

### Debug Mode (With Injector Logging)

```bash
# On Linux/macOS/Git Bash
export DEBUG=true && python product_info_export_main.py

# On Windows CMD
set DEBUG=true && python product_info_export_main.py

# On Windows PowerShell
$env:DEBUG="true"; python product_info_export_main.py
```

## Debug Output Example

When `DEBUG=true` is set, you'll see detailed dependency injection traces:

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

## Dependency Tree Visualization

The indentation (`>`, `>>`, `>>>`, etc.) shows the depth of dependency injection:

```
ProductInfoCsvExportProcessorImpl
└── ProductInfoService
    └── ProductInfoRepository
        └── Test2DatabaseSession (Singleton)
            └── Test2DatabaseEngine (Singleton)
                └── DatabaseConfig (Singleton)
```

## Understanding the Logs

### Key Information in Debug Logs

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

### Singleton Behavior

Notice that `DatabaseConfig`, `Test2DatabaseEngine`, and `Test2DatabaseSession` are created with `SingletonScope`:
- They are created only once
- Subsequent requests return the same instance

## Use Cases

### 1. Debugging Injection Issues

If you encounter dependency injection errors, enable debug logging to see exactly where it fails:

```bash
DEBUG=true python product_info_export_main.py
```

### 2. Understanding Application Architecture

Use the logs to visualize how components are wired together:
- Which classes depend on what
- What's singleton vs transient
- Order of initialization

### 3. Performance Analysis

Debug logs can help identify:
- Heavy initialization in constructors
- Unnecessary object creation
- Singleton reuse patterns

## Disabling Logging

To disable injector logging, simply run without the DEBUG flag:

```bash
python product_info_export_main.py
```

Or explicitly set:

```bash
DEBUG=false python product_info_export_main.py
```

## Integration with Other Tools

The injector logging integrates seamlessly with:
- SQLAlchemy logging (shown as INFO level)
- Application logging (batch processor logs)
- Custom business logic logging

## Best Practices

1. **Development**: Enable `DEBUG=true` during development
2. **Testing**: Keep logging on to verify dependency wiring
3. **Production**: Disable debug logging for performance
4. **CI/CD**: Use debug logs in failing test cases for diagnosis

## Related Files

- `examples/injector_logging_example.py` - Basic injector logging example
- `examples/README.md` - Comprehensive injector logging guide
- `product_info_export_main.py` - This script with logging support

@echo off
setlocal enabledelayedexpansion
REM Test active_user_sync_main.py 1000 times and check for connection leaks

echo ================================================================================
echo Connection Leak Test: Running active_user_sync_main.py 1000 times
echo ================================================================================
echo.

REM Get start time
set START_TIME=%TIME%

REM Initialize counters
set /a SUCCESS_COUNT=0
set /a ERROR_COUNT=0
set /a TOTAL=1000

echo Starting %TOTAL% iterations...
echo Progress will be shown every 100 iterations
echo.

REM Loop 1000 times
for /L %%i in (1,1,%TOTAL%) do (
    REM Run the batch program
    python.exe .\app\batch\active_user_sync_main.py >nul 2>&1

    if errorlevel 1 (
        set /a ERROR_COUNT+=1
    ) else (
        set /a SUCCESS_COUNT+=1
    )

    REM Show progress every 100 iterations
    set /a MOD=%%i%%100
    if !MOD! EQU 0 (
        echo Iteration %%i / %TOTAL%: Success=!SUCCESS_COUNT!, Errors=!ERROR_COUNT!

        REM Check MySQL connections
        python -c "import pymysql; conn=pymysql.connect(host='localhost', user='user1', password='1234', database='test1'); cursor=conn.cursor(); cursor.execute('SHOW STATUS LIKE \"Threads_connected\"'); result=cursor.fetchone(); print('  MySQL Threads_connected:', result[1]); conn.close();" 2>nul
    )
)

REM Get end time
set END_TIME=%TIME%

echo.
echo ================================================================================
echo Test Results
echo ================================================================================
echo Total iterations: %TOTAL%
echo Successful: !SUCCESS_COUNT!
echo Errors: !ERROR_COUNT!
echo Start time: %START_TIME%
echo End time: %END_TIME%
echo.

REM Final connection check
echo ================================================================================
echo Final MySQL Connection Status
echo ================================================================================
python -c "import pymysql; conn=pymysql.connect(host='localhost', user='user1', password='1234', database='test1'); cursor=conn.cursor(); cursor.execute('SHOW STATUS LIKE \"Threads_connected\"'); result=cursor.fetchone(); print('Threads_connected:', result[1]); cursor.execute('SHOW STATUS LIKE \"Max_used_connections\"'); result=cursor.fetchone(); print('Max_used_connections:', result[1]); conn.close();"

echo.
echo ================================================================================
echo Conclusion
echo ================================================================================
echo If Threads_connected remains stable (not increasing significantly),
echo then no connection leak is detected.
echo ================================================================================

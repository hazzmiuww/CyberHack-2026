@echo off
REM Reset SIMA QC Database
REM This script deletes the SQLite database to start fresh

echo.
echo ========================================
echo   SIMA QC - Database Reset
echo ========================================
echo.

if exist "backend\sima_qc.db" (
    echo Found database: backend\sima_qc.db
    echo.
    echo WARNING: This will delete all detection records!
    echo.
    set /p confirm="Are you sure? (yes/no): "
    
    if /i "%confirm%"=="yes" (
        del "backend\sima_qc.db"
        echo.
        echo √ Database deleted successfully!
        echo   A new empty database will be created on next startup.
    ) else (
        echo.
        echo Database reset cancelled.
    )
) else (
    echo No database found. Nothing to reset.
)

echo.
pause

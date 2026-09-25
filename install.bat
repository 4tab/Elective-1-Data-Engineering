@echo off
setlocal enabledelayedexpansion

where py >nul 2>&1
if %errorlevel%==0 (
    set PYTHON=py
) else (
    where python >nul 2>&1
    if %errorlevel%==0 (
        set PYTHON=python
    ) else (
        echo Python 3 is required but was not found. Install Python 3.11+ and rerun.
        exit /b 1
    )
)

%PYTHON% -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -e .

if not exist .env copy .env.example .env >nul

echo Environment ready.
echo Run: .venv\Scripts\python.exe -m nyc_taxi_platform.cli all
endlocal

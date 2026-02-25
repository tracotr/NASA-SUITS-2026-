@echo off

cd /d "%~dp0"

:: Create virtual environment if it doesn't exist
if not exist .venv (
    echo Virtual environment not found, setting up and installing dependencies.
    python -m venv .venv
    call .venv\Scripts\activate
    pip install -r requirements.txt
) else (
    echo Starting virtual environment.
    call .venv\Scripts\activate
)

:: Start the API server
uvicorn tss_api:app
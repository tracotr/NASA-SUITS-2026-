#!/bin/bash

cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found, setting up and installing dependencies."
    python3 -m venv .venv
    source .venv/bin/activate
    # Only install during initial setup or when requirements.txt changes
    pip install -r requirements.txt
else
    echo "Starting virtual environment."
    source .venv/bin/activate
fi

# Start the API server without re-installing dependencies
uvicorn tss_api:app
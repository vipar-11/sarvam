#!/bin/bash
# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

echo "=================================================="
echo "   Campus Placement Cell Voice Assistant App"
echo "=================================================="

# Check and activate/create virtual environment
if [ -d "$PROJECT_ROOT/venv" ]; then
    echo "Found existing virtual environment at: $PROJECT_ROOT/venv"
    echo "Activating..."
    source "$PROJECT_ROOT/venv/bin/activate"
else
    echo "Virtual environment not found at $PROJECT_ROOT/venv."
    echo "Creating new virtual environment..."
    python3 -m venv "$PROJECT_ROOT/venv"
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Install dependencies from requirements.txt
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo "Installing base requirements..."
    pip install -r "$PROJECT_ROOT/requirements.txt"
fi

# Ensure fastapi, uvicorn, and other dependencies are installed
echo "Ensuring required FastAPI and client dependencies are installed..."
pip install fastapi uvicorn httpx python-multipart python-dotenv

# Run uvicorn server
echo "--------------------------------------------------"
echo "Launching FastAPI server..."
echo "Open your browser at: http://127.0.0.1:8000"
echo "--------------------------------------------------"

# Run from the project root directory
cd "$PROJECT_ROOT"
python -m uvicorn placement_cell.main:app --host 127.0.0.1 --port 8000 --reload

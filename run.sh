#!/bin/bash

ENV_NAME=".venv"

# 1. Find the correct Python command
if command -v python3 &>/dev/null; then
    PYTHON_EXE="python3"
elif command -v python &>/dev/null; then
    PYTHON_EXE="python"
else
    echo "Error: Python is not installed on this system."
    exit 1
fi

echo "Using $PYTHON_EXE..."

# 2. Creating virtual environment if it doesn't exist
if [ ! -d "$ENV_NAME" ]; then
    echo "Creating virtual environment..."
    $PYTHON_EXE -m venv $ENV_NAME
fi

# 3. Activating environment
if [ -d "$ENV_NAME/Scripts" ]; then
    source $ENV_NAME/Scripts/activate
else
    source $ENV_NAME/bin/activate
fi

# 4. Installing dependencies
echo "Installing/Updating dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found!"
fi

# 5. Applying database migrations
echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "----------------------------------------"
echo "Setup Complete! Starting Django Server..."
echo "----------------------------------------"
cd proj
python manage.py runserver
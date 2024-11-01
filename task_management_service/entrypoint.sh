#!/bin/bash

echo "Running unit tests..."
pytest --maxfail=1 --disable-warnings

if [ $? -ne 0 ]; then
  echo "Tests failed. Exiting..."
  exit 1
else
  echo "Tests passed. Starting the Task Management service..."
  python app.py
fi

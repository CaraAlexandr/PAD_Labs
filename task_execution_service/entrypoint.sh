#!/bin/bash

# Start the Flask app in the background
python app.py &

# Start the worker threads
python worker.py &

# Wait for all background processes to finish
wait -n

# Exit with status of process that exited first
exit $?

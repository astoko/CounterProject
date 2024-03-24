#!/bin/sh

# Function to handle SIGINT signal (Ctrl+C)
sigint_handler() {
    # Kill the process if it's running
    if [ -n "$process_id" ]; then
        kill "$process_id"
    fi
    exit 0
}

# Trap SIGINT signal (Ctrl+C) and call sigint_handler function
trap sigint_handler SIGINT

python main.py

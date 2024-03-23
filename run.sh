#!/usr/bin/env bash

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

# Infinite loop
while :
do
    # Start the process (replace "your_process_command" with the actual command)
    bun spam.js &

    # Get the process ID of the last background process
    process_id=$!

    # Wait for 1 minute
    sleep 60

    # Kill the process
    kill $process_id

    # Optionally, wait for a brief moment to ensure the process is killed before restarting
    sleep 1
done
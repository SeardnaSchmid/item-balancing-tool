#!/bin/bash

# Create data directory for persistent storage
echo "Creating data directory for persistent storage..."
mkdir -p ./data
chmod 755 ./data

echo "Data directory created at: $(pwd)/data"
echo "This directory will be mounted to /app/data inside the container."
echo "Data will persist between container restarts."

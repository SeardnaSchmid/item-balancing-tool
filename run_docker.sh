#!/bin/bash

# Create a copy of data.json with more permissive rights
cp data.json data.json.tmp
chmod 666 data.json.tmp

# Set environment variables for user and group IDs
USER_ID=$(id -u)
GROUP_ID=$(id -g)

# Run the container with environment variables
sudo docker-compose up -d

# Wait for the container to start
echo "Starting container..."
sleep 5

# Check if the container is running
CONTAINER_STATUS=$(sudo docker inspect --format='{{.State.Status}}' item-balancing-tool 2>/dev/null)

if [ "$CONTAINER_STATUS" = "running" ]; then
    echo "Container is running successfully!"
    echo "You can access the application at: http://localhost:8502"
else
    echo "Container may have issues. Checking logs..."
    sudo docker-compose logs
fi

#!/bin/bash

echo "Starting Item Balancing Tool Docker Container..."

# Überprüfen, ob Docker installiert ist
if ! command -v docker &> /dev/null; then
    echo "Docker ist nicht installiert. Bitte installieren Sie Docker und versuchen Sie es erneut."
    exit 1
fi

# Docker Compose überprüfen
if command -v docker-compose &> /dev/null; then
    echo "Docker Compose gefunden. Starte Container mit docker-compose..."
    docker-compose up -d
    echo "Container gestartet. Zugriff auf http://localhost:8501"
else
    echo "Docker Compose nicht gefunden. Starte Container mit docker..."
    docker build -t item-balancing-tool .
    docker run -d -p 8501:8501 --name item-balancing-tool -v $(pwd)/data.json:/app/data.json item-balancing-tool
    echo "Container gestartet. Zugriff auf http://localhost:8501"
fi

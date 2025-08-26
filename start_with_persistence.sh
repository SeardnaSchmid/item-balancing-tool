#!/bin/bash

echo "🚀 Setting up Item Balancing Tool with Docker"
echo "=============================================="

# Create data directory for persistence
echo "📁 Creating data directory..."
./setup_data_dir.sh

echo ""
echo "🐳 Building and starting Docker container..."
docker-compose up --build -d

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Your Item Balancing Tool is now running at:"
echo "   http://localhost:8502"
echo ""
echo "💾 Data persistence:"
echo "   - Data is auto-saved inside the container"
echo "   - Data persists between container restarts via volume mount"
echo "   - Local data directory: $(pwd)/data"
echo ""
echo "🔧 Useful commands:"
echo "   docker-compose logs -f          # View logs"
echo "   docker-compose stop             # Stop the container"
echo "   docker-compose restart          # Restart the container"
echo "   docker-compose down             # Stop and remove the container"

#!/bin/bash
# Deployment Script for Gender Analysis System

set -e

echo "🚀 Deploying Gender Analysis System..."
echo "=================================="

# Get absolute path to script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python -c "
from storage.database import db_manager
db_manager.initialize_tables()
print('✅ Database tables created')
"

# Check services
echo "Checking services..."
source venv/bin/activate

# Check PostgreSQL
python -c "
from storage.database import db_manager
if db_manager.health_check():
    print('✅ PostgreSQL: OK')
else:
    print('❌ PostgreSQL: Failed')
"

# Check Redis
python -c "
from core.utils.queue_manager import TaskQueue
queue = TaskQueue()
if queue.is_available():
    print('✅ Redis: OK')
else:
    print('❌ Redis: Failed')
"

# Check Prometheus
curl -s http://localhost:9090/api/v1/status/config > /dev/null && echo "✅ Prometheus: OK" || echo "⚠️  Prometheus: Not running"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "To start the system:"
echo "  cd $PROJECT_DIR"
echo "  source venv/bin/activate"
echo "  python -m api.main"
echo ""
echo "Services monitoring:"
echo "  - Prometheus: http://localhost:9090"
echo "  - Redis Insight: /Applications/Redis Insight.app"
echo "  - pgAdmin: /Applications/pgAdmin 4.app"


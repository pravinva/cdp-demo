#!/bin/bash
# Start script for CDP Platform

echo "Starting Databricks CDP Platform..."
echo "=================================="

# Check if backend dependencies are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo ""
    echo "⚠️  Backend dependencies not installed."
    echo "   Install with: cd backend && pip3 install -r requirements.txt"
    echo "   Note: Some packages (pyspark, databricks-sdk) require additional setup"
    echo ""
    echo "Starting frontend only..."
    echo ""
    cd frontend && npm run dev
else
    echo ""
    echo "Starting backend server..."
    cd backend
    python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo "Backend started (PID: $BACKEND_PID)"
    echo "Backend API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/api/docs"
    echo ""
    echo "Starting frontend server..."
    cd ../frontend
    npm run dev
    # Cleanup on exit
    kill $BACKEND_PID 2>/dev/null
fi


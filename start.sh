#!/bin/bash

echo "🎾 Starting Tennis Coach Application..."

# Start the Flask backend
echo "Starting Flask backend..."
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start the React frontend
echo "Starting React frontend..."
cd tennis-coach-ui
npm start &
FRONTEND_PID=$!

echo "✅ Application started!"
echo "🎾 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup processes
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

# Wait for either process to exit
wait
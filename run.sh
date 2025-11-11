#!/bin/bash
# Run the DeepBest Trading Dashboard

echo "Starting DeepBest Trading Dashboard..."
echo "The dashboard will be available at http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"
python app.py

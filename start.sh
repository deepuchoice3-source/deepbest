#!/bin/bash

# Startup script for DeepBest Market Metrics Application

echo "=========================================="
echo "DeepBest - Nifty 50 Market Metrics"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1)
echo "Python version: $python_version"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "Creating .env from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your Upstox credentials."
    echo ""
    echo "To get started:"
    echo "1. Register at https://account.upstox.com/developer/apps"
    echo "2. Create an app to get API credentials"
    echo "3. Edit .env file with your UPSTOX_ACCESS_TOKEN"
    echo ""
    read -p "Do you want to run in DEMO mode (without Upstox credentials)? (y/n): " use_demo
    
    if [ "$use_demo" = "y" ] || [ "$use_demo" = "Y" ]; then
        echo ""
        echo "🚀 Starting in DEMO mode with simulated data..."
        python3 mock_server.py
        exit 0
    else
        echo ""
        echo "Please configure .env file and run this script again."
        exit 1
    fi
fi

# Check if access token is configured
if grep -q "your_access_token_here" .env; then
    echo "⚠️  Upstox access token not configured in .env"
    echo ""
    read -p "Run in DEMO mode instead? (y/n): " use_demo
    
    if [ "$use_demo" = "y" ] || [ "$use_demo" = "Y" ]; then
        echo ""
        echo "🚀 Starting in DEMO mode with simulated data..."
        python3 mock_server.py
        exit 0
    else
        echo "Please configure your Upstox access token in .env file"
        exit 1
    fi
fi

echo "🚀 Starting with Upstox real-time data..."
echo ""
python3 app.py

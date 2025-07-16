#!/bin/bash

# iOS Test Runner Script
# Handles Appium startup and test execution

set -e

echo "🚀 Starting iOS Test Suite"
echo ""

# Check if Appium is already running
if lsof -i :4723 > /dev/null 2>&1; then
    echo "⚠️  Appium is already running on port 4723. Stopping it..."
    pkill -f appium || true
    sleep 2
fi

# Start Appium in the background
echo "🔧 Starting Appium server..."
./node_modules/.bin/appium \
    --address localhost \
    --port 4723 \
    --relaxed-security \
    --allow-cors \
    --log ./test-results/appium.log &

APPIUM_PID=$!
echo "📋 Appium PID: $APPIUM_PID"

# Wait for Appium to be ready
echo "⏳ Waiting for Appium to be ready..."
sleep 3

# Check if Appium is responding
MAX_ATTEMPTS=10
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:4723/status > /dev/null 2>&1; then
        echo "✅ Appium is ready!"
        break
    else
        ATTEMPT=$((ATTEMPT + 1))
        echo "⏳ Appium not ready yet, attempt $ATTEMPT/$MAX_ATTEMPTS..."
        sleep 1
    fi
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "❌ Appium failed to start after $MAX_ATTEMPTS attempts"
    kill $APPIUM_PID 2>/dev/null || true
    exit 1
fi

# Cleanup function
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    kill $APPIUM_PID 2>/dev/null || true
    echo "✅ Cleanup complete"
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Run the tests
echo "🎯 Running tests..."
echo ""
TARGET=ios npx ts-node wdio/runner.ts

echo ""
echo "🏁 Test execution completed"
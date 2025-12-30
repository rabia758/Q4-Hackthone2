#!/bin/bash

echo "Setting up the Full-Stack Web Todo Application..."

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

# Check if Python and pip are available
if command -v python3 &> /dev/null && command -v pip3 &> /dev/null; then
    echo "Installing backend dependencies..."
    cd src/backend
    pip3 install -r requirements.txt
    cd ../..
else
    echo "Python or pip not found. Please install Python and pip first."
    exit 1
fi

echo "Setup complete!"
echo ""
echo "To run the application, use:"
echo "  npm run dev:concurrent"
echo ""
echo "To run individually:"
echo "  Frontend: npm run dev"
echo "  Backend: npm run backend"
#!/bin/bash

# Setup script for Telecom Support AI Agents
# Automates environment setup, dependency installation, and vector store initialization

set -e  # Exit on error

echo "================================================"
echo "🚀 Telecom Support AI - Setup Script"
echo "================================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"
echo ""

# Create virtual environment
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"
echo ""

# Setup .env file
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Skipping creation."
else
    echo "🔧 Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY"
    echo "   You can get an API key from: https://platform.openai.com/api-keys"
    echo ""
    read -p "Press Enter to continue after adding your API key..."
fi
echo ""

# Check if API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo "❌ ERROR: Please set your OPENAI_API_KEY in .env file"
    exit 1
fi
echo "✓ API key configured"
echo ""

# Build vector store
echo "🔧 Building vector store from documentation..."
echo "   This may take 1-2 minutes..."
python retriever/build_vectorstore.py
echo "✓ Vector store built successfully"
echo ""

# Final message
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate virtual environment (if not already active):"
echo "   source venv/bin/activate"
echo ""
echo "2. Start the FastAPI server:"
echo "   python main.py"
echo "   Then visit: http://localhost:8000"
echo ""
echo "3. OR run in CLI mode for quick testing:"
echo "   python main.py --cli"
echo ""
echo "4. View API documentation:"
echo "   http://localhost:8000/docs (when server is running)"
echo ""
echo "================================================"

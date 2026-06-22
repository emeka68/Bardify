#!/bin/bash
# Quick install script for Shakespeare Translator CLI

set -e

echo "🎭 Shakespeare Translator — CLI Installation"
echo "=============================================="
echo ""

# Check Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "⚙️  Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt > /dev/null

# Install as editable package
echo "🔗 Installing shakespeare CLI..."
pip install -e . > /dev/null

# Verify installation
echo ""
echo "✅ Installation complete!"
echo ""

# Test it
echo "🧪 Testing CLI..."
if shakespeare --version > /dev/null 2>&1; then
    echo "✅ CLI is working!"
    echo ""
    echo "Try it out:"
    echo "  shakespeare \"Hey what's up?\""
    echo "  shakespeare --interactive"
    echo "  echo 'Hello world' | shakespeare --quiet"
    echo ""
    echo "More info: shakespeare --help"
else
    echo "❌ CLI test failed"
    exit 1
fi

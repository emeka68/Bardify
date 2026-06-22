#!/bin/bash
# Test script for Shakespeare Translator CLI

echo "🎭 Shakespeare Translator — CLI Test Suite"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

test_count=0
pass_count=0

# Test function
run_test() {
    test_count=$((test_count + 1))
    echo "Test $test_count: $1"
    
    if eval "$2" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}\n"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}❌ FAIL${NC}\n"
    fi
}

# Ensure we're in the right directory
if [ ! -f "cli.py" ]; then
    echo "❌ Error: cli.py not found. Run from project root."
    exit 1
fi

# Install dependencies if needed
if ! python -c "import click" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt > /dev/null
fi

# Tests
run_test "Show help" "python cli.py --help"
run_test "Show version" "python cli.py --version"
run_test "Transform single text" "echo 'test' | python cli.py transform 'Hello world'"
run_test "Single text from argument" "python cli.py transform 'Hello' --quiet"
run_test "Show config" "python cli.py config"
run_test "Show examples" "python cli.py examples"

# Summary
echo "=========================================="
echo "Results: $pass_count/$test_count tests passed"

if [ $pass_count -eq $test_count ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed${NC}"
    exit 1
fi

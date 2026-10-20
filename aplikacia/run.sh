#!/bin/bash
# run.sh — Spustenie zberateľskej aplikácie Zbierka & Vinted Snajper
# Otvorí moderné Apple/Vinted rozhranie na porte 5001.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================================="
echo "  🚀 Spúšťam Zbierku & Vinted Snajper..."
echo "  🌐 Otvorte prehliadač na: http://127.0.0.1:5001"
echo "=========================================================="

if [ -f "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3" ]; then
    PYTHON_CMD="/Library/Frameworks/Python.framework/Versions/3.14/bin/python3"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

$PYTHON_CMD app.py

#!/bin/bash
echo " === INSURANCE SERVER starting ==="
echo "Running on port 5001"
(redis-server > /dev/null 2>&1) & (python3 app.py)
#!/bin/bash
echo " === DOCTOR SERVER starting ==="
echo "Running on port 5000"
(redis-server > /dev/null 2>&1) & (python3 app.py)
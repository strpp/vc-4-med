#!/bin/bash
echo " === DOCTOR SERVER starting ==="
echo "Running on port 5000"
(redis-server) & (python3 setup.py; python3 app.py)
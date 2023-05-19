#!/bin/bash
echo " === DOCTOR SERVER starting ==="
echo "Running on port 5000"
(redis-server) & (python setup.py; python app.py)
#!/bin/bash
echo " === DOCTOR SERVER starting ==="
echo "Running on port 5000"
(redis-server > /dev/null 2>&1) & (cd doctor; python app.py > doctor.log 2>&1)
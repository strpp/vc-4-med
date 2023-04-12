#!/bin/bash
echo " === VC-4-MED starting ==="
echo "Doctor running on port 5000. Pharma running on port 5001. Insurance running on port 5002"
(redis-server > /dev/null 2>&1) & (sudo -i -u couchdb /home/couchdb/bin/couchdb > /dev/null 2>&1) & (cd doctor; python app.py > doctor.log 2>&1) & (cd insurance; python app.py > insurance.log 2>&1) & (cd pharma; python app.py > pharma.log 2>&1)
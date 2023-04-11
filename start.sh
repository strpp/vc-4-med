#!/bin/bash
(redis-server > /dev/null 2>&1) & (sudo -i -u couchdb /home/couchdb/bin/couchdb > /dev/null 2>&1) & (cd doctor; python app.py) & (cd pharma; python app.py )


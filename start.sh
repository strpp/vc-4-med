#!/bin/bash
(redis-server > /dev/null 2>&1) & (sudo -i -u couchdb /home/couchdb/bin/couchdb > /dev/null 2>&1) & (cd vc-4-med/pharma; python app.py )


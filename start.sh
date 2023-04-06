#!/bin/bash
redis-server & sudo -i -u couchdb /home/couchdb/bin/couchdb & (cd pharma; python app.py )


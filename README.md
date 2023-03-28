# vc-4-med
SSI flow for the management of medical prescriptions to minimize opportunities for frauds.

## SETUP
(todo)

## RUN A DEMO
### 1 - START services
start Redis: 
redis-server
start couchDB: 
sudo -i -u couchdb /home/couchdb/bin/couchdb

### 2 - START server
python app.py

### PORTS
Doctor on 5000
Pharma on 5001
Insurance on 5002
CouchDB interface (Fauxton) on 5984/_utils

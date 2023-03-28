# vc-4-med
SSI flow for the management of medical prescriptions to minimize opportunities for frauds.

## SETUP
(still todo)  <br />
The system requires:  <br />
a Redis instance to cache values  <br />
a CouchDB node to store verifiable credentials  <br />
a list of python packages  <br />


## RUN A DEMO
### 1 - Launch services
start Redis:  <br />
<code>redis-server</code>  <br />
start couchDB:  <br />
<code>sudo -i -u couchdb /home/couchdb/bin/couchdb</code>  <br />

### 2 - Launch servers
Move into each dir (doctor, pharma, insurance) and start flask servers using the following command <br />
<code>python app.py</code>

### PORTS
Doctor on 5000  <br />
Pharma on 5001  <br />
Insurance on 5002  <br />
CouchDB interface (Fauxton) on 5984/_utils  <br />

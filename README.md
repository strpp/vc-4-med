# vc-4-med
SSI flow for the management of medical prescriptions to minimize opportunities for frauds. <br />
This repository contains the source code for a project developed under the supervision of Padua university.

## SETUP
The system requires <a href='https://docs.couchdb.org/en/stable/install/unix.html'>a CouchDB node</a> running on port 5984 with two databases : 'vc' and 'insurance'  <br />
To install all the Python packages you need:
<code> pip install -r requirements.txt </code>

## RUN A DEMO
After setting up, you can run a demo by typing:
<code>./start.sh</code>

### PORTS
Doctor on 5000  <br />
Pharma on 5001  <br />
Insurance on 5002  <br />
CouchDB interface (Fauxton) on 5984/_utils  <br />

## TEST SMART CONTRACT ON Mumbai
contract address:    0xCD3D21d1e7f8303d2450a2954444E04a2AFB20AE <br>
owner:               0xbd332ee288eE1335fae22c49906b06Ef050a070d <br>

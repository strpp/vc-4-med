from flask import Flask, render_template
from flask_session import Session
from flask_socketio import SocketIO
from flask_qrcode import QRcode
from flask_cors import CORS
from dotenv import load_dotenv
import os
import socket
import couchdb
import redis
import verify_prescription

load_dotenv()

try:
    red = redis.Redis(host='localhost', port=6379, db=0)
except redis.ConnectionError:
    red = redis.Redis(host='redis', port=6379, db=0)
    
hostname = socket.gethostname()
COUCH_ADMIN = os.getenv('COUCH_ADMIN')
COUCH_PWD = os.getenv('COUCH_PWD')

if(hostname == 'raspberrypi'):
    couch = couchdb.Server('http://localhost:5984')
else: # we are on docker instance
    couch = couchdb.Server(f'http://{COUCH_ADMIN}:{COUCH_PWD}@172.21.0.2:5984')

socketio = SocketIO()

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
socketio = SocketIO(app)
verify_prescription.init_app(app, red, socketio, couch)

Session(app)
QRcode(app)
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
   socketio.run(app, debug=True, host='0.0.0.0', port=5001)

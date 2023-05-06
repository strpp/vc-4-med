from flask import Flask, render_template
from flask_session import Session
from flask_socketio import SocketIO
from flask_qrcode import QRcode
from flask_cors import CORS
from dotenv import load_dotenv
import couchdb
import redis
import verify_prescription
import os

red = redis.Redis(host='localhost', port=6379, db=0)
couch = couchdb.Server('http://localhost:5984')
socketio = SocketIO()
load_dotenv()

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

from flask import Flask, render_template
from flask_qrcode import QRcode
from flask_socketio import SocketIO
import redis
import prescription
import os


red = redis.Redis(host='localhost', port=6379, db=0)
socketio = SocketIO()

app = Flask(__name__)
app.config.from_pyfile('config.py')
socketio = SocketIO(app)
prescription.init_app(app, red, socketio)

QRcode(app)

@app.route('/')
def index():
    return render_template('index.html', doctor=os.getenv('DOCTOR'))

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

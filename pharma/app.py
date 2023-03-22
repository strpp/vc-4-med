from flask import Flask, render_template
from flask_qrcode import QRcode
import redis

red = redis.Redis(host='localhost', port=6379, db=0)

app = Flask(__name__)
app.secret_key = 'mysecretkey' # set the secret key for sessions

QRcode(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

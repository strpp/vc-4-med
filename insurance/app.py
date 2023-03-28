from flask import Flask, request, jsonify
from flask_session import Session
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
app.secret_key = 'mysecretkey' # set the secret key for sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

@app.route('/')
def index():
    return "Insurance API"

@app.route('/api/refund', methods=['POST'])
def refund():
    try:
        vps = request.json
    except:
        return 'Bad Request', 400

    # Check VP
    print(vps[0])

    # Check TXH on blockchain

    # Initiate refund process

    # Return results
    response = jsonify({'message': 'success'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5002)

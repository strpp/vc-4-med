from flask import jsonify, request, render_template, session, redirect, flash, Response
from datetime import timedelta, datetime
import json
import uuid
import didkit
from web3 import Web3

def init_app(app, red) :
    app.add_url_rule('/authorize',  view_func=authorize, methods = ['GET', 'POST'], defaults={"red" : red})
    app.add_url_rule('/verify/<stream_id>',  view_func=verify, methods = ['GET','POST'], defaults={"red" : red})
    app.add_url_rule('/callback/<stream_id>',  view_func=callback, methods = ['GET','POST'], defaults={"red" : red})
    return

def authorize(red):
        
    #Generate stream id
    stream_id = str(uuid.uuid4().hex)

    red.set(stream_id, json.dumps({'stream_id' : stream_id, 'verified' : False}))
    # TODO: add client to web socket to listen for changes

    #Generate QR Code
    url = f'http://192.168.1.20:5001/authorize/{stream_id}'
    print(url)
    return render_template('qrcode.html', url=url)

def verify(red):

    if request.method == 'GET':
        #TODO
        return 200
    
    else:
        #TODO
        return 200

def callback(red):
    #TODO
    return 200




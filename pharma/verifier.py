from flask import jsonify, request, render_template, session, redirect, flash, Response
from flask_socketio import SocketIO, join_room, leave_room
from datetime import timedelta, datetime
import json
import uuid
import didkit
from web3 import Web3

def init_app(app, red, socketio) : 

    app.add_url_rule('/authorize',  view_func=authorize, methods = ['GET', 'POST'], defaults={"red" : red, "socketio" : socketio})
    app.add_url_rule('/verify/<stream_id>',  view_func=verify, methods = ['GET','POST'], defaults={"red" : red, "socketio" : socketio})
    app.add_url_rule('/callback/<stream_id>',  view_func=callback, methods = ['GET','POST'], defaults={"red" : red})
    return

def authorize(red, socketio):

    #Generate stream id
    stream_id = str(uuid.uuid4().hex)

    @socketio.on('subscribe')
    def subscribe(data):
        # Add client to private channel to get further updates
        join_room(data['socket_id'])
        # Save socket_id on server session to make /authorize able to link socket_id and stream_id
        socket_id = data['socket_id']
        print(f'socket_id : {socket_id}, stream_id : {stream_id}')
        red.set(stream_id, json.dumps({'stream_id' : stream_id, 'socket_id' : socket_id, 'verified' : False}))

    #Generate QR Code
    url = f'http://192.168.1.20:5001/verify/{stream_id}'
    print(url)
    return render_template('qrcode.html', url=url)

def verify(stream_id, red, socketio):

    if request.method == 'GET':
        socket_id = json.loads(red.get(stream_id).decode())['socket_id']
        print(f'{stream_id} requested auth for {socket_id}')
        socketio.emit('stream_id', {'stream_id' : stream_id}, to=socket_id)
        return jsonify({'stream_id' : stream_id})
    
    else:
        #TODO
        return 200

def callback(stream_id, red):
    #TODO
    return jsonify({'callback': 'success', 'stream_id' : stream_id})



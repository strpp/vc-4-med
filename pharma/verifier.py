from flask import jsonify, request, render_template, session, redirect, flash, Response
from flask_socketio import SocketIO, join_room, leave_room
from datetime import timedelta, datetime
from didkit import verify_presentation
import json
import uuid
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

async def verify(stream_id, red, socketio):

    if request.method == 'GET':
        presentation_request = {
            "type": "VerifiablePresentationRequest",
            "query": [
                    {
                    "type": "QueryByExample",
                    "credentialQuery": [
                        {
                        "required": True,
                        "example": {
                            "type": "MedicalPrescriptionCredential",
                            "trustedIssuer": [
                                {
                                    "required": True,
                                    "issuer": "did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX"
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ],
            "challenge": str(uuid.uuid4),
            "domain": "www.example.com"
        }
        return jsonify(presentation_request)
    
    else: #POST
        form = request.form
        presentation = json.loads(form.get('presentation'))
        verification_method = presentation['proof']['verificationMethod']
        
        try:
            didkit_options = {"proofPurpose": "assertionMethod","verificationMethod": verification_method}
            await verify_presentation(json.dumps(presentation), json.dumps(didkit_options))

            # Redirect client via server push
            socket_id = json.loads(red.get(stream_id).decode())['socket_id']
            socketio.emit('stream_id', {'stream_id' : stream_id}, to=socket_id)

            # Save the tokens in the session
            red.set(stream_id, json.dumps({'stream_id' : stream_id, 'socket_id' : socket_id, 'verified' : True, 'vp' : presentation}))
            #session['id_token'] = create_id_token()
            #session['access_token'] = create_access_token()

            # Send ok to wallet
            return 'Credential verified successfully!', 200
        
        except Exception as e:
            print(e)
            return 'Credential verification failed.', 400


def callback(stream_id, red):
    vp = json.loads(red.get(stream_id).decode())['vp']
    return jsonify({'callback': 'success', 'vp' : vp})



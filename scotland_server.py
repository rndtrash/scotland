#!/usr/bin/env python3

import time
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import urllib
import json
import uuid
import random
import html

app = Flask(__name__, static_url_path='/static')
sio = SocketIO(app)

users_dic = dict()

@app.route('/')
def root():
	return app.send_static_file('index.html')

@sio.on('connect')
def connect():
	if request.sid in users_dic:
		return
	nickname = request.args.get('nickname')[:32]
	if len(nickname) == 0:
		nickname = 'scot land'
	print('connect ', request.sid, nickname)
	users_dic[request.sid] = {'id': str(uuid.uuid4()), 'nickname': html.escape(nickname), 'x': random.randint(0, 7), 'y': random.randint(0, 7)}
	sio.emit('users', [users_dic[i] for i in users_dic if i != request.sid], room=request.sid)
	sio.emit('join', json.dumps(users_dic[request.sid]))

@sio.on('disconnect')
def disconnect():
	id = users_dic[request.sid]['id']
	print('disconnect ', request.sid, id)
	del users_dic[request.sid]
	sio.emit('leave', id)

@sio.event
def say(data):
	msg = html.escape(str(data)[:128])
	print(request.sid, msg)
	if len(msg) != 0:
		sio.emit('say', {'id': users_dic[request.sid]['id'], 'msg': msg})

@sio.event
def move(data):
	print("move", request.sid, data)
	xy = data.split(";")
	if len(xy) != 2:
		return
	xy = [min(7, max(0, int(x))) for x in xy]
	sio.emit('move', {'id': users_dic[request.sid]['id'], 'x': xy[0], 'y': xy[1]})

if __name__ == '__main__':
    sio.run(app)

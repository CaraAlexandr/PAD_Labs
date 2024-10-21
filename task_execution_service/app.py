# app.py
from flask import Flask, request
from flask_migrate import Migrate
from flask_socketio import SocketIO, join_room, leave_room, emit
import grpc
from concurrent import futures
import threading
import redis
from extensions import db
from services import TaskExecutionServicer
from tasks import process_task
import logging
import time
import os
import signal
import sys
import requests

import task_execution_pb2_grpc
from workers import start_worker, monitor_redis_queue, serve_grpc
from utils import deregister_with_service_discovery

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db_task_execution:5432/task_execution_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Initialize SocketIO with WebSocket transport mode
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', transports=['websocket'], ping_timeout=60, ping_interval=25)
redis_client = redis.Redis(host='redis_pad', port=6379)
app.config['redis_client'] = redis_client

logging.basicConfig(level=logging.INFO)

from routes import worker_bp, status_bp
app.register_blueprint(worker_bp)
app.register_blueprint(status_bp)

# SocketIO Event Handlers
@socketio.on('join_task', namespace='/lobby')
def handle_join_task(data):
    task_id = data.get('task_id')
    user = data.get('user', 'Unknown')
    if task_id:
        room = str(task_id)
        join_room(room)
        logging.info(f"User {user} (Session ID: {request.sid}) joined task room: {room}")
        emit('joined', {'room': room})

        # Notify all users in the room
        emit('user_joined', {'message': f"User {user} joined task {room}"}, room=room)
        # Notify users in the general lobby
        emit('user_joined', {'message': f"User {user} joined task {room}"}, room='all_tasks')
    else:
        emit('error', {'message': 'No task_id provided'})

@socketio.on('join_all_tasks', namespace='/lobby')
def handle_join_all_tasks(data):
    user = data.get('user', 'Unknown')
    join_room('all_tasks')
    logging.info(f"User {user} (Session ID: {request.sid}) joined the general tasks room")
    emit('joined', {'room': 'all_tasks'})
    # Notify all users in the general room
    emit('user_joined', {'message': f"User {user} joined the general tasks room"}, room='all_tasks')

@socketio.on('leave_task', namespace='/lobby')
def handle_leave_task(data):
    task_id = data.get('task_id')
    user = data.get('user', 'Unknown')
    if task_id:
        room = str(task_id)
        leave_room(room)
        logging.info(f"User {user} (Session ID: {request.sid}) left task room: {room}")
        emit('left', {'room': room})
    else:
        emit('error', {'message': 'No task_id provided'})

@socketio.on('disconnect', namespace='/lobby')
def handle_disconnect():
    logging.info(f"User {request.sid} disconnected.")

def signal_handler(sig, frame):
    deregister_with_service_discovery()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Start gRPC server
        grpc_thread = threading.Thread(target=serve_grpc, args=(app, socketio), daemon=True)
        grpc_thread.start()
        # Start monitoring Redis queue
        monitor_thread = threading.Thread(target=monitor_redis_queue, daemon=True)
        monitor_thread.start()
        # Start worker threads
        start_worker(socketio, app)
        # Run SocketIO server without namespace for testing
        socketio.run(app, host='0.0.0.0', port=5001)

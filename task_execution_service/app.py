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
from email.mime.text import MIMEText
import smtplib

import task_execution_pb2_grpc  # Correct Import

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db_task_execution:5432/task_execution_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")
redis_client = redis.Redis(host='redis_pad', port=6379)

from routes import worker_bp, status_bp

app.register_blueprint(worker_bp)
app.register_blueprint(status_bp)

logging.basicConfig(level=logging.INFO)

# SocketIO Event Handlers
@socketio.on('join_task', namespace='/lobby')
def handle_join_task(data):
    task_id = data.get('task_id')
    user = data.get('user', 'Unknown')  # Optional: Get user info if provided
    if task_id:
        room = str(task_id)
        join_room(room)
        logging.info(f"User {user} (Session ID: {request.sid}) joined task room: {room}")
        emit('joined', {'room': room})
    else:
        emit('error', {'message': 'No task_id provided'})

@socketio.on('leave_task', namespace='/lobby')
def handle_leave_task(data):
    task_id = data.get('task_id')
    user = data.get('user', 'Unknown')  # Optional: Get user info if provided
    if task_id:
        room = str(task_id)
        leave_room(room)
        logging.info(f"User {user} (Session ID: {request.sid}) left task room: {room}")
        emit('left', {'room': room})
    else:
        emit('error', {'message': 'No task_id provided'})

@socketio.on('disconnect', namespace='/lobby')
def handle_disconnect():
    logging.info(f"User {request.sid} disconnected from /lobby namespace.")

def send_alert(message):
    try:
        smtp_server = os.getenv('ALERT_SMTP_SERVER', 'smtp.example.com')
        smtp_user = os.getenv('ALERT_SMTP_USER', 'user')
        smtp_password = os.getenv('ALERT_SMTP_PASSWORD', 'password')
        alert_from = os.getenv('ALERT_FROM', 'alert@example.com')
        alert_to = os.getenv('ALERT_TO', 'admin@example.com')

        msg = MIMEText(message)
        msg['Subject'] = 'Redis Queue Alert'
        msg['From'] = alert_from
        msg['To'] = alert_to

        with smtplib.SMTP(smtp_server) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
        logging.info("Alert email sent.")
    except Exception as e:
        logging.error(f"Failed to send alert email: {e}")

def monitor_redis_queue():
    critical_threshold = 60
    check_interval = 30  # seconds
    while True:
        try:
            queue_length = redis_client.llen('task_queue')
            logging.info(f"Redis task_queue length: {queue_length}")
            if queue_length > critical_threshold:
                alert_message = f"ALERT: Redis task queue length is {queue_length}, exceeding the critical threshold of {critical_threshold}."
                logging.warning(alert_message)
                send_alert(alert_message)
        except Exception as e:
            logging.error(f"Error monitoring Redis queue: {e}")
        time.sleep(check_interval)

def deregister_with_service_discovery():
    service_name = 'task_execution_service'
    service_discovery_url = os.getenv('SERVICE_DISCOVERY_URL', 'http://service_discovery:8003/services/deregister')
    try:
        response = requests.delete(f'{service_discovery_url}/{service_name}')
        if response.status_code in (200, 204):
            logging.info('Deregistered from Service Discovery.')
        else:
            logging.error(f'Failed to deregister from Service Discovery: {response.text}')
    except Exception as e:
        logging.error(f'Error deregistering with Service Discovery: {e}')

def signal_handler(sig, frame):
    deregister_with_service_discovery()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# gRPC server
def serve_grpc(app):
    with app.app_context():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        task_execution_pb2_grpc.add_TaskExecutionServiceServicer_to_server(TaskExecutionServicer(app), server)
        server.add_insecure_port('[::]:50052')
        server.start()
        logging.info("gRPC server for Task Execution Service started on port 50052.")
        server.wait_for_termination()

# Worker function
def worker():
    with app.app_context():
        while True:
            task_data = redis_client.brpop('task_queue')
            if task_data:
                task_id_bytes = task_data[1]
                task_id_str = task_id_bytes.decode('utf-8')  # Decode bytes to string
                try:
                    task_id = int(task_id_str)
                    logging.info(f"Worker picked up Task ID: {task_id}")
                    process_task(task_id, socketio)
                except ValueError:
                    logging.error(f"Invalid task ID retrieved from queue: {task_id_str}")

# Start worker threads
def start_workers():
    for _ in range(10):  # Limit to 10 workers
        threading.Thread(target=worker, daemon=True).start()
    logging.info("Started 10 worker threads.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        threading.Thread(target=serve_grpc, args=(app,), daemon=True).start()
        threading.Thread(target=monitor_redis_queue, daemon=True).start()
        start_workers()
        socketio.run(app, host='0.0.0.0', port=5000)

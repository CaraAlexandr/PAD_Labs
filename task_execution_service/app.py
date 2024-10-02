import eventlet
eventlet.monkey_patch()  # Ensure this is done first before anything else

from flask import Flask
from flask_migrate import Migrate
from flask_socketio import SocketIO, join_room, emit
import grpc
from concurrent import futures
import threading
import redis
from extensions import db
from services import TaskExecutionServicer
import task_execution_pb2_grpc
from tasks import process_task

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db_task_execution:5432/task_execution_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Recommended to disable

db.init_app(app)  # Initialize db with the app
migrate = Migrate(app, db)

# Initialize Redis and SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")
redis_client = redis.Redis(host='redis_pad', port=6379)

# Register blueprints (Assuming you have them in `routes.py`)
from routes import worker_bp, status_bp

app.register_blueprint(worker_bp)
app.register_blueprint(status_bp)


# WebSocket logic for task updates
@socketio.on('connect', namespace='/lobby')
def on_connect():
    emit('status', {'msg': 'Connected to the task lobby'})


@socketio.on('join', namespace='/lobby')
def on_join(data):
    task_id = data.get('task_id')
    if task_id:
        join_room(task_id)
        emit('status', {'msg': f'Joined room for task {task_id}'}, room=task_id)
    else:
        emit('status', {'msg': 'Joined general lobby for all tasks'})


# gRPC server for task execution
def serve_grpc(app):
    with app.app_context():  # Ensure the app context is available for gRPC
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        task_execution_pb2_grpc.add_TaskExecutionServicer_to_server(TaskExecutionServicer(app), server)
        server.add_insecure_port('[::]:50052')  # gRPC server on port 50052
        server.start()
        server.wait_for_termination()


# Worker function to process tasks from Redis queue
def worker():
    with app.app_context():  # Ensure the app context is available in the worker
        while True:
            task_data = redis_client.brpop('task_queue')
            if task_data:
                task_id = int(task_data[1])
                process_task(task_id)  # Now this function is properly imported
                socketio.emit('task_update', {'task_id': task_id, 'status': 'completed'}, room=task_id)


# Function to start worker threads
def start_workers():
    for _ in range(10):  # Limit to 10 workers
        threading.Thread(target=worker).start()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
        threading.Thread(target=serve_grpc, args=(app,)).start()  # Start gRPC server in a thread
        start_workers()  # Start workers to process tasks
        socketio.run(app, host='0.0.0.0', port=5000)  # Run Flask with Eventlet

from flask_socketio import SocketIO  # Add this line
from flask import Flask
from flask_migrate import Migrate
import grpc
from concurrent import futures
import task_execution_pb2_grpc
from services import TaskExecutionServicer
import threading
import multiprocessing
import redis
from extensions import db  # Import db from extensions.py

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db_task_execution:5432/task_execution_db'

db.init_app(app)
migrate = Migrate(app, db)
socketio = SocketIO(app, cors_allowed_origins="*")
redis_client = redis.Redis(host='redis_pad', port=6379)

from routes import worker_bp, status_bp

app.register_blueprint(worker_bp)
app.register_blueprint(status_bp)

# gRPC server function
def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    task_execution_pb2_grpc.add_TaskExecutionServicer_to_server(TaskExecutionServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()

# Worker function to process tasks from Redis queue
def worker():
    while True:
        task_id = redis_client.brpop('task_queue')[1]
        # Process the task
        tasks.process_task(int(task_id), socketio)

# Start worker processes
def start_workers():
    processes = []
    for _ in range(10):  # Limit to 10 workers
        p = multiprocessing.Process(target=worker)
        p.start()
        processes.append(p)

# Run the gRPC server and workers in separate threads
if __name__ == '__main__':
    threading.Thread(target=serve_grpc).start()
    threading.Thread(target=start_workers).start()
    socketio.run(app, host='0.0.0.0', port=5000)

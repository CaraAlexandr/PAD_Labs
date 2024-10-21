# workers.py
import threading
import logging
import time
import grpc
import redis
from flask import current_app
from extensions import db
from models import Task
from tasks import process_task
import task_execution_pb2_grpc
import task_execution_pb2
from utils import send_alert

def worker(worker_id, socketio, app):
    with app.app_context():
        redis_client = app.config.get('redis_client', None)
        if not redis_client:
            redis_client = redis.Redis(host='redis_pad', port=6379)
            app.config['redis_client'] = redis_client
        while True:
            task_data = redis_client.brpop('task_queue')
            if task_data:
                task_id_bytes = task_data[1]
                task_id_str = task_id_bytes.decode('utf-8')
                try:
                    task_id = int(task_id_str)
                    logging.info(f"Worker {worker_id} picked up Task ID: {task_id}")

                    # Use gRPC to start the task
                    grpc_channel = grpc.insecure_channel('localhost:50052')
                    task_execution_stub = task_execution_pb2_grpc.TaskExecutionServiceStub(grpc_channel)
                    task_execution_stub.StartTask(task_execution_pb2.TaskIdRequest(taskId=task_id))

                    process_task(task_id, socketio)  # Pass socketio to process_task
                except ValueError:
                    logging.error(f"Invalid task ID retrieved from queue: {task_id_str}")

def start_worker(socketio, app, num_workers=10):
    redis_client = app.config.get('redis_client', None)
    if not redis_client:
        redis_client = redis.Redis(host='redis_pad', port=6379)
        app.config['redis_client'] = redis_client
    for i in range(num_workers):
        thread = threading.Thread(target=worker, args=(i, socketio, app), daemon=True)
        thread.start()
        logging.info(f"Started worker thread {i}")

def monitor_redis_queue():
    redis_client = redis.Redis(host='redis_pad', port=6379)
    critical_threshold = 60
    check_interval = 30
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

def serve_grpc(app, socketio):
    import grpc
    from concurrent import futures
    import task_execution_pb2_grpc
    from services import TaskExecutionServicer

    with app.app_context():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        task_execution_pb2_grpc.add_TaskExecutionServiceServicer_to_server(TaskExecutionServicer(app, socketio), server)
        server.add_insecure_port('[::]:50052')
        server.start()
        logging.info("gRPC server for Task Execution Service started on port 50052.")
        server.wait_for_termination()

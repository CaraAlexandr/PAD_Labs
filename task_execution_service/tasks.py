import time
import grpc
import task_management_pb2
import task_management_pb2_grpc
from models import db
import random

def process_task(task_id, socketio):
    # Simulate task processing based on task type
    task_type = get_task_type(task_id)
    if task_type in ['word_count', 'sentiment_analysis', 'text_summarization']:
        time.sleep(random.uniform(1, 3))
    elif task_type in ['image_resize', 'apply_filter']:
        time.sleep(random.uniform(2, 5))
    elif task_type in ['calculate_statistics', 'find_patterns']:
        time.sleep(random.uniform(3, 6))
    elif task_type in ['weather_data', 'currency_conversion']:
        time.sleep(random.uniform(1, 2))
    elif task_type in ['simulate_backup', 'large_file_processing']:
        time.sleep(random.uniform(5, 10))
    else:
        time.sleep(2)
    # Update Task Management Service via gRPC
    with grpc.insecure_channel('task_management_service:50051') as channel:
        stub = task_management_pb2_grpc.TaskManagementStub(channel)
        response = stub.UpdateTaskStatus(task_management_pb2.TaskStatusUpdate(
            task_id=task_id,
            status='completed'
        ))
    # Notify clients via WebSocket
    socketio.emit('task_update', {'task_id': task_id, 'status': 'completed'}, broadcast=True)

def get_task_type(task_id):
    # Retrieve task type from Task Management Service
    # For simplicity, returning a random task type
    task_types = ['word_count', 'image_resize', 'calculate_statistics', 'weather_data', 'simulate_backup']
    return random.choice(task_types)

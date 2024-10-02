# task_execution_service/app/services.py
import grpc
import task_execution_pb2
import task_execution_pb2_grpc
from .extensions import db, socketio
import redis
from flask import Flask

class TaskExecutionServicer(task_execution_pb2_grpc.TaskExecutionServiceServicer):
    def __init__(self, app: Flask):
        self.app = app
        self.redis_client = redis.Redis(host='redis_pad', port=6379)

    def StartTask(self, request, context):
        with self.app.app_context():
            task_id = request.task_id
            self.redis_client.lpush('task_queue', task_id)
            fetch_task_and_process(task_id, socketio)
            return task_execution_pb2.StartTaskResponse(message="Task started successfully")

    def GetTaskStatus(self, request, context):
        from models import Task
        with self.app.app_context():
            task = Task.query.get(request.task_id)
            if task:
                return task_execution_pb2.GetTaskStatusResponse(
                    status=task.status,
                    result=task.result or ""
                )
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Task with ID {request.task_id} not found")
                return task_execution_pb2.GetTaskStatusResponse()

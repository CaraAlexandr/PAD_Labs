# task_execution_service/app/services.py
import grpc
from grpc import task_execution_pb2
from grpc import task_execution_pb2_grpc
from flask import current_app
from models import Worker, Task
from extensions import db
import redis

class TaskExecutionServicer(task_execution_pb2_grpc.TaskExecutionServiceServicer):
    def __init__(self, app):
        self.app = app

    def ExecuteTask(self, request, context):
        # Implement the gRPC ExecuteTask method
        task_id = request.task_id
        # Fetch and process the task
        task = Task.query.get(task_id)
        if not task:
            context.set_details('Task not found')
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return task_execution_pb2.ExecuteTaskResponse()

        # Simulate task execution
        task.status = "completed"
        task.result = "Task executed successfully."
        db.session.commit()

        return task_execution_pb2.ExecuteTaskResponse(message="Task executed successfully.")

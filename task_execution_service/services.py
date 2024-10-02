import task_execution_pb2
import task_execution_pb2_grpc
from flask import current_app
from extensions import db
from models import Task
import grpc

class TaskExecutionServicer(task_execution_pb2_grpc.TaskExecutionServiceServicer):
    def StartTask(self, request, context):
        with current_app.app_context():
            task = Task.query.get(request.task_id)
            if not task:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f'Task with ID {request.task_id} not found')
                return task_execution_pb2.TaskExecutionResponse()
            # Update task status to 'queued'
            task.status = 'queued'
            db.session.commit()
            # Add task ID to Redis queue
            from app import redis_client  # Import here to avoid circular import
            redis_client.lpush('task_queue', task.id)
            return task_execution_pb2.TaskExecutionResponse(
                task_id=task.id,
                status='queued',
                result='Task queued for execution'
            )

    def GetTaskStatus(self, request, context):
        with current_app.app_context():
            task = Task.query.get(request.task_id)
            if not task:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f'Task with ID {request.task_id} not found')
                return task_execution_pb2.TaskExecutionResponse()
            return task_execution_pb2.TaskExecutionResponse(
                task_id=task.id,
                status=task.status,
                result='Task status retrieved'
            )

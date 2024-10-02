# task_management_service/app/services.py
import grpc
from grpc import task_management_pb2
from grpc import task_management_pb2_grpc
from flask import current_app
from models import Task
from extensions import db
import redis

class TaskManagementServicer(task_management_pb2_grpc.TaskManagementServiceServicer):
    def __init__(self, app):
        self.app = app

    def CreateTask(self, request, context):
        # Implement gRPC CreateTask method
        task = Task(
            description=request.description,
            task_type=request.task_type,
            payload=request.payload,
            status="pending"
        )
        db.session.add(task)
        db.session.commit()

        # Push to Redis
        redis_client = redis.Redis(host='redis_pad', port=6379)
        redis_client.lpush('task_queue', task.id)

        return task_management_pb2.CreateTaskResponse(id=task.id)

    def GetTask(self, request, context):
        task = Task.query.get(request.id)
        if not task:
            context.set_details('Task not found')
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return task_management_pb2.GetTaskResponse()

        return task_management_pb2.GetTaskResponse(
            id=task.id,
            description=task.description,
            task_type=task.task_type,
            payload=task.payload,
            status=task.status,
            result=task.result or "",
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
            finished_at=task.finished_at.isoformat() if task.finished_at else ""
        )

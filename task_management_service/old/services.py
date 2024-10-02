# task_management_service/app/services.py
import grpc
import task_management_pb2
import task_management_pb2_grpc
from models import Task
from extensions import db
import redis
from flask import Flask
from datetime import datetime

class TaskManagementServicer(task_management_pb2_grpc.TaskManagementServiceServicer):
    def __init__(self, app: Flask):
        self.app = app
        self.redis_client = redis.Redis(host='redis_pad', port=6379)

    def CreateTask(self, request, context):
        with self.app.app_context():
            new_task = Task(description=request.description, task_type=request.task_type, payload=request.payload)
            db.session.add(new_task)
            db.session.commit()

            self.redis_client.lpush('task_queue', new_task.id)

            return task_management_pb2.TaskResponse(
                id=new_task.id,
                description=new_task.description,
                task_type=new_task.task_type,
                status=new_task.status,
                payload=new_task.payload,
                result=new_task.result or "",
                created_at=new_task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                updated_at=new_task.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                finished_at=new_task.finished_at.strftime('%Y-%m-%d %H:%M:%S') if new_task.finished_at else ""
            )

    def GetTaskById(self, request, context):
        with self.app.app_context():
            task = Task.query.get(request.id)
            if task:
                return task_management_pb2.TaskResponse(
                    id=task.id,
                    description=task.description,
                    task_type=task.task_type,
                    status=task.status,
                    payload=task.payload,
                    result=task.result or "",
                    created_at=task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    updated_at=task.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    finished_at=task.finished_at.strftime('%Y-%m-%d %H:%M:%S') if task.finished_at else ""
                )
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Task with ID {request.id} not found")
                return task_management_pb2.TaskResponse()

    def ListTasks(self, request, context):
        with self.app.app_context():
            tasks_query = Task.query.all()
            tasks = [
                task_management_pb2.TaskResponse(
                    id=task.id,
                    description=task.description,
                    task_type=task.task_type,
                    status=task.status,
                    payload=task.payload,
                    result=task.result or "",
                    created_at=task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    updated_at=task.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    finished_at=task.finished_at.strftime('%Y-%m-%d %H:%M:%S') if task.finished_at else ""
                ) for task in tasks_query
            ]
        return task_management_pb2.TasksResponse(tasks=tasks)

    def UpdateTaskStatus(self, request, context):
        with self.app.app_context():
            task = Task.query.get(request.task_id)
            if task:
                task.status = request.status
                task.result = request.result
                if request.status == 'completed':
                    task.finished_at = datetime.utcnow()
                db.session.commit()
                return task_management_pb2.TaskResponse(
                    id=task.id,
                    description=task.description,
                    task_type=task.task_type,
                    status=task.status,
                    payload=task.payload,
                    result=task.result or "",
                    created_at=task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    updated_at=task.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    finished_at=task.finished_at.strftime('%Y-%m-%d %H:%M:%S') if task.finished_at else ""
                )
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Task with ID {request.task_id} not found")
                return task_management_pb2.TaskResponse()

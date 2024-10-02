import task_management_pb2
import task_management_pb2_grpc
from models import Task
from extensions import db
import redis
from flask import Flask

class TaskManagementServicer(task_management_pb2_grpc.TaskManagementServiceServicer):
    def __init__(self, app: Flask):
        self.app = app
        self.redis_client = redis.Redis(host='redis_pad', port=6379)  # Ensure host matches Docker Compose

    def CreateTask(self, request, context):
        with self.app.app_context():
            new_task = Task(description=request.description, task_type=request.task_type, status='pending')
            db.session.add(new_task)
            db.session.commit()

            # Add the task to the Redis queue
            self.redis_client.lpush('task_queue', new_task.id)

            return task_management_pb2.TaskResponse(
                id=new_task.id,
                description=new_task.description,
                task_type=new_task.task_type,
                status=new_task.status
            )

    def GetTaskById(self, request, context):
        with self.app.app_context():
            task = Task.query.get(request.id)
            if task:
                return task_management_pb2.TaskResponse(
                    id=task.id,
                    description=task.description,
                    task_type=task.task_type,
                    status=task.status
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
                    status=task.status
                ) for task in tasks_query
            ]
        return task_management_pb2.TasksResponse(tasks=tasks)

    def UpdateTaskStatus(self, request, context):
        with self.app.app_context():
            task = Task.query.get(request.task_id)
            if task:
                task.status = request.status
                db.session.commit()
                return task_management_pb2.TaskResponse(
                    id=task.id,
                    description=task.description,
                    task_type=task.task_type,
                    status=task.status
                )
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Task with ID {request.task_id} not found")
                return task_management_pb2.TaskResponse()

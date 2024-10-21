# task_management_service/services.py
import grpc
import task_management_pb2
import task_management_pb2_grpc
from models import Task
from extensions import db
import redis
from flask import Flask
import logging

class TaskManagementServicer(task_management_pb2_grpc.TaskManagementServiceServicer):
    def __init__(self, app: Flask):
        self.app = app
        self.redis_client = redis.Redis(host='redis_pad', port=6379)
        logging.basicConfig(level=logging.INFO)

    def CreateTask(self, request, context):
        with self.app.app_context():
            logging.info(f"Received CreateTask request: {request}")
            new_task = Task(
                description=request.description,
                task_type=request.task_type,
                status='pending',
                payload=request.payload
            )
            db.session.add(new_task)
            db.session.commit()

            # Add the task to the Redis queue
            self.redis_client.lpush('task_queue', new_task.id)

            logging.info(f"Created Task ID {new_task.id} and added to queue.")

            return task_management_pb2.TaskResponse(
                id=new_task.id,
                description=new_task.description,
                task_type=new_task.task_type,
                status=new_task.status,
                payload=new_task.payload,
                result=new_task.result or ""
            )

    def GetTaskById(self, request, context):
        with self.app.app_context():
            task = Task.query.get(request.id)
            if task:
                logging.info(f"Retrieved Task ID {task.id}")
                return task_management_pb2.TaskResponse(
                    id=task.id,
                    description=task.description,
                    task_type=task.task_type,
                    status=task.status,
                    payload=task.payload,
                    result=task.result or ""
                )
            else:
                logging.warning(f"Task with ID {request.id} not found.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Task with ID {request.id} not found")
                return task_management_pb2.TaskResponse()

    def UpdateTaskStatus(self, request, context):
        with self.app.app_context():
            task = Task.query.get(request.task_id)
            if task:
                task.status = request.status
                task.result = request.result  # Save the result
                db.session.commit()
                logging.info(f"Updated Task ID {task.id} status to {task.status}.")
                return task_management_pb2.TaskStatusResponse(success=True)
            else:
                logging.warning(f"Task with ID {request.task_id} not found for status update.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Task with ID {request.task_id} not found")
                return task_management_pb2.TaskStatusResponse(success=False)

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
                    result=task.result or ""
                ) for task in tasks_query
            ]
        return task_management_pb2.TasksResponse(tasks=tasks)

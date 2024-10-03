# task_execution_service/services.py

import task_execution_pb2
import task_execution_pb2_grpc
import task_management_pb2
import task_management_pb2_grpc
import grpc
import json
from flask import Flask
import logging

class TaskExecutionServicer(task_execution_pb2_grpc.TaskExecutionServiceServicer):
    def __init__(self, app: Flask):
        self.app = app
        self.task_management_channel = grpc.insecure_channel('task_management_service:50051')
        self.task_management_stub = task_management_pb2_grpc.TaskManagementServiceStub(self.task_management_channel)
        logging.basicConfig(level=logging.INFO)

    def StartTask(self, request, context):
        task_id = request.taskId  # Ensure the field name matches the .proto file
        logging.info(f"Received StartTask request for Task ID: {task_id}")

        # Fetch task details from Task Management Service
        try:
            task_response = self.task_management_stub.GetTaskById(
                task_management_pb2.TaskIdRequest(id=task_id)
            )
            logging.info(f"Fetched Task Details: {task_response}")
        except grpc.RpcError as e:
            logging.error(f"gRPC Error while fetching task: {e.code()} - {e.details()}")
            context.set_code(e.code())
            context.set_details(e.details())
            return task_execution_pb2.TaskExecutionResponse()

        if not task_response.id:
            logging.error(f"Task with ID {task_id} not found.")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Task with ID {task_id} not found")
            return task_execution_pb2.TaskExecutionResponse()

        # Execute the task
        result = self.execute_task(task_response)
        logging.info(f"Execution Result for Task ID {task_id}: {result}")

        # Update task status and result in Task Management Service
        try:
            update_response = self.task_management_stub.UpdateTaskStatus(
                task_management_pb2.TaskStatusUpdateRequest(
                    task_id=task_id,
                    status='completed',
                    result=json.dumps(result)  # Serialize result to JSON string
                )
            )
            logging.info(f"Task ID {task_id} status updated successfully.")
        except grpc.RpcError as e:
            logging.error(f"gRPC Error while updating task status: {e.code()} - {e.details()}")
            context.set_code(e.code())
            context.set_details(e.details())
            return task_execution_pb2.TaskExecutionResponse()

        return task_execution_pb2.TaskExecutionResponse(
            taskId=task_id,
            status='completed',
            result=json.dumps(result)
        )

    def execute_task(self, task):
        # Implement the actual task execution logic based on task_type
        if task.task_type == 'word_count':
            word_count = len(task.payload.split())
            return {"word_count": word_count}
        # Add other task types as needed
        return {}

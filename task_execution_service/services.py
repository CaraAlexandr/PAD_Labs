# services.py
import task_execution_pb2
import task_execution_pb2_grpc
import task_management_pb2
import task_management_pb2_grpc
import grpc
import json
from flask import Flask
from flask_socketio import SocketIO
import logging

class TaskExecutionServicer(task_execution_pb2_grpc.TaskExecutionServiceServicer):
    def __init__(self, app: Flask, socketio: SocketIO):
        self.app = app
        self.socketio = socketio
        self.task_management_channel = grpc.insecure_channel('task_management_service:50051')
        self.task_management_stub = task_management_pb2_grpc.TaskManagementServiceStub(self.task_management_channel)
        logging.basicConfig(level=logging.INFO)

    def StartTask(self, request, context):
        task_id = request.taskId
        logging.info(f"Received StartTask request for Task ID: {task_id}")

        # Fetch task details from Task Management Service
        try:
            task_response = self.task_management_stub.GetTaskById(
                task_management_pb2.TaskIdRequest(id=task_id)
            )
            logging.info(f"Fetched Task Details: {task_response}")
        except grpc.RpcError as e:
            logging.error(f"gRPC Error: {e}")
            context.set_code(e.code())
            context.set_details(e.details())
            return task_execution_pb2.TaskExecutionResponse()

        # Emit task update when task starts
        self._broadcast_task_update(task_id, 'started')

        # Execute the task and get the result
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

        # Emit task completion updates
        self._broadcast_task_update(task_id, 'completed', json.dumps(result))

        return task_execution_pb2.TaskExecutionResponse(
            taskId=task_id,
            status='completed',
            result=json.dumps(result)
        )

    def execute_task(self, task):
        if task.task_type == 'word_count':
            return {"word_count": len(task.payload.split())}
        return {}

    def _broadcast_task_update(self, task_id, status, result=None):
        """
        Broadcasts task updates to both the specific task room and the general room.
        """
        try:
            logging.info(f"Broadcasting task update: {task_id} status: {status}")
            with self.app.app_context():
                # Emit to specific task room
                self.socketio.emit('task_update', {
                    'id': task_id,
                    'status': status,
                    'result': result
                }, namespace='/lobby', room=str(task_id))

                # Emit to general lobby
                self.socketio.emit('task_update', {
                    'id': task_id,
                    'status': status,
                    'result': result
                }, namespace='/lobby', room='all_tasks')

                logging.info(f"Broadcast successful: Task ID {task_id} - Status {status}")

        except Exception as e:
            logging.error(f"Error broadcasting task update for Task ID {task_id}: {e}")

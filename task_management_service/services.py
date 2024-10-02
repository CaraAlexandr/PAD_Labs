import task_management_pb2
import task_management_pb2_grpc
from models import Task
from extensions import db

class TaskManagementServicer(task_management_pb2_grpc.TaskManagementServicer):
    def UpdateTaskStatus(self, request, context):
        task = Task.query.get(request.task_id)
        if task:
            task.status = request.status
            db.session.commit()
            return task_management_pb2.UpdateResponse(message='Task status updated.')
        else:
            return task_management_pb2.UpdateResponse(message='Task not found.')
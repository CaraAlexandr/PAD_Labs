# task_management_service/app/main.py
import grpc
from concurrent import futures
import time
from app.services import TaskManagementServicer
from app import create_app
from flask import Blueprint, jsonify, request
from app.models import Task
from app.extensions import db
import redis

def serve_grpc(app):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = TaskManagementServicer(app)
    from app.grpc import task_management_pb2_grpc
    task_management_pb2_grpc.add_TaskManagementServiceServicer_to_server(servicer, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Task Management Service gRPC server started on port 50051.")
    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)

def run_rest(app):
    import redis

    redis_client = redis.Redis(host='redis_pad', port=6379)

    bp = Blueprint('api', __name__)

    @bp.route('/tasks', methods=['POST'])
    def create_task():
        data = request.get_json()
        description = data.get('description')
        task_type = data.get('task_type')
        payload = data.get('payload')

        if not all([description, task_type, payload]):
            return jsonify({'error': 'Missing fields'}), 400

        new_task = Task(description=description, task_type=task_type, payload=payload)
        db.session.add(new_task)
        db.session.commit()

        redis_client.lpush('task_queue', new_task.id)

        # Health Monitoring: Check if queue length exceeds 60
        queue_length = redis_client.llen('task_queue')
        if queue_length > 60:
            # Raise an alert (could be a log, email, or other notification)
            # For simplicity, log a warning
            app.logger.warning(f"Critical Alert: Task queue length exceeded 60. Current length: {queue_length}")

        return jsonify({
            'id': new_task.id,
            'description': new_task.description,
            'task_type': new_task.task_type,
            'payload': new_task.payload,
            'status': new_task.status,
            'result': new_task.result or "",
            'created_at': new_task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': new_task.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'finished_at': new_task.finished_at.strftime('%Y-%m-%d %H:%M:%S') if new_task.finished_at else ""
        }), 201

    @bp.route('/tasks/<int:id>', methods=['GET'])
    def get_task(id):
        task = Task.query.get(id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        return jsonify({
            'id': task.id,
            'description': task.description,
            'task_type': task.task_type,
            'payload': task.payload,
            'status': task.status,
            'result': task.result or "",
            'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': task.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'finished_at': task.finished_at.strftime('%Y-%m-%d %H:%M:%S') if task.finished_at else ""
        }), 200

    @bp.route('/tasks', methods=['GET'])
    def list_tasks():
        tasks = Task.query.all()
        tasks_list = [{
            'id': task.id,
            'description': task.description,
            'task_type': task.task_type,
            'payload': task.payload,
            'status': task.status,
            'result': task.result or "",
            'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': task.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'finished_at': task.finished_at.strftime('%Y-%m-%d %H:%M:%S') if task.finished_at else ""
        } for task in tasks]
        return jsonify(tasks_list), 200

    @bp.route('/tasks/<int:id>', methods=['DELETE'])
    def delete_task(id):
        task = Task.query.get(id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'}), 200

    @bp.route('/status', methods=['GET'])
    def status():
        return jsonify({'status': 'Task Management Service is running'}), 200

    app.register_blueprint(bp)

    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    import threading
    grpc_thread = threading.Thread(target=serve_grpc, args=(app,))
    grpc_thread.start()
    run_rest(app)

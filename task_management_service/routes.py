from flask import Blueprint, jsonify, request
from models import Task
import redis
from extensions import db

task_bp = Blueprint('task_bp', __name__)
status_bp = Blueprint('status_bp', __name__)

redis_client = redis.Redis(host='redis', port=6379)

@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    task = Task(description=data['description'], task_type=data['task_type'], status='pending')
    db.session.add(task)
    db.session.commit()
    redis_client.lpush('task_queue', task.id)
    return jsonify({'id': task.id, 'status': task.status}), 201

@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get(task_id)
    if task:
        return jsonify({'id': task.id, 'status': task.status}), 200
    else:
        return jsonify({'error': 'Task not found'}), 404

@task_bp.route('/tasks', methods=['GET'])
def list_tasks():
    tasks = Task.query.all()
    return jsonify([{'id': t.id, 'status': t.status} for t in tasks]), 200

@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted'}), 200
    else:
        return jsonify({'error': 'Task not found'}), 404

@status_bp.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'Task Management Service is running'}), 200

# task_management_service/routes.py

from flask import Blueprint, jsonify, request
from models import Task
import redis
from extensions import db
import datetime

task_bp = Blueprint('task_bp', __name__)
status_bp = Blueprint('status_bp', __name__)

# Update Redis host to 'redis_pad' to match Docker Compose
redis_client = redis.Redis(host='redis_pad', port=6379)


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    required_fields = ['description', 'task_type', 'payload']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': f"Missing fields. Required fields: {required_fields}"}), 400

    task = Task(
        description=data['description'],
        task_type=data['task_type'],
        status='pending',
        payload=data['payload'],
        result="",  # Initialize result as empty string
        start_time=datetime.datetime.utcnow()
    )
    db.session.add(task)
    db.session.commit()
    redis_client.lpush('task_queue', task.id)
    return jsonify({
        'id': task.id,
        'status': task.status,
        'task_type': task.task_type
    }), 201


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get(task_id)
    if task:
        return jsonify({
            'id': task.id,
            'description': task.description,
            'task_type': task.task_type,
            'status': task.status,
            'payload': task.payload,
            'result': task.result,
            'start_time': task.start_time.isoformat() if task.start_time else None,
            'end_time': task.end_time.isoformat() if task.end_time else None
        }), 200
    else:
        return jsonify({'error': 'Task not found'}), 404


@task_bp.route('/tasks', methods=['GET'])
def list_tasks():
    page_number = request.args.get('page_number', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)
    tasks_query = Task.query.offset((page_number - 1) * page_size).limit(page_size).all()
    return jsonify([{
        'id': t.id,
        'description': t.description,
        'task_type': t.task_type,
        'status': t.status,
        'payload': t.payload,
        'result': t.result,
        'start_time': t.start_time.isoformat() if t.start_time else None,
        'end_time': t.end_time.isoformat() if t.end_time else None
    } for t in tasks_query]), 200


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

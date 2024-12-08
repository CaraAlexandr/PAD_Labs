import json
import os
from flask import Blueprint, request, jsonify
from extensions import db
from models import Task
from rediscluster import RedisCluster

os.environ.pop('REDIS_HOST', None)
os.environ.pop('REDIS_PORT', None)
os.environ.pop('REDIS_URL', None)

task_bp = Blueprint('task_bp', __name__)

redis_nodes = os.environ.get('REDIS_CLUSTER_NODES', 'redis-node-1:7001,redis-node-2:7002,redis-node-3:7003')
startup_nodes = [{"host": x.split(":")[0], "port": int(x.split(":")[1])} for x in redis_nodes.split(",")]
redis_queue = RedisCluster(
    startup_nodes=startup_nodes,
    decode_responses=True,
    skip_full_coverage_check=True
)

@task_bp.route('/', methods=['POST'])
def create_task():
    data = request.json
    task = Task(
        description=data.get('description'),
        task_type=data.get('task_type'),
        payload=json.dumps(data.get('payload')),
        status='queued'
    )
    db.session.add(task)
    db.session.commit()
    redis_queue.lpush('task_queue', task.id)
    return jsonify({'message': 'Task created', 'task_id': task.id}), 201

@task_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify({
        'id': task.id,
        'description': task.description,
        'task_type': task.task_type,
        'status': task.status,
        'payload': json.loads(task.payload),
        'result': task.result,
        'start_time': task.start_time,
        'end_time': task.end_time
    })

@task_bp.route('/', methods=['GET'])
def list_tasks():
    tasks = Task.query.all()
    return jsonify([{
        'id': t.id,
        'description': t.description,
        'task_type': t.task_type,
        'status': t.status,
        'payload': json.loads(t.payload),
        'result': t.result,
        'start_time': t.start_time,
        'end_time': t.end_time
    } for t in tasks])

@task_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.json
    task.description = data.get('description', task.description)
    task.task_type = data.get('task_type', task.task_type)
    task.payload = json.dumps(data.get('payload', json.loads(task.payload)))
    db.session.commit()
    return jsonify({'message': 'Task updated'})

@task_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'})

@task_bp.route('/private/<int:task_id>', methods=['PUT'])
def update_private_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.json
    if 'description' in data:
        task.description = data['description']
    if 'task_type' in data:
        task.task_type = data['task_type']
    if 'payload' in data:
        task.payload = json.dumps(data['payload'])
    if 'status' in data:
        task.status = data['status']
    if 'result' in data:
        task.result = data['result']
    if 'start_time' in data:
        task.start_time = data['start_time']
    if 'end_time' in data:
        task.end_time = data['end_time']
    db.session.commit()
    return jsonify({'message': 'Task updated'}), 200

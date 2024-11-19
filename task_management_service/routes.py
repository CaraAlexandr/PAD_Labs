import json
import os

# import redis
from rediscluster import RedisCluster
from flask import Blueprint, request, jsonify

from extensions import db
from models import Task

task_bp = Blueprint('task_bp', __name__)

# # Redis configuration
# redis_host = os.environ.get('REDIS_HOST', 'redis_pad')
# redis_port = int(os.environ.get('REDIS_PORT', 6379))
# redis_queue = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

redis_nodes = os.environ.get('REDIS_CLUSTER_NODES', 'redis-node-1:7001,redis-node-2:7002,redis-node-3:7003')
startup_nodes = [{"host": node.split(":")[0], "port": int(node.split(":")[1])} for node in redis_nodes.split(",")]
redis_queue = RedisCluster(startup_nodes=startup_nodes, decode_responses=True, skip_full_coverage_check=True)
queue_name = '{task_queue}'

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

    # Push task to Redis queue
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
        'id': task.id,
        'description': task.description,
        'task_type': task.task_type,
        'status': task.status,
        'payload': json.loads(task.payload),
        'result': task.result,
        'start_time': task.start_time,
        'end_time': task.end_time
    } for task in tasks])

@task_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.json
    print(data)
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

    # Update fields if they are provided in the request
    if 'description' in data:
        task.description = data.get('description', task.description)
    if 'task_type' in data:
        task.task_type = data.get('task_type', task.task_type)
    if 'payload' in data:
        # Ensure payload is a JSON string
        task.payload = json.dumps(data.get('payload'))
    if 'status' in data:
        task.status = data.get('status')
    if 'result' in data:
        task.result = data.get('result')
    if 'start_time' in data:
        task.start_time = data.get('start_time')
    if 'end_time' in data:
        task.end_time = data.get('end_time')

    db.session.commit()
    return jsonify({'message': 'Task updated'}), 200

from flask import Blueprint, jsonify, request
from models import Worker
from extensions import db

worker_bp = Blueprint('worker_bp', __name__)
status_bp = Blueprint('status_bp', __name__)

@worker_bp.route('/workers', methods=['GET'])
def get_workers():
    workers = Worker.query.all()
    return jsonify([{'id': w.id, 'name': w.name, 'status': w.status} for w in workers]), 200

@worker_bp.route('/workers', methods=['POST'])
def add_worker():
    data = request.get_json()
    worker = Worker(name=data['name'], status='active')
    db.session.add(worker)
    db.session.commit()
    return jsonify({'id': worker.id, 'name': worker.name}), 201

@worker_bp.route('/workers/<int:worker_id>', methods=['DELETE'])
def remove_worker(worker_id):
    worker = Worker.query.get(worker_id)
    if worker:
        db.session.delete(worker)
        db.session.commit()
        return jsonify({'message': 'Worker removed'}), 200
    else:
        return jsonify({'error': 'Worker not found'}), 404

@status_bp.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'Task Execution Service is running'}), 200

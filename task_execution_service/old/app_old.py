# task_execution_service/app/main.py
import grpc
from concurrent import futures
import time
from .services import TaskExecutionServicer
import task_execution_pb2_grpc
from app_old import create_app
from flask import Blueprint, jsonify, request
from flask_socketio import join_room, leave_room, emit
import eventlet
eventlet.monkey_patch()

def serve_grpc(app):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = TaskExecutionServicer(app)
    task_execution_pb2_grpc.add_TaskExecutionServiceServicer_to_server(servicer, server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Task Execution Service gRPC server started on port 50052.")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

def run_rest(app):
    from .models import Worker
    from .extensions import db, socketio

    bp = Blueprint('api', __name__)

    @bp.route('/api/workers', methods=['GET'])
    def get_workers():
        workers = Worker.query.all()
        workers_list = [{'id': worker.id, 'startTime': worker.start_time.isoformat()} for worker in workers]
        return jsonify(workers_list), 200

    @bp.route('/api/workers', methods=['POST'])
    def add_worker():
        data = request.get_json()
        worker_id = data.get('id')
        if not worker_id:
            return jsonify({'error': 'Worker ID is required'}), 400
        if Worker.query.get(worker_id):
            return jsonify({'error': 'Worker already exists'}), 400
        new_worker = Worker(id=worker_id)
        db.session.add(new_worker)
        db.session.commit()
        return jsonify({'workerId': new_worker.id}), 201

    @bp.route('/api/workers/<string:id>', methods=['DELETE'])
    def remove_worker(id):
        worker = Worker.query.get(id)
        if not worker:
            return jsonify({'error': 'Worker not found'}), 404
        db.session.delete(worker)
        db.session.commit()
        return jsonify({'message': 'Worker removed successfully'}), 200

    @bp.route('/status', methods=['GET'])
    def status():
        return jsonify({'status': 'Task Execution Service is running'}), 200

    app.register_blueprint(bp)

    @socketio.on('join', namespace='/lobby')
    def handle_join(data):
        task_id = data.get('task_id')
        if task_id:
            room = f"task_{task_id}"
            join_room(room)
            emit('joined', {'room': room})
        else:
            join_room('all_tasks')
            emit('joined', {'room': 'all_tasks'})

    @socketio.on('leave', namespace='/lobby')
    def handle_leave(data):
        task_id = data.get('task_id')
        if task_id:
            room = f"task_{task_id}"
            leave_room(room)
            emit('left', {'room': room})
        else:
            leave_room('all_tasks')
            emit('left', {'room': 'all_tasks'})

    socketio.run(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    import threading
    grpc_thread = threading.Thread(target=serve_grpc, args=(app,))
    grpc_thread.start()
    run_rest(app)

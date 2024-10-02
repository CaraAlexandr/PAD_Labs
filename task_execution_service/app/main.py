# task_execution_service/app/main.py
import grpc
from concurrent import futures
import time
from services import TaskExecutionServicer
from app import create_app
from flask import Blueprint, jsonify, request
from flask_socketio import SocketIO
import eventlet
import redis
import logging
import threading

eventlet.monkey_patch()

def serve_grpc(app):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = TaskExecutionServicer(app)
    from app.grpc import task_execution_pb2_grpc
    task_execution_pb2_grpc.add_TaskExecutionServiceServicer_to_server(servicer, server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Task Execution Service gRPC server started on port 50052.")
    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)

def run_rest(app):
    from app.models import Worker
    from app.extensions import db, socketio
    import redis

    redis_client = redis.Redis(host='redis_pad', port=6379)

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

    # Health Monitoring: Check Redis task queue length
    def monitor_redis_queue():
        while True:
            try:
                queue_length = redis_client.llen('task_queue')
                if queue_length > 60:
                    # Raise an alert (send Slack notification)
                    alert_message = f"Critical Alert: Task queue length exceeded 60. Current length: {queue_length}"
                    app.logger.warning(alert_message)
                    # send_slack_alert(alert_message)  # Uncomment if alerting is implemented
            except Exception as e:
                app.logger.error(f"Error monitoring Redis queue: {str(e)}")
            time.sleep(30)  # Check every 30 seconds

    monitoring_thread = threading.Thread(target=monitor_redis_queue)
    monitoring_thread.daemon = True
    monitoring_thread.start()

    socketio.run(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    grpc_thread = threading.Thread(target=serve_grpc, args=(app,))
    grpc_thread.start()
    run_rest(app)

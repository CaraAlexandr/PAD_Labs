import threading
from rediscluster import RedisCluster
import json
import requests
from time import sleep
from models import WorkerModel
from extensions import db
from datetime import datetime
import os
from tasks import execute_task
import logging

class Worker(threading.Thread):
    def __init__(self, worker_id, app_context):
        threading.Thread.__init__(self)
        self.worker_id = worker_id
        self.name = f"Worker-{worker_id}"
        self.app_context = app_context
        redis_nodes = os.environ.get('REDIS_CLUSTER_NODES', 'redis-node-1:7001,redis-node-2:7002,redis-node-3:7003')
        startup_nodes = [{"host": node.split(":")[0], "port": int(node.split(":")[1])} for node in redis_nodes.split(",")]
        self.redis_queue = RedisCluster(startup_nodes=startup_nodes, decode_responses=True, skip_full_coverage_check=True)
        self.queue_name = '{task_queue}'
        self.task_management_url = os.environ.get('TASK_MANAGEMENT_URL', 'http://task_management_service:5000/tasks')
        self.daemon = True
        self.logger = logging.getLogger(self.name)

    def run(self):
        with self.app_context:
            while True:
                try:
                    task_id = self.redis_queue.rpop(self.queue_name)
                    if task_id:
                        task_id = int(task_id)
                        self.logger.info(f"Processing task {task_id}")
                        self.process_task(task_id)
                    else:
                        sleep(1)
                except Exception as e:
                    self.logger.error(f"Error in worker: {e}")
                    sleep(5)

    def process_task(self, task_id):
        # Update worker status
        worker_record = WorkerModel.query.filter_by(name=self.name).first()
        if not worker_record:
            worker_record = WorkerModel(name=self.name)
            db.session.add(worker_record)
        worker_record.status = 'busy'
        worker_record.current_task_id = task_id
        worker_record.start_time = datetime.utcnow()
        db.session.commit()

        # Fetch task details
        response = requests.get(f"{self.task_management_url}/{task_id}")
        task_data = response.json()

        # Execute the task
        result = execute_task(task_data['task_type'], task_data['payload'])

        # Update task status
        update_data = {
            'status': 'completed',
            'result': result,
            'end_time': datetime.utcnow().isoformat()
        }
        requests.put(f"{self.task_management_url}/private/{task_id}", json=update_data)

        # Update worker status
        worker_record.status = 'idle'
        worker_record.current_task_id = None
        worker_record.end_time = datetime.utcnow()
        db.session.commit()

class WorkerManager:
    def __init__(self, app, max_workers=5):
        self.app = app
        self.max_workers = max_workers
        self.workers = []

    def start_workers(self):
        for i in range(self.max_workers):
            worker = Worker(worker_id=i+1, app_context=self.app.app_context())
            worker.start()
            self.workers.append(worker)

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    worker_manager = WorkerManager(app)
    worker_manager.start_workers()
    # Keep the main thread alive
    while True:
        sleep(60)

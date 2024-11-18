import os
import threading
from datetime import datetime
from time import sleep

import redis
import requests

from extensions import db
from models import WorkerModel
from tasks import execute_task


class Worker(threading.Thread):
    def __init__(self, worker_id):
        threading.Thread.__init__(self)
        self.worker_id = worker_id
        self.name = f"Worker-{worker_id}"
        self.redis_host = os.environ.get('REDIS_HOST', 'redis_pad')
        self.redis_port = int(os.environ.get('REDIS_PORT', 6379))
        self.redis_queue = redis.StrictRedis(host=self.redis_host, port=self.redis_port, db=0)
        self.task_management_url = os.environ.get('TASK_MANAGEMENT_URL', 'http://task_management_service:5000/tasks')
        self.daemon = True

    def run(self):
        while True:
            task_id = self.redis_queue.rpop('task_queue')
            if task_id:
                task_id = int(task_id)
                self.process_task(task_id)
            else:
                sleep(1)  # Wait before checking the queue again

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
        requests.put(f"{self.task_management_url}/{task_id}", json=update_data)

        # Update worker status
        worker_record.status = 'idle'
        worker_record.current_task_id = None
        worker_record.end_time = datetime.utcnow()
        db.session.commit()

class WorkerManager:
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.workers = []

    def start_workers(self):
        for i in range(self.max_workers):
            worker = Worker(worker_id=i+1)
            worker.start()
            self.workers.append(worker)

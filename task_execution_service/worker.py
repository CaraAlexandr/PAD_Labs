# workers.py

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

        # Initialize Redis Cluster connection
        redis_nodes = os.environ.get('REDIS_CLUSTER_NODES', 'redis-node-1:7001,redis-node-2:7002,redis-node-3:7003')
        startup_nodes = [{"host": x.split(":")[0], "port": int(x.split(":")[1])} for x in redis_nodes.split(",")]

        self.redis_queue = RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,
            skip_full_coverage_check=True
        )

        # Test Redis connection
        try:
            self.redis_queue.ping()
            print("Successfully connected to Redis cluster.")
        except Exception as e:
            print(f"Failed to connect to Redis cluster: {e}")
            raise e

        # Set the Redis queue name
        self.queue_name = os.environ.get('TASK_QUEUE_NAME', 'task_queue')  # Removed curly braces

        self.task_management_url = os.environ.get('TASK_MANAGEMENT_URL', 'http://task_management_service:5000/tasks')
        self.daemon = True

        # Initialize logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)  # More verbose logging

        # Configure logging handler (optional)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def run(self):
        with self.app_context:
            # Ensure this worker is known to the system
            self.ensure_worker_record_exists()

            while True:
                try:
                    task_id = self.redis_queue.rpop(self.queue_name)
                    if task_id:
                        self.logger.info(f"Pulled task {task_id} from Redis queue.")
                        try:
                            task_id = int(task_id)
                        except ValueError:
                            self.logger.error(f"Invalid task_id format: {task_id}. Skipping...")
                            continue
                        self.process_task(task_id)
                    else:
                        # No tasks available, wait a bit before polling again
                        sleep(1)
                except Exception as e:
                    self.logger.error(f"Error in worker loop: {e}", exc_info=True)
                    sleep(5)

    def ensure_worker_record_exists(self):
        # Ensure the worker record is present in DB
        worker_record = WorkerModel.query.filter_by(name=self.name).first()
        if not worker_record:
            worker_record = WorkerModel(name=self.name, status='idle')
            db.session.add(worker_record)
            db.session.commit()
            self.logger.info(f"Created new worker record for {self.name}.")
        else:
            # If the worker already exists, ensure it's idle
            worker_record.status = 'idle'
            worker_record.current_task_id = None
            worker_record.start_time = None
            worker_record.end_time = None
            db.session.commit()
            self.logger.info(f"Reset worker record for {self.name} to idle.")

    def update_worker_status(self, status, task_id=None):
        worker_record = WorkerModel.query.filter_by(name=self.name).first()
        if not worker_record:
            # If not found for some reason, recreate it
            worker_record = WorkerModel(name=self.name)
            db.session.add(worker_record)
            self.logger.warning(f"Worker record for {self.name} not found. Created a new one.")

        worker_record.status = status
        worker_record.current_task_id = task_id
        if status == 'busy' and task_id is not None:
            worker_record.start_time = datetime.utcnow()
            worker_record.end_time = None
        elif status == 'idle':
            worker_record.end_time = datetime.utcnow()
        db.session.commit()
        self.logger.debug(f"Updated worker status to {status}.")

    def process_task(self, task_id):
        # Phase 0: Mark the worker as busy with this task
        self.logger.debug(f"Worker {self.name} starting process for task {task_id}.")
        self.update_worker_status('busy', task_id)

        try:
            # PHASE 1: PREPARE (Set task in "in_progress" state)
            # Fetch the current task state
            response = requests.get(f"{self.task_management_url}/{task_id}")
            if response.status_code != 200:
                self.logger.error(f"Task {task_id} could not be fetched. Status code: {response.status_code}")
                # Re-queue the task or handle error
                self.redis_queue.lpush(self.queue_name, task_id)
                self.update_worker_status('idle')
                return

            task_data = response.json()
            if task_data.get('status') == 'completed':
                self.logger.info(f"Task {task_id} is already completed. Skipping...")
                self.update_worker_status('idle')
                return

            # Set task to in_progress before execution (prepare phase)
            update_data = {
                'status': 'in_progress',
                'start_time': datetime.utcnow().isoformat() + 'Z'
            }
            self.logger.debug(f"Setting task {task_id} to in_progress...")
            update_response = requests.put(f"{self.task_management_url}/private/{task_id}", json=update_data)
            if update_response.status_code != 200:
                self.logger.error(f"Failed to set task {task_id} to in_progress. Status: {update_response.status_code}")
                # Re-queue the task if needed or just fail
                self.redis_queue.lpush(self.queue_name, task_id)
                self.update_worker_status('idle')
                return

            # PHASE 2: EXECUTE the task
            self.logger.info(f"Executing task {task_id}...")
            # Ensure payload is serialized as a JSON string if required
            payload_serialized = json.dumps(task_data['payload'])
            result = execute_task(task_data['task_type'], payload_serialized)
            self.logger.info(f"Task {task_id} executed successfully with result: {result}")

            # PHASE 3: COMMIT (Set task to completed)
            commit_data = {
                'status': 'completed',
                'result': result,
                'end_time': datetime.utcnow().isoformat() + 'Z'
            }
            self.logger.debug(f"Committing task {task_id} as completed...")
            commit_response = requests.put(f"{self.task_management_url}/private/{task_id}", json=commit_data)

            if commit_response.status_code != 200:
                # Commit failed, we should rollback or mark as failed
                self.logger.error(f"Failed to commit (complete) task {task_id}. Rolling back to failed state.")
                rollback_data = {
                    'status': 'failed',
                    'result': 'Commit failed',
                    'end_time': datetime.utcnow().isoformat() + 'Z'
                }
                rollback_response = requests.put(f"{self.task_management_url}/private/{task_id}", json=rollback_data)
                if rollback_response.status_code == 200:
                    self.logger.info(f"Rolled back task {task_id} to failed state.")
                else:
                    self.logger.error(f"Failed to rollback task {task_id} to failed state. Status: {rollback_response.status_code}")

            # If everything is successful, we are done
            self.logger.info(f"Task {task_id} fully processed by {self.name}.")

        except Exception as e:
            self.logger.error(f"Error while processing task {task_id}: {e}", exc_info=True)
            # Attempt rollback if task was in progress:
            try:
                rollback_data = {
                    'status': 'failed',
                    'result': str(e),
                    'end_time': datetime.utcnow().isoformat() + 'Z'
                }
                rollback_response = requests.put(f"{self.task_management_url}/private/{task_id}", json=rollback_data)
                if rollback_response.status_code == 200:
                    self.logger.info(f"Rolled back task {task_id} to failed state due to error.")
                else:
                    self.logger.error(f"Failed to rollback task {task_id} to failed state after error. Status: {rollback_response.status_code}")
            except Exception as rollback_exc:
                self.logger.error(f"Failed to rollback task {task_id} after error: {rollback_exc}", exc_info=True)

        finally:
            # Phase 4: Set worker to idle
            self.update_worker_status('idle')
            self.logger.debug(f"Worker {self.name} is now idle.")

class WorkerManager:
    def __init__(self, app, max_workers=5):
        self.app = app
        self.max_workers = max_workers
        self.workers = []
        self.logger = logging.getLogger('WorkerManager')
        self.logger.setLevel(logging.INFO)

        # Configure logging handler (optional)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def start_workers(self):
        for i in range(self.max_workers):
            worker = Worker(worker_id=i+1, app_context=self.app.app_context())
            worker.start()
            self.workers.append(worker)
            self.logger.info(f"Started {worker.name}")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    worker_manager = WorkerManager(app)
    worker_manager.start_workers()
    # Keep the main thread alive
    while True:
        sleep(60)

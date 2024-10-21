# tasks.py
import logging

import grpc
import task_management_pb2
import task_management_pb2_grpc
from models import db, Task
import time
import json
from flask import current_app
from flask_socketio import SocketIO
import numpy as np
import requests
import random


# tasks.py
def process_task(task_id, socketio):
    with current_app.app_context():
        task = Task.query.get(task_id)
        if not task:
            logging.error(f"Task {task_id} not found")
            return
        try:
            # Emit in-progress update
            task.status = 'in_progress'
            db.session.commit()
            socketio.emit('task_update', {
                'id': task.id,
                'status': task.status,
                'result': task.result
            }, namespace='/lobby', room=str(task.id))

            # Task execution logic (simulated delay)
            time.sleep(2)
            result = execute_task_logic(task)

            # Update to completed
            task.status = 'completed'
            task.result = json.dumps(result)
            db.session.commit()

            # Emit completed update
            socketio.emit('task_update', {
                'id': task.id,
                'status': task.status,
                'result': task.result
            }, namespace='/lobby', room=str(task.id))

        except Exception as e:
            task.status = 'failed'
            task.result = str(e)
            db.session.commit()

            # Emit failure update
            socketio.emit('task_update', {
                'id': task.id,
                'status': task.status,
                'result': task.result
            }, namespace='/lobby', room=str(task.id))
            logging.error(f"Error processing task {task_id}: {e}")

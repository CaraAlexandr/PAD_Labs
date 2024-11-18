# task_execution/routes.py

import os
from flask import Blueprint, jsonify, request
from extensions import db
from models import Task
import requests
import json
from tasks import execute_task  # Ensure this is correctly implemented

from datetime import datetime

manual_exec_bp = Blueprint('manual_exec_bp', __name__)
execution_bp = Blueprint('execution_bp', __name__)

# URL of the Task Management Service
TASK_MANAGEMENT_URL = os.environ.get('TASK_MANAGEMENT_URL', 'http://task_management_service:8001/tasks')


@manual_exec_bp.route('/<int:task_id>', methods=['POST'])
def execute_task_manually(task_id):
    try:
        # Fetch task details from Task Management Service
        response = requests.get(f"{TASK_MANAGEMENT_URL}/{task_id}")
        if response.status_code != 200:
            return jsonify({'error': f'Task {task_id} not found'}), 404

        task_data = response.json()

        if task_data['status'] == 'completed':
            return jsonify({'message': f'Task {task_id} is already completed'}), 400

        # Execute the task
        # Serialize payload to JSON string if execute_task expects a string
        result = execute_task(task_data['task_type'], json.dumps(task_data['payload']))

        # Update task status in Task Management Service
        update_data = {
            'status': 'completed',
            'result': result,
            'end_time': datetime.utcnow().isoformat()
        }
        update_response = requests.put(f"{TASK_MANAGEMENT_URL}/{task_id}", json=update_data)
        if update_response.status_code != 200:
            return jsonify({'error': f'Failed to update task {task_id}'}), 500

        return jsonify({'message': f'Task {task_id} executed successfully', 'result': result}), 200

    except requests.exceptions.RequestException as e:
        # Handle HTTP request exceptions
        return jsonify({'error': f'HTTP Request failed: {str(e)}'}), 502
    except Exception as e:
        # Handle unexpected exceptions
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500


@execution_bp.route('/process', methods=['POST'])
def process_task():
    """
    Manually process a specific task by ID.
    Expected JSON Body:
    {
        "task_id": 300
    }
    """
    data = request.json
    task_id = data.get('task_id')
    if not task_id:
        return jsonify({'error': 'task_id is required'}), 400

    try:
        # Fetch task details from Task Management Service
        task_response = requests.get(f"{TASK_MANAGEMENT_URL}/{task_id}")
        if task_response.status_code != 200:
            return jsonify({'error': f'Failed to retrieve task {task_id}'}), task_response.status_code

        task = task_response.json()
        if task['status'] == 'completed':
            return jsonify({'message': f'Task {task_id} has already been completed.'}), 400

        # Update task status to 'in_progress'
        update_response = requests.put(
            f"{TASK_MANAGEMENT_URL}/private/{task_id}",
            json={'status': 'in_progress',
                  'start_time': datetime.utcnow().isoformat() + 'Z'
                  }
        )
        if update_response.status_code != 200:
            return jsonify(
                {'error': f'Failed to update task {task_id} status to in_progress'}), update_response.status_code

        # Execute the task
        # Serialize payload to JSON string if execute_task expects a string
        result = execute_task(task['task_type'], json.dumps(task['payload']))

        # Update task status to 'completed' with result
        update_response = requests.put(
            f"{TASK_MANAGEMENT_URL}/private/{task_id}",
            json={
                'status': 'completed',
                'result': result,
                'end_time': datetime.utcnow().isoformat() + 'Z'
            }
        )
        if update_response.status_code != 200:
            return jsonify(
                {'error': f'Failed to update task {task_id} status to completed'}), update_response.status_code

        return jsonify({'message': f'Task {task_id} has been processed successfully.', 'result': result}), 200
    except requests.exceptions.RequestException as e:
        # Handle HTTP request exceptions
        return jsonify({'error': f'HTTP Request failed: {str(e)}'}), 502
    except Exception as e:
        # Handle unexpected exceptions
        # Attempt to update task status to 'failed'
        try:
            requests.put(
                f"{TASK_MANAGEMENT_URL}/{task_id}",
                json={
                    'status': 'failed',
                    'result': str(e),
                    'end_time': datetime.utcnow().isoformat() + 'Z'
                }
            )
        except:
            pass  # If updating the task fails, ignore
        return jsonify({'error': f'Failed to process task {task_id}', 'details': str(e)}), 500

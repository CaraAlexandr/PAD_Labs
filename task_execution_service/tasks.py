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

def process_task(task_id, socketio):
    with current_app.app_context():
        # Retrieve the task from the database
        task = Task.query.get(task_id)
        if not task:
            return

        task_type = task.task_type
        task.status = 'in_progress'
        db.session.commit()

        # Notify clients via WebSocket
        socketio.emit('task_update', {'id': task_id, 'status': 'in_progress'}, namespace='/lobby', broadcast=True)

        # Execute the task based on its type
        if task_type == 'word_count':
            result = word_count(task.payload)
        elif task_type == 'sentiment_analysis':
            result = sentiment_analysis(task.payload)
        elif task_type == 'text_summarization':
            result = text_summarization(task.payload)
        elif task_type == 'image_resize':
            result = image_resize(task.payload)
        elif task_type == 'apply_filter':
            result = apply_filter(task.payload)
        elif task_type == 'calculate_statistics':
            result = calculate_statistics(task.payload)
        elif task_type == 'find_patterns':
            result = find_patterns(task.payload)
        elif task_type == 'weather_data':
            result = fetch_weather_data(task.payload)
        elif task_type == 'currency_conversion':
            result = currency_conversion(task.payload)
        elif task_type == 'simulate_backup':
            result = simulate_backup(task.payload)
        elif task_type == 'large_file_processing':
            result = large_file_processing(task.payload)
        else:
            result = {'error': 'Unknown task type'}

        # Simulate task processing time
        time.sleep(random.uniform(1, 3))

        # Update task status to 'completed'
        task.status = 'completed'
        task.result = json.dumps(result)
        db.session.commit()

        # Update Task Management Service via gRPC
        with grpc.insecure_channel('task_management_service:50051') as channel:
            stub = task_management_pb2_grpc.TaskManagementServiceStub(channel)
            stub.UpdateTaskStatus(task_management_pb2.UpdateTaskStatusRequest(
                task_id=task_id,
                status='completed',
                result=json.dumps(result)
            ))

        # Notify clients via WebSocket
        socketio.emit('task_update', {'id': task_id, 'status': 'completed', 'result': result}, namespace='/lobby',
                      broadcast=True)

def word_count(text):
    """Counts the number of words in the given text."""
    words = text.split()
    count = len(words)
    return {'word_count': count}

def sentiment_analysis(text):
    """Performs a dummy sentiment analysis."""
    sentiments = ['positive', 'neutral', 'negative']
    result = random.choice(sentiments)
    return {'sentiment': result}

def text_summarization(text):
    """Performs a dummy text summarization."""
    summary = ' '.join(text.split()[:5]) + '...'
    return {'summary': summary}

def image_resize(payload):
    """Performs a dummy image resize."""
    # Payload should contain image data; here we simulate
    return {'status': 'image resized'}

def apply_filter(payload):
    """Applies a dummy filter to an image."""
    # Payload should contain image data; here we simulate
    return {'status': 'filter applied'}

def calculate_statistics(data):
    """Calculates basic statistics (mean, median, standard deviation) from a list of numbers."""
    try:
        numbers = list(map(float, data.split(',')))
        mean = np.mean(numbers)
        median = np.median(numbers)
        std_dev = np.std(numbers)
        return {
            'mean': mean,
            'median': median,
            'std_dev': std_dev
        }
    except ValueError:
        return {'error': 'Invalid data. Please provide a list of numbers separated by commas.'}

def find_patterns(data):
    """Finds repeated words in the input text."""
    words = data.split()
    patterns = {word: words.count(word) for word in set(words) if words.count(word) > 1}
    return {'patterns': patterns}

def fetch_weather_data(location):
    """Fetches weather data from an external API for a given location."""
    try:
        api_url = f"https://api.weatherapi.com/v1/current.json?key=YOUR_API_KEY&q={location}"
        response = requests.get(api_url)
        if response.status_code == 200:
            weather_info = response.json()
            return {
                'location': weather_info['location']['name'],
                'temperature': weather_info['current']['temp_c'],
                'condition': weather_info['current']['condition']['text']
            }
        else:
            return {'error': 'Failed to fetch weather data'}
    except Exception as e:
        return {'error': str(e)}

def currency_conversion(data):
    """Converts an amount from one currency to another using an external API."""
    try:
        amount, from_currency, to_currency = data.split(',')
        amount = float(amount)
        # Replace this URL with a real currency conversion API
        api_url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(api_url)
        if response.status_code == 200:
            rates = response.json().get('rates', {})
            if to_currency in rates:
                converted_amount = amount * rates[to_currency]
                return {f"{amount} {from_currency}": f"{converted_amount} {to_currency}"}
            else:
                return {'error': f"Conversion rate for {to_currency} not found."}
        else:
            return {'error': 'Failed to fetch conversion rates'}
    except Exception as e:
        return {'error': str(e)}

def simulate_backup(data):
    """Simulates a backup operation, possibly backing up files."""
    # Simulate long-running task
    time.sleep(5)
    return {"result": "Backup completed successfully"}

def large_file_processing(data):
    """Simulates processing a large file."""
    # Simulate long-running task
    time.sleep(5)
    return {"result": "Large file processed successfully"}

# task_execution_service/app/tasks.py
import grpc
import task_management_pb2
import task_management_pb2_grpc
from extensions import db, socketio
from flask import current_app
import time
import json
from datetime import datetime

def fetch_task_and_process(task_id, socketio_instance):
    with current_app.app_context():
        task = Task.query.get(task_id)
        if not task:
            return

        task.status = 'in_progress'
        db.session.commit()

        socketio_instance.emit('task_update', {
            'id': task.id,
            'status': task.status,
            'result': task.result or ""
        }, namespace='/lobby', room='all_tasks')

        socketio_instance.emit('task_update', {
            'id': task.id,
            'status': task.status,
            'result': task.result or ""
        }, namespace='/lobby', room=f'task_{task.id}')

        result = execute_task(task.task_type, task.payload)

        time.sleep(1)

        task.status = 'completed'
        task.result = json.dumps(result)
        task.finished_at = datetime.utcnow()
        db.session.commit()

        with grpc.insecure_channel('task_management_service:50051') as channel:
            stub = task_management_pb2_grpc.TaskManagementServiceStub(channel)
            stub.UpdateTaskStatus(task_management_pb2.UpdateTaskStatusRequest(
                task_id=task.id,
                status='completed',
                result=task.result
            ))

        socketio_instance.emit('task_update', {
            'id': task.id,
            'status': task.status,
            'result': result
        }, namespace='/lobby', room='all_tasks')

        socketio_instance.emit('task_update', {
            'id': task.id,
            'status': task.status,
            'result': result
        }, namespace='/lobby', room=f'task_{task.id}')

def execute_task(task_type, payload):
    if task_type == 'word_count':
        return word_count(payload)
    elif task_type == 'sentiment_analysis':
        return sentiment_analysis(payload)
    elif task_type == 'text_summarization':
        return text_summarization(payload)
    elif task_type == 'image_resize':
        return image_resize(payload)
    elif task_type == 'apply_filter':
        return apply_filter(payload)
    elif task_type == 'calculate_statistics':
        return calculate_statistics(payload)
    elif task_type == 'find_patterns':
        return find_patterns(payload)
    elif task_type == 'weather_data':
        return fetch_weather_data(payload)
    elif task_type == 'currency_conversion':
        return currency_conversion(payload)
    elif task_type == 'simulate_backup':
        return simulate_backup(payload)
    elif task_type == 'large_file_processing':
        return large_file_processing(payload)
    else:
        return {'error': 'Unknown task type'}

def word_count(text):
    words = text.split()
    return {'word_count': len(words)}

def sentiment_analysis(text):
    import random
    sentiments = ['positive', 'neutral', 'negative']
    return {'sentiment': random.choice(sentiments)}

def text_summarization(text):
    summary = ' '.join(text.split()[:5]) + '...'
    return {'summary': summary}

def image_resize(payload):
    return {'status': 'image resized'}

def apply_filter(payload):
    return {'status': 'filter applied'}

def calculate_statistics(data):
    import numpy as np
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
        return {'error': 'Invalid data. Provide numbers separated by commas.'}

def find_patterns(data):
    words = data.split()
    patterns = {word: words.count(word) for word in set(words) if words.count(word) > 1}
    return {'patterns': patterns}

def fetch_weather_data(location):
    import requests
    try:
        api_url = f"https://api.weatherapi.com/v1/current.json?key=9fb7d20ea51a4782a01185122240210&q={location}"
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
    import requests
    try:
        amount, from_currency, to_currency = data.split(',')
        amount = float(amount)
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

def simulate_backup(payload):
    time.sleep(5)
    return {"result": "Backup completed successfully"}

def large_file_processing(payload):
    time.sleep(5)
    return {"result": "Large file processed successfully"}

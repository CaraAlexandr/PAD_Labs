# tasks.py
import logging
import json
import time
from flask import current_app
from models import db, Task
from flask_socketio import SocketIO
import random
import numpy as np

def process_task(task_id, socketio):
    time.sleep(10)
    with current_app.app_context():
        task = Task.query.get(task_id)
        if not task:
            logging.error(f"Task {task_id} not found")
            return
        try:
            task.status = 'in_progress'
            db.session.commit()

            # Emit the 'in_progress' update
            socketio.emit('task_update', {
                'id': task.id,
                'status': task.status,
                'result': task.result
            }, namespace='/lobby', room=str(task.id))

            # Simulate task execution time
            result = execute_task_logic(task)
            time.sleep(2)

            task.status = 'completed'
            task.result = json.dumps(result)
            db.session.commit()

            # Emit the 'completed' update
            socketio.emit('task_update', {
                'id': task.id,
                'status': task.status,
                'result': task.result
            }, namespace='/lobby', room=str(task.id))

        except Exception as e:
            task.status = 'failed'
            task.result = str(e)
            db.session.commit()

            # Emit the 'failed' update
            socketio.emit('task_update', {
                'id': task.id,
                'status': task.status,
                'result': task.result
            }, namespace='/lobby', room=str(task.id))

def execute_task_logic(task):
    if task.task_type == 'word_count':
        return word_count(task.payload)
    elif task.task_type == 'sentiment_analysis':
        return sentiment_analysis(task.payload)
    elif task.task_type == 'text_summarization':
        return text_summarization(task.payload)
    elif task.task_type == 'image_resize':
        return image_resize(task.payload)
    elif task.task_type == 'apply_filter':
        return apply_filter(task.payload)
    elif task.task_type == 'calculate_statistics':
        return calculate_statistics(task.payload)
    elif task.task_type == 'find_patterns':
        return find_patterns(task.payload)
    elif task.task_type == 'fetch_weather_data':
        return fetch_weather_data(task.payload)
    elif task.task_type == 'currency_conversion':
        return currency_conversion(task.payload)
    elif task.task_type == 'simulate_backup':
        return simulate_backup(task.payload)
    elif task.task_type == 'large_file_processing':
        return large_file_processing(task.payload)
    else:
        return {"error": "Unknown task type"}

def word_count(text):
    words = text.split()
    count = len(words)
    return {'word_count': count}

def sentiment_analysis(text):
    sentiments = ['positive', 'neutral', 'negative']
    result = random.choice(sentiments)
    return {'sentiment': result}

def text_summarization(text):
    summary = ' '.join(text.split()[:5]) + '...'
    return {'summary': summary}

def image_resize(payload):
    return {'status': 'image resized'}

def apply_filter(payload):
    return {'status': 'filter applied'}

def calculate_statistics(data):
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
    words = data.split()
    patterns = {word: words.count(word) for word in set(words) if words.count(word) > 1}
    return {'patterns': patterns}

def fetch_weather_data(location):
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

def simulate_backup(data):
    time.sleep(5)
    return {"result": "Backup completed successfully"}

def large_file_processing(data):
    time.sleep(5)
    return {"result": "Large file processed successfully"}

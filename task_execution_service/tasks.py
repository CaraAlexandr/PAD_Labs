#task_management_service\tasks.py
import json
import time

def execute_task(task_type, payload):
    payload = json.loads(payload)
    if task_type == 'word_count':
        text = payload.get('text', '')
        return len(text.split())
    elif task_type == 'sum_array':
        array = payload.get('array', [])
        return sum(array)
    elif task_type == 'multiply_array':
        array = payload.get('array', [])
        result = 1
        for num in array:
            result *= num
        return result
    elif task_type == 'reverse_string':
        text = payload.get('text', '')
        return text[::-1]
    elif task_type == 'sort_numbers':
        array = payload.get('array', [])
        return sorted(array)
    elif task_type == 'test':
        time.sleep(10)
        return 'Test task executed'
    else:
        return 'Unknown task type'

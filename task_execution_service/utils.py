# task_execution_service/utils.py

import os
import smtplib
from email.mime.text import MIMEText
import logging
import requests

def send_alert(message):
    try:
        smtp_server = os.getenv('ALERT_SMTP_SERVER', 'smtp.example.com')
        smtp_user = os.getenv('ALERT_SMTP_USER', 'user')
        smtp_password = os.getenv('ALERT_SMTP_PASSWORD', 'password')
        alert_from = os.getenv('ALERT_FROM', 'alert@example.com')
        alert_to = os.getenv('ALERT_TO', 'admin@example.com')

        msg = MIMEText(message)
        msg['Subject'] = 'Redis Queue Alert'
        msg['From'] = alert_from
        msg['To'] = alert_to

        with smtplib.SMTP(smtp_server) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
        logging.info("Alert email sent.")
    except Exception as e:
        logging.error(f"Failed to send alert email: {e}")

def deregister_with_service_discovery(service_name='task_execution_service'):
    service_discovery_url = os.getenv('SERVICE_DISCOVERY_URL', 'http://service_discovery:8003/services/deregister')
    try:
        response = requests.delete(f'{service_discovery_url}/{service_name}')
        if response.status_code in (200, 204):
            logging.info('Deregistered from Service Discovery.')
        else:
            logging.error(f'Failed to deregister from Service Discovery: {response.text}')
    except Exception as e:
        logging.error(f'Error deregistering with Service Discovery: {e}')

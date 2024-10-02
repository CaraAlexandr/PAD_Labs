# task_execution_service/app/models.py
from .extensions import db
from datetime import datetime

class Worker(db.Model):
    __tablename__ = 'workers'

    id = db.Column(db.String, primary_key=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    task_type = db.Column(db.String(50), nullable=False)
    payload = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='pending')
    result = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)

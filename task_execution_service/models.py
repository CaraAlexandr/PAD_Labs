# models.py
from extensions import db
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    task_type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    payload = db.Column(db.Text)
    result = db.Column(db.Text)
    # start_time = db.Column(db.DateTime)
    # end_time = db.Column(db.DateTime)

class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    status = db.Column(db.String(20))
    current_task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
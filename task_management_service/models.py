# task_management_service/models.py

from extensions import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))
    task_type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    payload = db.Column(db.Text)
    result = db.Column(db.Text)  # Added result field

    def __repr__(self):
        return f"<Task {self.id}>"

from extensions import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    task_type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    payload = db.Column(db.Text)
# task_execution_service/app/app.py
from flask import Flask
from extensions import db, socketio
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db_task_execution:5432/task_execution_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    socketio.init_app(app, message_queue='redis://redis_pad:6379/0', cors_allowed_origins="*")
    return app

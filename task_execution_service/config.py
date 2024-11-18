import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:password@db_task_execution:5432/task_execution_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

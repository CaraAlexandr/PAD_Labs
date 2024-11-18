import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:password@db_task_management:5432/task_management_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

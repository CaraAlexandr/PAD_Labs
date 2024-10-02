from flask import Flask
from flask_migrate import Migrate
import grpc
from concurrent import futures
import task_management_pb2_grpc
from services import TaskManagementServicer
import threading
from extensions import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db_task_management:5432/task_management_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Recommended to disable

db.init_app(app)  # Initialize db with the app
migrate = Migrate(app, db)

from routes import task_bp, status_bp

app.register_blueprint(task_bp)
app.register_blueprint(status_bp)

# gRPC server
def serve_grpc(app):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    task_management_pb2_grpc.add_TaskManagementServiceServicer_to_server(TaskManagementServicer(app), server)
    server.add_insecure_port('[::]:50051')  # gRPC server on port 50051
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
        threading.Thread(target=serve_grpc, args=(app,)).start()  # Start gRPC server in a thread
        app.run(host='0.0.0.0', port=5000)  # Start Flask HTTP server on port 5000
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate gRPC code with the same runtime version
RUN python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/task_execution.proto
RUN python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/task_management.proto

CMD ["python", "app.py"]

# task_management_service/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Install grpcio-tools to compile .proto files
RUN pip install grpcio-tools

# Compile the .proto files
RUN python -m grpc_tools.protoc -I./app/grpc --python_out=./app/grpc --grpc_python_out=./app/grpc ./app/grpc/task_management.proto

# Verify that .proto files are compiled
RUN ls -la app/grpc/

# Run the service as a module to support absolute imports
CMD ["python", "-m", "app.main"]

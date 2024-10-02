FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY .. .

# Generate gRPC code
RUN python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/task_management.proto

CMD ["python", "app.py"]

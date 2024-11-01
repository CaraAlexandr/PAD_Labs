# Base image
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .



# Generate gRPC code
RUN python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/task_management.proto

CMD ["python", "app.py"]

## Ensure the gRPC code is accessible by setting PYTHONPATH
#ENV PYTHONPATH="/app:${PYTHONPATH}"
#
## Install testing dependencies (like pytest)
#RUN pip install pytest
#
## Run tests before starting the service
#COPY entrypoint.sh /app/entrypoint.sh
#RUN chmod +x /app/entrypoint.sh
#
## Expose Flask and gRPC ports
#EXPOSE 5000
#EXPOSE 50051
#
## Set the entrypoint to run tests and then start the service
#ENTRYPOINT ["/app/entrypoint.sh"]

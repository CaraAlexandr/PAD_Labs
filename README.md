# Distributed Task Queue System

## PlantUML Architecture Diagram

![ZLPDZzis4BthLmmG86s16Ccb5n-Ax7gDJH1luDWEYgBjOIoD9S8KgPBKRfnVdnbAilMnRlPcaU-z6Suy3ltU1tIXBdKILD04Tye7f_Pre0nsw8_mfQQQO7loWKguSMcX0gMXTfGa_gXCXGvBI6rPMKCcRCE9HHmZqEIQUX1ZC_9KmU_lUeiEpR5TJ7w1EpeeGnSn3qyg581QeISFQ3BU](https://github.com/user-attachments/assets/d1a5aa56-085d-4b58-9344-3a39c53fa5fd)


### Diagram Explanation

- **Clients**: Users or applications that interact with the system by submitting tasks and retrieving results.

- **Load Balancer (Nginx)**: Distributes incoming client requests among multiple API Gateway instances.

- **API Gateway**: Serves as the entry point, handling client requests, implementing the Circuit Breaker, and routing requests to appropriate services using Service Discovery.

- **Service Discovery**: Manages dynamic registration and discovery of services, enabling the API Gateway to find available instances of services.

- **Task Management Service Cluster**: Consists of multiple instances (TMS1, TMS2, TMS3) for high availability and load balancing. They handle task creation, status updates, and result retrieval.

- **Task Execution Service Cluster**: Contains multiple instances (TES1, TES2, TES3) that process tasks from the Redis Cluster and update task statuses.

- **Redis Cluster**: Comprises multiple nodes (Redis1, Redis2, Redis3) configured with consistent hashing and sharding for distributed caching and task queueing.

- **Databases**:
  - **Task Management Database**: Stores task metadata, with replication for high availability.
  - **Task Execution Database**: Stores execution logs and results, with replication.

- **Logging & Monitoring**: Centralized logging and monitoring using ELK Stack, Prometheus, and Grafana.

- **Data Warehouse**: Data from the databases is periodically extracted, transformed, and loaded into Amazon Redshift for analytical purposes.

---

### Distributed Task Queue System

This document provides an overview of the Distributed Task Queue System, including its architecture, components, endpoints, and instructions on how to run and deploy the application.

### Table of Contents

- [Introduction](#introduction)
- [System Architecture](#system-architecture)
- [Components](#components)
- [Endpoints Documentation](#endpoints-documentation)
- [Running and Deployment Instructions](#running-and-deployment-instructions)
- [Additional Information](#additional-information)

---

### Introduction

The Distributed Task Queue System is designed using a microservices architecture to facilitate the submission, execution, and monitoring of various tasks. The system is scalable, fault-tolerant, and includes features such as high availability, distributed transactions, consistent hashing for caching, and data analytics.

### System Architecture

The system comprises several microservices and components:

- **API Gateway**: Entry point for clients, handling requests, authentication, routing, and implementing a Circuit Breaker.
- **Load Balancer (Nginx)**: Distributes incoming requests among API Gateway instances.
- **Service Discovery**: Manages dynamic service registration and discovery.
- **Task Management Service Cluster**: Handles task creation, status updates, and result retrieval.
- **Task Execution Service Cluster**: Processes tasks from a queue and updates their status.
- **Redis Cluster**: Acts as a distributed task queue and caching layer.
- **Databases**: PostgreSQL clusters for both Task Management and Task Execution services, with replication.
- **Logging and Monitoring**: Aggregates logs and metrics using ELK Stack and Prometheus with Grafana.
- **Data Warehouse**: Periodically updated with data from databases for analytics.
- **Circuit Breaker**: Implemented within the API Gateway to prevent cascading failures.

### Components

#### 1. API Gateway

- **Technology**: NestJS (Node.js)
- **Responsibilities**:
  - Serves as the entry point for client requests.
  - Implements authentication and authorization.
  - Routes requests to appropriate services using Service Discovery.
  - Incorporates a Circuit Breaker to prevent cascading failures.

#### 2. Load Balancer (Nginx)

- **Responsibilities**:
  - Distributes incoming client requests among multiple API Gateway instances.
  - Ensures high availability and load balancing.

#### 3. Service Discovery

- **Technology**: Custom Implementation (e.g., etcd, Consul)
- **Responsibilities**:
  - Maintains a registry of service instances.
  - Provides dynamic service discovery for the API Gateway and other services.

#### 4. Task Management Service

- **Technology**: Python Flask
- **Responsibilities**:
  - Handles task creation, status updates, and result retrieval.
  - Stores task data in the PostgreSQL cluster.
  - Enqueues tasks into the Redis Cluster for processing.

#### 5. Task Execution Service

- **Technology**: Python gRPC
- **Responsibilities**:
  - Dequeues tasks from the Redis Cluster.
  - Executes tasks based on their type.
  - Updates task status and results in the Task Management Service.

#### 6. Redis Cluster

- **Technology**: Redis with Consistent Hashing
- **Responsibilities**:
  - Acts as a distributed task queue and caching layer.
  - Implements consistent hashing for even load distribution and high availability.

#### 7. Databases

- **Technology**: PostgreSQL with Replication
- **Components**:
  - **Task Management Database**: Stores task metadata.
  - **Task Execution Database**: Stores execution logs and results.

#### 8. Logging & Monitoring

- **Technology**: ELK Stack, Prometheus, Grafana
- **Responsibilities**:
  - Aggregates logs from all services.
  - Monitors metrics and system performance.
  - Provides dashboards and alerting mechanisms.

#### 9. Data Warehouse

- **Technology**: Amazon Redshift, Apache NiFi
- **Responsibilities**:
  - Aggregates data from databases for analytics.
  - Updated via periodic ETL processes.

---
### Enhancements Overview

The system incorporates several enhancements to meet specific requirements, referred to as Marks 1-9. Below are the detailed implementations of each mark:

#### Mark 1: Circuit Breaker

- **Description**: Implement a Circuit Breaker to prevent cascading failures by stopping requests to a failing service after multiple failed attempts.
- **Implementation**:
  - Integrated using the `resilience4j` library within the API Gateway.
  - Monitors the number of failed requests to downstream services.
  - Trips the circuit after a predefined threshold of failures, redirecting traffic away from the failing service.
- **Functionality**:
  - Enhances system resilience by isolating failing services.
  - Provides fallback responses to clients during service downtimes.

#### Mark 2: Service High Availability

- **Description**: Ensure high availability of services by deploying multiple replicas and implementing load balancing.
- **Implementation**:
  - Deployed multiple replicas of each microservice using Docker Compose's `deploy` and `replicas` options.
  - Utilized Nginx as a Load Balancer to distribute incoming requests among service instances.
  - Implemented health checks to monitor service instance health and automatically remove unhealthy instances from the load balancer.
- **Features**:
  - **Load Balancing**: Nginx balances the load, preventing any single instance from becoming a bottleneck.
  - **Fault Tolerance**: Automatically handles the failure of service instances without impacting overall system availability.

#### Mark 3: Logging and Monitoring

- **Description**: Implement centralized logging and monitoring to aggregate data from all services.
- **Implementation**:
  - **Logging**: Deployed the ELK Stack (Elasticsearch, Logstash, Kibana) to collect and aggregate logs from all services.
  - **Monitoring**: Utilized Prometheus to collect metrics and Grafana to visualize them through dashboards.
- **Functionality**:
  - **Centralized Logging**: Aggregates logs for easier debugging and analysis.
  - **Real-Time Monitoring**: Tracks system performance and resource utilization, enabling proactive issue detection.
  - **Alerting**: Configured alerts for anomalous metrics to notify the team of potential issues.

#### Mark 4: Distributed Transactions with Two-Phase Commit

- **Description**: Implement microservice-based Two-Phase Commit (2PC) transactions to ensure atomicity across multiple databases.
- **Implementation**:
  - Created a new endpoint (`POST /tasks/commit`) that initiates a distributed transaction involving both the Task Management and Task Execution databases.
  - Utilized a coordinator service within the Task Management Service to manage the 2PC protocol.
  - Ensured that both databases either commit or rollback changes to maintain consistency.
- **Functionality**:
  - Guarantees that operations affecting multiple services are completed successfully and consistently.
  - Prevents partial updates that could lead to data inconsistency.

#### Mark 5: Consistent Hashing for Cache

- **Description**: Implement consistent hashing in the Redis Cluster to evenly distribute cache keys and minimize cache misses.
- **Implementation**:
  - Configured Redis Cluster nodes with consistent hashing algorithms.
  - Ensured that when nodes are added or removed, only a minimal number of keys are redistributed.
- **Benefits**:
  - Enhances performance by ensuring an even distribution of cache load.
  - Reduces the impact of node changes on cache availability and consistency.

#### Mark 6: Cache High Availability

- **Description**: Ensure high availability of the cache layer by configuring Redis Cluster with replication and failover mechanisms.
- **Implementation**:
  - Configured Redis Cluster with multiple replicas for each primary node.
  - Enabled automatic failover using Redis Sentinel to monitor and promote replicas in case of primary node failures.
- **Features**:
  - **Replication**: Maintains multiple copies of cache data to prevent data loss.
  - **Automatic Failover**: Quickly recovers from node failures without manual intervention, maintaining cache availability.

#### Mark 7: Long-Running Saga Transactions

- **Description**: Implement long-running saga transactions with a coordinator to handle distributed operations without relying on Two-Phase Commit.
- **Implementation**:
  - Developed a Saga Coordinator service that manages the sequence of transactions across microservices.
  - Defined compensating actions to rollback changes in case of failures during the saga.
  - Created endpoints that initiate saga transactions for complex operations.
- **Functionality**:
  - Manages distributed transactions without the complexity and locking issues of 2PC.
  - Enhances system scalability and reliability by handling failures gracefully through compensating actions.

#### Mark 8: Database Redundancy and Replication

- **Description**: Implement database redundancy and replication to ensure data availability and reliability.
- **Implementation**:
  - Configured PostgreSQL clusters with at least three replicas for both Task Management and Task Execution databases.
  - Utilized streaming replication to maintain real-time data consistency across replicas.
  - Implemented automated failover using tools like Patroni to promote replicas in case of primary node failures.
- **Features**:
  - **Data Redundancy**: Multiple replicas prevent data loss and ensure high availability.
  - **Failover**: Automated mechanisms quickly switch to replicas during failures, minimizing downtime.

#### Mark 9: Data Warehouse Integration

- **Description**: Create a Data Warehouse that aggregates data from all databases for analytical purposes.
- **Implementation**:
  - Established a Data Warehouse using Amazon Redshift.
  - Developed ETL (Extract, Transform, Load) processes using Apache NiFi to periodically extract data from PostgreSQL databases, transform it as needed, and load it into the Data Warehouse.
  - Scheduled ETL jobs to run at regular intervals to keep the Data Warehouse updated.
- **Functionality**:
  - Consolidates data from multiple sources for comprehensive analytics and reporting.
  - Enables complex queries and data analysis without impacting operational databases.

---

### Endpoints Documentation

#### API Gateway Endpoints

1. **Create Task**

   - **Endpoint**: `POST /tasks`
   - **Description**: Creates a new task.
   - **Request Body**:

     ```json
     {
       "description": "Count words",
       "task_type": "word_count",
       "payload": "word1 word2 word3"
     }
     ```

   - **Response**:

     ```json
     {
       "id": 1,
       "status": "pending",
       "task_type": "word_count"
     }
     ```

2. **Get Task by ID**

   - **Endpoint**: `GET /tasks/{id}`
   - **Description**: Retrieves task details by ID.
   - **Response**:

     ```json
     {
       "id": 1,
       "description": "Count words",
       "task_type": "word_count",
       "status": "completed",
       "payload": "word1 word2 word3",
       "result": "{\"word_count\": 3}",
       "start_time": "2021-10-01T12:00:00Z",
       "end_time": "2021-10-01T12:00:05Z"
     }
     ```

3. **List Tasks**

   - **Endpoint**: `GET /tasks`
   - **Description**: Retrieves a list of tasks with pagination support.
   - **Query Parameters**:
     - `page_number` (optional, default: 1)
     - `page_size` (optional, default: 10)
   - **Response**:

     ```json
     [
       {
         "id": 1,
         "description": "Count words",
         "task_type": "word_count",
         "status": "completed",
         "payload": "word1 word2 word3",
         "result": "{\"word_count\": 3}",
         "start_time": "2021-10-01T12:00:00Z",
         "end_time": "2021-10-01T12:00:05Z"
       },
       // More tasks...
     ]
     ```

4. **Delete Task**

   - **Endpoint**: `DELETE /tasks/{id}`
   - **Description**: Deletes a task by ID.
   - **Response**:

     ```json
     {
       "message": "Task deleted"
     }
     ```

5. **Start Task Execution**

   - **Endpoint**: `POST /tasks/{id}/execute`
   - **Description**: Starts the execution of a task.
   - **Response**:

     ```json
     {
       "taskId": 1,
       "status": "completed",
       "result": "{\"word_count\": 3}"
     }
     ```

---

### Running and Deployment Instructions

#### Prerequisites

- **Docker**: Ensure Docker is installed on your system.
- **Docker Compose**: Required to orchestrate the multi-container application.

#### Starting the Application

1. **Clone the Repository**

   ```bash
   git clone https://github.com/CaraAlexandr/PAD_Labs
   cd PAD_Labs
   ```

2. **Build and Start Services**

   Run the following command to build and start all services in detached mode:

   ```bash
   docker-compose up --build -d
   ```

   This command will:

   - Build Docker images for all services defined in `docker-compose.yml`.
   - Start the containers in the background (`-d` flag).
   - Download any necessary images and dependencies.

3. **Verify Services are Running**

   You can check the status of the containers using:

   ```bash
   docker-compose ps
   ```

   Ensure that all services are listed and have a status of `Up`.

4. **Access the API Gateway**

   The API Gateway should be accessible at `http://localhost:8002`.

   You can test the status endpoint:

   ```bash
   curl http://localhost:8002/status
   ```

   Expected response:

   ```json
   {
     "status": "Gateway is running"
   }
   ```

#### Stopping the Application

To stop all running containers, use:

```bash
docker-compose down
```

---

### Additional Information

- **Logging and Monitoring**: Access dashboards for ELK Stack and Grafana if they are exposed on specific ports (configure as needed in `docker-compose.yml`).
- **Scaling Services**: You can scale services by adjusting the `deploy: replicas` option in `docker-compose.yml` for each service.
- **Configuration Files**: Customize configurations in the respective service directories, such as environment variables, database settings, and more.
- **Data Persistence**: Ensure volumes are configured in `docker-compose.yml` to persist data for databases and other stateful services.

---

**Note**: This README provides a high-level overview and basic instructions to get started with the Distributed Task Queue System. For detailed information, please refer to the documentation in each service's directory or contact the project maintainers.

#!/bin/sh

echo "Waiting for Redis nodes to start..."
sleep 10

echo "Creating Redis cluster..."
yes | redis-cli --cluster create \
  redis-node-1:7001 \
  redis-node-2:7002 \
  redis-node-3:7003 \
  redis-node-4:7004 \
  redis-node-5:7005 \
  redis-node-6:7006 \
  --cluster-replicas 1 \ --cluster-yes || echo "Failed to create Redis cluster. It might already be created."

echo "Redis cluster setup completed."

#!/bin/sh

echo "Waiting for Redis nodes to start..."
sleep 10

echo "Creating Redis cluster..."
yes | redis-cli --cluster create \
  172.32.1.1:7001 \
  172.32.1.2:7002 \
  172.32.1.3:7003 \
  172.32.1.4:7004 \
  172.32.1.5:7005 \
  172.32.1.6:7006 \
  --cluster-replicas 1

echo "Redis cluster created."

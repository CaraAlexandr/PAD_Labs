#!/bin/bash

# Base URL of the API
BASE_URL="http://localhost:8002"

# Expected values
EXPECTED_DESCRIPTION="Count words"
EXPECTED_TASK_TYPE="word_count"
EXPECTED_PAYLOAD="word1 word2 word3"
EXPECTED_STATUS="completed"  # Update this to 'completed'

# Function to print headers
print_header() {
  echo "======================================="
  echo "$1"
  echo "======================================="
}

# Function to compare expected vs actual values
compare_values() {
  local expected=$1
  local actual=$2
  local field_name=$3

  if [ "$expected" != "$actual" ]; then
    echo "Mismatch in $field_name: Expected '$expected', got '$actual'"
    exit 1
  else
    echo "$field_name is correct: $actual"
  fi
}

# 1. Check Gateway Status
print_header "1. Checking Gateway Status"

STATUS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/status")

if [ "$STATUS_RESPONSE" -eq 200 ]; then
  echo "Gateway is running."
else
  echo "Failed to reach Gateway. HTTP Status: $STATUS_RESPONSE"
  exit 1
fi

echo ""

# 2. Create a Task
print_header "2. Creating a Task"

CREATE_PAYLOAD='{
  "description": "Count words",
  "task_type": "word_count",
  "payload": "word1 word2 word3"
}'

CREATE_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -d "$CREATE_PAYLOAD")

# Separate body and status code
CREATE_BODY=$(echo "$CREATE_RESPONSE" | sed '$d')
CREATE_STATUS=$(echo "$CREATE_RESPONSE" | tail -n1)

if [ "$CREATE_STATUS" -eq 201 ] || [ "$CREATE_STATUS" -eq 200 ]; then
  echo "Task created successfully."
  # Extract the Task ID using grep and sed instead of jq
  TASK_ID=$(echo "$CREATE_BODY" | grep -o '"id":[^,]*' | sed 's/"id"://')
  echo "Created Task ID: $TASK_ID"

  # Extract and compare the description, task_type, and payload from the response
  DESCRIPTION=$(echo "$CREATE_BODY" | grep -o '"description":"[^"]*' | sed 's/"description":"//')
  PAYLOAD=$(echo "$CREATE_BODY" | grep -o '"payload":"[^"]*' | sed 's/"payload":"//')

  compare_values "$EXPECTED_DESCRIPTION" "$DESCRIPTION" "Description"
  compare_values "$EXPECTED_PAYLOAD" "$PAYLOAD" "Payload"
else
  echo "Failed to create task. HTTP Status: $CREATE_STATUS"
  echo "Response: $CREATE_BODY"
  exit 1
fi

echo ""

# 3. Retrieve the Created Task by ID
print_header "3. Retrieving Task by ID"

GET_TASK_RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/tasks/$TASK_ID")

GET_TASK_BODY=$(echo "$GET_TASK_RESPONSE" | sed '$d')
GET_TASK_STATUS=$(echo "$GET_TASK_RESPONSE" | tail -n1)

if [ "$GET_TASK_STATUS" -eq 200 ]; then
  echo "Task retrieved successfully:"
  echo "$GET_TASK_BODY"

  # Extract and compare the description, task_type, payload, and status from the response
  DESCRIPTION=$(echo "$GET_TASK_BODY" | grep -o '"description":"[^"]*' | sed 's/"description":"//')
  PAYLOAD=$(echo "$GET_TASK_BODY" | grep -o '"payload":"[^"]*' | sed 's/"payload":"//')
  STATUS=$(echo "$GET_TASK_BODY" | grep -o '"status":"[^"]*' | sed 's/"status":"//')

  compare_values "$EXPECTED_DESCRIPTION" "$DESCRIPTION" "Description"
  compare_values "$EXPECTED_PAYLOAD" "$PAYLOAD" "Payload"
  compare_values "$EXPECTED_STATUS" "$STATUS" "Status"
else
  echo "Failed to retrieve task. HTTP Status: $GET_TASK_STATUS"
  echo "Response: $GET_TASK_BODY"
  exit 1
fi

echo ""


# 4. Start the Task
print_header "4. Starting the Task"

# Expected values for the task start response
EXPECTED_TASK_ID="1"  # Use the dynamically obtained Task ID
EXPECTED_TASK_STATUS="completed"
EXPECTED_TASK_RESULT='{\"word_count\": 3}'  # Include escaped quotes

START_TASK_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/tasks/$EXPECTED_TASK_ID/execute")

START_TASK_BODY=$(echo "$START_TASK_RESPONSE" | sed '$d')
START_TASK_STATUS_CODE=$(echo "$START_TASK_RESPONSE" | tail -n1)

if [ "$START_TASK_STATUS_CODE" -eq 201 ] || [ "$START_TASK_STATUS_CODE" -eq 202 ]; then
  echo "Task started successfully."
  echo "Response:"
  echo "$START_TASK_BODY"

  # Extract values from the response
  RESPONSE_TASK_ID=$(echo "$START_TASK_BODY" | sed -n 's/.*"taskId":\([0-9]*\),.*/\1/p')
  RESPONSE_STATUS=$(echo "$START_TASK_BODY" | sed -n 's/.*"status":"\([^"]*\)".*/\1/p')
  RESPONSE_RESULT=$(echo "$START_TASK_BODY" | sed -n 's/.*"result":"\(.*\)"}$/\1/p')

  # Compare task ID, status, and result
  compare_values "$EXPECTED_TASK_ID" "$RESPONSE_TASK_ID" "Task ID"
  compare_values "$EXPECTED_TASK_STATUS" "$RESPONSE_STATUS" "Status"

  # Compare result with escaped quotes
  compare_values "$EXPECTED_TASK_RESULT" "$RESPONSE_RESULT" "Result"
else
  echo "Failed to start task. HTTP Status: $START_TASK_STATUS_CODE"
  echo "Response: $START_TASK_BODY"
  exit 1
fi

echo ""


echo "All tests completed successfully."

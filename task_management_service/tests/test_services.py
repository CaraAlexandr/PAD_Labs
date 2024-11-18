import unittest
from unittest.mock import MagicMock, patch

import task_management_pb2
from app import app
from models import Task
from services import TaskManagementServicer


class TestTaskManagementServicer(unittest.TestCase):
    def setUp(self):
        # Set up Flask app context
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db_task_management:5432/task_management_db'

    @patch('services.db.session.add')
    @patch('services.db.session.commit')
    @patch('services.redis.Redis')  # Mock Redis interactions
    @patch('models.Task', spec=True)  # Mock the Task model class
    def test_create_task(self, mock_task_class, mock_redis, mock_commit, mock_add):
        with self.app.app_context():
            # Set up mock Redis instance
            mock_redis_instance = mock_redis.return_value

            # Set up mock Task object
            mock_task_instance = MagicMock(spec=Task)
            mock_task_instance.id = None  # Initially, the ID is not set
            mock_task_class.return_value = mock_task_instance  # Return the mock Task instance when Task() is called

            # Mock gRPC request
            request = task_management_pb2.TaskRequest(
                description="Test task",
                task_type="typeA",
                payload="{}"
            )

            # Initialize the servicer and call the method
            servicer = TaskManagementServicer(self.app)

            # Simulate adding the task and committing (ID is assigned after commit)
            mock_add.return_value = None
            mock_commit.side_effect = lambda: setattr(mock_task_instance, 'id', 1)  # Simulate ID assignment

            # Call the CreateTask method
            response = servicer.CreateTask(request, None)

            # Assertions to ensure task creation worked as expected
            self.assertIsNotNone(response.id)  # ID should be auto-generated, ensure it's not None
            self.assertEqual(response.description, "Test task")
            self.assertEqual(response.task_type, "typeA")
            self.assertEqual(response.status, "pending")

            # Ensure the task was added to the database
            mock_add.assert_called_once_with(mock_task_instance)
            mock_commit.assert_called_once()

            # Ensure Redis lpush was called with a valid ID
            mock_redis_instance.lpush.assert_called_with('task_queue', 1)


if __name__ == '__main__':
    unittest.main()

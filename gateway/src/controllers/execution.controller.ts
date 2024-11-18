import { Controller, Post, Param, Body, HttpException, HttpStatus } from '@nestjs/common';
import axios from 'axios';

@Controller('execute_task')
export class ExecutionController {
  private readonly executionServiceUrl = process.env.TASK_EXECUTION_URL || 'http://task_execution_service:5001';

  @Post(':id')
  async executeTask(@Param('id') taskId: number) {
    if (!taskId) {
      throw new HttpException('task_id is required', HttpStatus.BAD_REQUEST);
    }

    try {
      // Forward the request to the Task Execution Service's /process endpoint
      const response = await axios.post(`${this.executionServiceUrl}/process`, { task_id: taskId });

      return response.data;
    } catch (error) {
      // Handle errors from the Execution Service
      if (error.response) {
        throw new HttpException(
          error.response.data,
          error.response.status
        );
      } else {
        throw new HttpException(
          'Failed to communicate with Task Execution Service',
          HttpStatus.INTERNAL_SERVER_ERROR
        );
      }
    }
  }
}

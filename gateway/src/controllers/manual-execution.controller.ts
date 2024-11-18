import { Controller, Post, Param, HttpException, HttpStatus } from '@nestjs/common';
import axios from 'axios';
import { Logger } from '@nestjs/common';

@Controller('execute_task')
export class ManualExecutionController {
  private readonly logger = new Logger(ManualExecutionController.name);
  private taskExecutionServiceUrl = process.env.TASK_EXECUTION_URL || 'http://task_execution_service:5001/execute';

  @Post(':task_id')
  async executeTask(@Param('task_id') taskId: number) {
    try {
      const response = await axios.post(`${this.taskExecutionServiceUrl}/${taskId}`);
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to execute task ${taskId}: ${error.message}`);
      throw new HttpException(
        {
          status: HttpStatus.INTERNAL_SERVER_ERROR,
          error: `Failed to execute task ${taskId}`,
        },
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}

import { Controller, Post, Param, HttpException, HttpStatus, Logger } from '@nestjs/common';
import axios from 'axios';
import CircuitBreaker = require('opossum');

@Controller('execute_task')
export class ExecutionController {
  private readonly executionServiceUrls: string[];
  private readonly logger = new Logger(ExecutionController.name);
  private readonly maxRetries = parseInt(process.env.MAX_RETRIES, 10) || 3;
  private readonly maxReroutes = parseInt(process.env.MAX_REROUTES, 10) || 2;
  private circuitBreakerOptions = {
    timeout: 60000,
    errorThresholdPercentage: 50,
    resetTimeout: 10000,
    rollingCountBuckets: 10,
    rollingCountTimeout: 10000,
  };
  private breaker;

  constructor() {
    this.executionServiceUrls = process.env.TASK_EXECUTION_URLS
      ? process.env.TASK_EXECUTION_URLS.split(',')
      : ['http://task_execution_service:5001'];

    this.breaker = new CircuitBreaker(
      async (taskId: number) => {
        return this.executeWithReroutesAndRetries(taskId);
      },
      this.circuitBreakerOptions,
    );

    this.breaker.fallback(() => {
      throw new HttpException(
        'Task Execution Service is currently unavailable',
        HttpStatus.SERVICE_UNAVAILABLE,
      );
    });

    this.breaker.on('open', () => {
      this.logger.warn('Circuit breaker is now OPEN. All requests will fail fast.');
    });

    this.breaker.on('halfOpen', () => {
      this.logger.log('Circuit breaker is HALF-OPEN. Testing the service.');
    });

    this.breaker.on('close', () => {
      this.logger.log('Circuit breaker is now CLOSED. Service has resumed.');
    });

    this.breaker.on('failure', (error) => {
      this.logger.error(`Circuit breaker detected a failure: ${error.message}`);
    });

    this.breaker.on('success', () => {
      this.logger.log('Request succeeded. Circuit breaker remains closed.');
    });
  }

  @Post(':id')
  async executeTask(@Param('id') taskId: number) {
    if (!taskId) {
      throw new HttpException('task_id is required', HttpStatus.BAD_REQUEST);
    }

    try {
      const result = await this.breaker.fire(taskId);
      return result;
    } catch (error) {
      if (error instanceof HttpException) {
        throw error;
      } else if (error.message === 'Breaker is open') {
        throw new HttpException(
          'Circuit breaker engaged: Task Execution Service is temporarily unavailable',
          HttpStatus.SERVICE_UNAVAILABLE,
        );
      } else {
        throw new HttpException(
          'Failed to execute task',
          HttpStatus.INTERNAL_SERVER_ERROR,
        );
      }
    }
  }

  private async executeWithReroutesAndRetries(taskId: number): Promise<any> {
    let lastError;
    let rerouteCount = 0;

    for (const serviceUrl of this.executionServiceUrls) {
      if (rerouteCount >= this.maxReroutes) {
        break;
      }

      try {
        const result = await this.executeWithRetries(taskId, serviceUrl, this.maxRetries);
        return result;
      } catch (error) {
        lastError = error;
        rerouteCount++;
        this.logger.warn(
          `Service at ${serviceUrl} failed. Rerouting to next service (${rerouteCount}/${this.maxReroutes})...`,
        );
      }
    }

    this.logger.error(
      `All reroutes (${this.maxReroutes}) have failed. Circuit breaker will engage if failure rate is high.`,
    );
    throw lastError;
  }

  private async executeWithRetries(
    taskId: number,
    serviceUrl: string,
    retries: number,
  ): Promise<any> {
    try {
      const response = await axios.post(`${serviceUrl}/process`, { task_id: taskId });
      return response.data;
    } catch (error) {
      if (retries > 1) {
        const attempt = this.maxRetries - retries + 1;
        this.logger.warn(
          `Request to ${serviceUrl} failed. Retrying attempt ${attempt}/${this.maxRetries}...`,
        );
        return this.executeWithRetries(taskId, serviceUrl, retries - 1);
      } else {
        this.logger.error(
          `All retries (${this.maxRetries}) for ${serviceUrl} have failed.`,
        );
        throw error;
      }
    }
  }
}

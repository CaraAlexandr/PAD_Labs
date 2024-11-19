import { Controller, Post, Param, HttpException, HttpStatus } from '@nestjs/common';
import axios from 'axios';
import CircuitBreaker = require('opossum');

@Controller('execute_task')
export class ExecutionController {
  private readonly executionServiceUrl =
    process.env.TASK_EXECUTION_URL || 'http://task_execution_service:5001';

  private readonly breaker;

  constructor() {
    const options = {
      timeout: 15000, // Adjusted timeout to accommodate retries
      errorThresholdPercentage: 50, // When 50% of requests fail, trip the circuit
      resetTimeout: 30000, // After 30 seconds, try again
    };

    // Function to be wrapped by the circuit breaker, including retries
    const axiosPostWithRetries = async (taskId) => {
      const maxRetries = parseInt(process.env.MAX_RETRIES) || 3; // Default to 3 retries
      let attempt = 0;
      let lastError;

      while (attempt < maxRetries) {
        try {
          const response = await axios.post(`${this.executionServiceUrl}/process`, { task_id: taskId });
          return response;
        } catch (error) {
          lastError = error;
          attempt++;
          if (attempt < maxRetries) {
            console.log(`Retrying request (${attempt}/${maxRetries})...`);
            await this.delay(1000 * attempt); // Exponential backoff delay
          }
        }
      }

      // After all retries have failed, throw the last encountered error
      throw lastError;
    };

    // Create the circuit breaker instance
    this.breaker = new CircuitBreaker(axiosPostWithRetries, options);

    // Fallback function when the circuit is open
    this.breaker.fallback(() => {
      throw new HttpException(
        'Circuit breaker is open. Please try again later.',
        HttpStatus.SERVICE_UNAVAILABLE,
      );
    });

    // Log circuit breaker events
    this.breaker.on('open', () => {
      console.log('Circuit breaker opened');
    });
    this.breaker.on('halfOpen', () => {
      console.log('Circuit breaker half-open');
    });
    this.breaker.on('close', () => {
      console.log('Circuit breaker closed');
    });
  }

  @Post(':id')
  async executeTask(@Param('id') taskId: number) {
    if (!taskId) {
      throw new HttpException('task_id is required', HttpStatus.BAD_REQUEST);
    }

    try {
      // Use the circuit breaker to call the axios function with retries
      const response = await this.breaker.fire(taskId);
      return response.data;
    } catch (error) {
      if (error instanceof HttpException) {
        // Error thrown by the circuit breaker or fallback
        throw error;
      } else if (error.response) {
        throw new HttpException(error.response.data, error.response.status);
      } else {
        throw new HttpException(
          'Failed to communicate with Task Execution Service after multiple retries',
          HttpStatus.INTERNAL_SERVER_ERROR,
        );
      }
    }
  }

  // Helper function for delay
  private delay(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

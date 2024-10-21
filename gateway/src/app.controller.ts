// gateway/src/app.controller.ts

import {
  Controller,
  Post,
  Body,
  Get,
  Param,
  OnModuleInit,
  Inject,
  ParseIntPipe,
  Logger,
} from '@nestjs/common';
import { ClientGrpc } from '@nestjs/microservices';
import { Observable, lastValueFrom } from 'rxjs';

interface TaskManagementService {
  createTask(data: { description: string; task_type: string; payload: string }): Observable<any>;
  getTaskById(data: { id: number }): Observable<any>;
  listTasks(data: { page_number: number; page_size: number }): Observable<any>;
}

interface TaskExecutionService {
  startTask(data: { taskId: number }): Observable<any>;
  getTaskStatus(data: { taskId: number }): Observable<any>;
}

@Controller()
export class AppController implements OnModuleInit {
  private readonly logger = new Logger(AppController.name);
  private taskManagementService: TaskManagementService;
  private taskExecutionService: TaskExecutionService;

  constructor(
    @Inject('TASK_MANAGEMENT_PACKAGE') private readonly taskManagementClient: ClientGrpc,
    @Inject('TASK_EXECUTION_PACKAGE') private readonly taskExecutionClient: ClientGrpc,
  ) {}

  onModuleInit() {
    this.taskManagementService =
      this.taskManagementClient.getService<TaskManagementService>('TaskManagementService');
    this.taskExecutionService =
      this.taskExecutionClient.getService<TaskExecutionService>('TaskExecutionService');
  }

  @Post('/tasks')
  async createTask(@Body() body) {
    this.logger.log(`Creating task with data: ${JSON.stringify(body)}`);
    try {
      const response = await lastValueFrom(this.taskManagementService.createTask(body));
      this.logger.log(`Task created with ID: ${response.id}`);
      this.logger.log(`Task created: ${response}`);
      return response;
    } catch (error) {
      this.logger.error(`Error creating task: ${error.message}`);
      throw error;
    }
  }

  @Get('/tasks/:id')
  async getTaskById(@Param('id', ParseIntPipe) id: number) {
    this.logger.log(`Fetching task with ID: ${id}`);
    try {
      const response = await lastValueFrom(this.taskManagementService.getTaskById({ id }));
      return response;
    } catch (error) {
      this.logger.error(`Error fetching task: ${error.message}`);
      throw error;
    }
  }

  @Post('/tasks/:id/execute')
  async startTask(@Param('id', ParseIntPipe) id: number) {
    this.logger.log(`Starting task with ID: ${id}`);
    try {
      const response = await lastValueFrom(this.taskExecutionService.startTask({ taskId: id }));
      return response;
    } catch (error) {
      this.logger.error(`Error starting task: ${error.message}`);
      throw error;
    }
  }

  @Get('/tasks/:id/status')
  async getTaskStatus(@Param('id', ParseIntPipe) id: number) {
    this.logger.log(`Getting status for task ID: ${id}`);
    try {
      const response = await lastValueFrom(this.taskExecutionService.getTaskStatus({ taskId: id }));
      return response;
    } catch (error) {
      this.logger.error(`Error getting task status: ${error.message}`);
      throw error;
    }
  }

  @Get('/tasks')
  async listTasks(@Body() body) {
    this.logger.log(`Listing tasks with parameters: ${JSON.stringify(body)}`);
    try {
      const response = await lastValueFrom(this.taskManagementService.listTasks(body));
      return response;
    } catch (error) {
      this.logger.error(`Error listing tasks: ${error.message}`);
      throw error;
    }
  }

    @Get('/status')
  getStatus(): string {
    return 'Gateway is running';
  }
}

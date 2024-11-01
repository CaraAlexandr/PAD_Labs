//gateway/app.controller.ts
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
import { GatewayService } from './gateway.service';

@Controller()
export class AppController {
  private readonly logger = new Logger(AppController.name);

  constructor(private readonly gatewayService: GatewayService) {}

  @Post('/tasks')
  async createTask(@Body() body) {
    this.logger.log(`Creating task with data: ${JSON.stringify(body)}`);
    try {
      const response = await this.gatewayService.createTask(body);
      this.logger.log(`Task created with ID: ${response.id}`);
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
      const response = await this.gatewayService.getTaskById(id);
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
      const response = await this.gatewayService.startTask(id);
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
      const response = await this.gatewayService.getTaskStatus(id);
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
      const response = await this.gatewayService.listTasks(body);
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

import { Controller, Post, Body, Get, Param, OnModuleInit, Inject } from '@nestjs/common';
import { ClientGrpc } from '@nestjs/microservices';
import { Observable } from 'rxjs';

interface TaskManagementService {
  createTask(data: { description: string, task_type: string }): Observable<any>;
  getTaskById(data: { id: number }): Observable<any>;
  listTasks(data: { page_number: number, page_size: number }): Observable<any>;
}

interface TaskExecutionService {
  startTask(data: { task_id: number }): Observable<any>;
  getTaskStatus(data: { task_id: number }): Observable<any>;
}

@Controller()
export class AppController implements OnModuleInit {
  private taskManagementService: TaskManagementService;
  private taskExecutionService: TaskExecutionService;

  constructor(
    @Inject('TASK_MANAGEMENT_PACKAGE') private readonly taskManagementClient: ClientGrpc,
    @Inject('TASK_EXECUTION_PACKAGE') private readonly taskExecutionClient: ClientGrpc,
  ) {}

  onModuleInit() {
    this.taskManagementService = this.taskManagementClient.getService<TaskManagementService>('TaskManagementService');
    this.taskExecutionService = this.taskExecutionClient.getService<TaskExecutionService>('TaskExecutionService');
  }

  @Post('/tasks')
  createTask(@Body() body) {
    return this.taskManagementService.createTask(body);
  }

  @Get('/tasks/:id')
  getTaskById(@Param('id') id: number) {
    return this.taskManagementService.getTaskById({ id });
  }

  @Post('/tasks/:id/execute')
  startTask(@Param('id') id: number) {
    return this.taskExecutionService.startTask({ task_id: id });
  }

  @Get('/tasks/:id/status')
  getTaskStatus(@Param('id') id: number) {
    return this.taskExecutionService.getTaskStatus({ task_id: id });
  }
}

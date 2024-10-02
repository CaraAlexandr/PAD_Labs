// gateway/src/app.controller.ts
import { Controller, Post, Body, Get, Param, Delete, OnModuleInit, HttpException, HttpStatus } from '@nestjs/common';
import { ClientGrpc } from '@nestjs/microservices';
import { Inject } from '@nestjs/common';
import { Observable, throwError, TimeoutError } from 'rxjs';
import { timeout, catchError, tap } from 'rxjs/operators';
import { Cache } from 'cache-manager';
import { CACHE_MANAGER, Inject as InjectCache } from '@nestjs/common';

interface CreateTaskData {
  description: string;
  task_type: string;
  payload: string;
}

interface TaskResponse {
  id: number;
  description: string;
  task_type: string;
  status: string;
  payload: string;
  result: string;
  created_at: string;
  updated_at: string;
  finished_at: string;
}

interface TasksResponse {
  tasks: TaskResponse[];
}

interface TaskManagementService {
  CreateTask(data: CreateTaskData): Observable<TaskResponse>;
  GetTaskById(data: { id: number }): Observable<TaskResponse>;
  ListTasks(data: { page_number: number; page_size: number }): Observable<TasksResponse>;
  DeleteTask(data: { id: number }): Observable<{ message: string }>;
}

interface StartTaskData {
  task_id: number;
}

interface StartTaskResponse {
  message: string;
}

interface TaskExecutionService {
  StartTask(data: StartTaskData): Observable<StartTaskResponse>;
  GetTaskStatus(data: { task_id: number }): Observable<{ status: string; result: string }>;
}

@Controller()
export class AppController implements OnModuleInit {
  private taskManagementService: TaskManagementService;
  private taskExecutionService: TaskExecutionService;

  constructor(
    @Inject('TASK_MANAGEMENT_PACKAGE') private readonly taskManagementClient: ClientGrpc,
    @Inject('TASK_EXECUTION_PACKAGE') private readonly taskExecutionClient: ClientGrpc,
    @InjectCache() private cacheManager: Cache,
  ) {}

  onModuleInit() {
    this.taskManagementService = this.taskManagementClient.getService<TaskManagementService>('TaskManagementService');
    this.taskExecutionService = this.taskExecutionClient.getService<TaskExecutionService>('TaskExecutionService');
  }

  @Post('/tasks')
  createTask(@Body() body: CreateTaskData) {
    return this.taskManagementService.CreateTask(body).pipe(
      timeout(10000),
      catchError((err) => {
        if (err instanceof TimeoutError) {
          return throwError(new HttpException('Request timed out', HttpStatus.REQUEST_TIMEOUT));
        }
        return throwError(err);
      }),
    );
  }

  @Get('/tasks/:id')
  async getTaskById(@Param('id') id: number) {
    const cacheKey = `task_${id}`;
    const cached = await this.cacheManager.get<TaskResponse>(cacheKey);
    if (cached) {
      return cached;
    }

    return this.taskManagementService.GetTaskById({ id }).pipe(
      timeout(10000),
      tap((task) => {
        this.cacheManager.set(cacheKey, task, { ttl: 300 }); // Cache for 5 minutes
      }),
      catchError((err) => {
        if (err instanceof TimeoutError) {
          return throwError(new HttpException('Request timed out', HttpStatus.REQUEST_TIMEOUT));
        }
        return throwError(err);
      }),
    );
  }

  @Get('/tasks')
  async listTasks(@Body() body: { page_number: number; page_size: number }) {
    const cacheKey = `tasks_page_${body.page_number}_size_${body.page_size}`;
    const cached = await this.cacheManager.get<TasksResponse>(cacheKey);
    if (cached) {
      return cached;
    }

    return this.taskManagementService.ListTasks(body).pipe(
      timeout(10000),
      tap((tasks) => {
        this.cacheManager.set(cacheKey, tasks, { ttl: 300 }); // Cache for 5 minutes
      }),
      catchError((err) => {
        if (err instanceof TimeoutError) {
          return throwError(new HttpException('Request timed out', HttpStatus.REQUEST_TIMEOUT));
        }
        return throwError(err);
      }),
    );
  }

  @Delete('/tasks/:id')
  deleteTask(@Param('id') id: number) {
    // Invalidate cache when a task is deleted
    const taskCacheKey = `task_${id}`;
    const tasksListCacheKeyPrefix = `tasks_page_`;

    this.cacheManager.del(taskCacheKey);
    // Optionally, delete all tasks list caches
    // This requires knowing all page numbers, or implement a pattern-based deletion

    return this.taskManagementService.DeleteTask({ id }).pipe(
      timeout(10000),
      catchError((err) => {
        if (err instanceof TimeoutError) {
          return throwError(new HttpException('Request timed out', HttpStatus.REQUEST_TIMEOUT));
        }
        return throwError(err);
      }),
    );
  }

  @Post('/tasks/:id/execute')
  startTask(@Param('id') id: number) {
    return this.taskExecutionService.StartTask({ task_id: id }).pipe(
      timeout(10000),
      catchError((err) => {
        if (err instanceof TimeoutError) {
          return throwError(new HttpException('Request timed out', HttpStatus.REQUEST_TIMEOUT));
        }
        return throwError(err);
      }),
    );
  }

  @Get('/tasks/:id/status')
  getTaskStatus(@Param('id') id: number) {
    return this.taskExecutionService.GetTaskStatus({ task_id: id }).pipe(
      timeout(10000),
      catchError((err) => {
        if (err instanceof TimeoutError) {
          return throwError(new HttpException('Request timed out', HttpStatus.REQUEST_TIMEOUT));
        }
        return throwError(err);
      }),
    );
  }
}

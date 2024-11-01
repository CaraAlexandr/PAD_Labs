import { Injectable, Inject } from '@nestjs/common';
import { ClientGrpc } from '@nestjs/microservices';
import * as CircuitBreaker from 'opossum';
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

@Injectable()
export class GatewayService {
  private taskManagementService: TaskManagementService;
  private taskExecutionService: TaskExecutionService;

  // Circuit breaker configuration options
  private breakerOptions = {
    timeout: 5000, // Time in ms to wait before timing out a request
    errorThresholdPercentage: 50, // Circuit breaker trips after 50% failures
    resetTimeout: 10000, // Time in ms before attempting to reset the breaker
  };

  private createTaskBreaker: CircuitBreaker;
  private getTaskByIdBreaker: CircuitBreaker;
  private listTasksBreaker: CircuitBreaker;
  private startTaskBreaker: CircuitBreaker;
  private getTaskStatusBreaker: CircuitBreaker;

  constructor(
    @Inject('TASK_MANAGEMENT_PACKAGE') private readonly taskManagementClient: ClientGrpc,
    @Inject('TASK_EXECUTION_PACKAGE') private readonly taskExecutionClient: ClientGrpc,
  ) {
    this.initializeCircuitBreakers();
  }

  onModuleInit() {
    this.taskManagementService = this.taskManagementClient.getService<TaskManagementService>('TaskManagementService');
    this.taskExecutionService = this.taskExecutionClient.getService<TaskExecutionService>('TaskExecutionService');
  }

  // Initialize all circuit breakers
  private initializeCircuitBreakers() {
    this.createTaskBreaker = new CircuitBreaker(this.callCreateTask.bind(this), this.breakerOptions);
    this.getTaskByIdBreaker = new CircuitBreaker(this.callGetTaskById.bind(this), this.breakerOptions);
    this.listTasksBreaker = new CircuitBreaker(this.callListTasks.bind(this), this.breakerOptions);
    this.startTaskBreaker = new CircuitBreaker(this.callStartTask.bind(this), this.breakerOptions);
    this.getTaskStatusBreaker = new CircuitBreaker(this.callGetTaskStatus.bind(this), this.breakerOptions);
  }

  // Service methods with circuit breakers
  async createTask(body: any): Promise<any> {
    return await this.createTaskBreaker.fire(body);
  }

  async getTaskById(id: number): Promise<any> {
    return await this.getTaskByIdBreaker.fire(id);
  }

  async listTasks(body: any): Promise<any> {
    return await this.listTasksBreaker.fire(body);
  }

  async startTask(id: number): Promise<any> {
    return await this.startTaskBreaker.fire(id);
  }

  async getTaskStatus(id: number): Promise<any> {
    return await this.getTaskStatusBreaker.fire(id);
  }

  // Actual gRPC calls wrapped with circuit breakers
  private async callCreateTask(body: any): Promise<any> {
    const response = await lastValueFrom(this.taskManagementService.createTask(body));
    return response;
  }

  private async callGetTaskById(id: number): Promise<any> {
    const response = await lastValueFrom(this.taskManagementService.getTaskById({ id }));
    return response;
  }

  private async callListTasks(body: any): Promise<any> {
    const response = await lastValueFrom(this.taskManagementService.listTasks(body));
    return response;
  }

  private async callStartTask(id: number): Promise<any> {
    const response = await lastValueFrom(this.taskExecutionService.startTask({ taskId: id }));
    return response;
  }

  private async callGetTaskStatus(id: number): Promise<any> {
    const response = await lastValueFrom(this.taskExecutionService.getTaskStatus({ taskId: id }));
    return response;
  }
}

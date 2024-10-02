// gateway/src/interfaces/task-management.interface.ts
import { Observable } from 'rxjs';
import { TaskResponse, TasksResponse } from './task.interface';

export interface TaskManagementService {
  CreateTask(data: CreateTaskData): Observable<TaskResponse>;
  GetTaskById(data: { id: number }): Observable<TaskResponse>;
  ListTasks(data: { page_number: number; page_size: number }): Observable<TasksResponse>;
  DeleteTask(data: { id: number }): Observable<{ message: string }>;
}

export interface CreateTaskData {
  description: string;
  task_type: string;
  payload: string;
}

// gateway/src/interfaces/task-execution.interface.ts
import { Observable } from 'rxjs';
import { StartTaskResponse } from './task.interface';

export interface TaskExecutionService {
  StartTask(data: StartTaskData): Observable<StartTaskResponse>;
  GetTaskStatus(data: { task_id: number }): Observable<{ status: string; result: string }>;
}

export interface StartTaskData {
  task_id: number;
}

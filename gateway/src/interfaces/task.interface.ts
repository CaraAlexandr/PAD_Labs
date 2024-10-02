// gateway/src/interfaces/task.interface.ts
export interface TaskResponse {
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

export interface TasksResponse {
  tasks: TaskResponse[];
}

export interface StartTaskResponse {
  message: string;
}

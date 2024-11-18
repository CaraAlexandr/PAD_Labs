import { Controller, Get, Post, Put, Delete, Body, Param } from '@nestjs/common';
import axios from 'axios';

@Controller('tasks')
export class TaskController {
  private taskServiceUrl = process.env.TASK_MANAGEMENT_URL || 'http://task_management_service:5000/tasks';

  @Post()
  async createTask(@Body() body) {
    const response = await axios.post(`${this.taskServiceUrl}/`, body);
    return response.data;
  }

  @Get(':id')
  async getTask(@Param('id') id: number) {
    const response = await axios.get(`${this.taskServiceUrl}/${id}`);
    return response.data;
  }

  @Get()
  async listTasks() {
    const response = await axios.get(`${this.taskServiceUrl}/`);
    return response.data;
  }

  @Put(':id')
  async updateTask(@Param('id') id: number, @Body() body) {
    const response = await axios.put(`${this.taskServiceUrl}/${id}`, body);
    return response.data;
  }

  @Delete(':id')
  async deleteTask(@Param('id') id: number) {
    const response = await axios.delete(`${this.taskServiceUrl}/${id}`);
    return response.data;
  }
}

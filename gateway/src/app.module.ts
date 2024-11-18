// src/app.module.ts
import { Module } from '@nestjs/common';
import { TaskController } from './controllers/task.controller';
import { ExecutionController } from './controllers/execution.controller';
import { ManualExecutionController } from './controllers/manual-execution.controller';
import { MetricsController } from './controllers/metrics.controller';
import { Registry } from 'prom-client';

@Module({
  controllers: [TaskController, ExecutionController, ManualExecutionController, MetricsController],
  providers: [Registry],
})
export class AppModule {}

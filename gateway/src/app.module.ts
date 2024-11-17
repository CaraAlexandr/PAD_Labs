import { Module } from '@nestjs/common';
import { TaskController } from './controllers/task.controller';
import { ExecutionController } from './controllers/execution.controller';
import {ManualExecutionController} from "./controllers/manual-execution.controller";

@Module({
  controllers: [TaskController, ExecutionController, ManualExecutionController],
})
export class AppModule {}

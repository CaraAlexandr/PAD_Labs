import { Module, CacheModule } from '@nestjs/common';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { AppController } from './app.controller';
import { join } from 'path'; // Import path utility to manage proto paths
import * as redisStore from 'cache-manager-ioredis';

@Module({
  imports: [
    // Register Redis cache using cache-manager-ioredis
    CacheModule.register({
      store: redisStore,
      host: 'redis_pad',
      port: 6379,
    }),

    // Register gRPC clients
    ClientsModule.register([
      {
        name: 'TASK_MANAGEMENT_PACKAGE',
        transport: Transport.GRPC,
        options: {
          package: 'task_management',
          protoPath: join(__dirname, '../proto/task_management.proto'),
          url: 'task_management_service:8000',
        },
      },
      {
        name: 'TASK_EXECUTION_PACKAGE',
        transport: Transport.GRPC,
        options: {
          package: 'task_execution',
          protoPath: join(__dirname, '../proto/task_execution.proto'),
          url: 'task_execution_service:8001',
        },
      },
    ]),
  ],
  controllers: [AppController],
})
export class AppModule {}

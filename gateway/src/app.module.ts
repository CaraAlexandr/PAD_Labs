// gateway/src/app.module.ts
import { Module, CacheModule } from '@nestjs/common';
import { AppController } from './app.controller';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { join } from 'path';
import { ConfigModule } from '@nestjs/config';
import * as redisStore from 'cache-manager-redis-store';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    CacheModule.register({
      store: redisStore,
      host: 'redis_pad',
      port: 6379,
      ttl: 300, // seconds
    }),
    ClientsModule.register([
      {
        name: 'TASK_MANAGEMENT_PACKAGE',
        transport: Transport.GRPC,
        options: {
          package: 'taskmanagement',
          protoPath: join(__dirname, 'grpc/task_management.proto'),
          url: 'task_management_service:50051',
        },
      },
      {
        name: 'TASK_EXECUTION_PACKAGE',
        transport: Transport.GRPC,
        options: {
          package: 'taskexecution',
          protoPath: join(__dirname, 'grpc/task_execution.proto'),
          url: 'task_execution_service:50052',
        },
      },
    ]),
  ],
  controllers: [AppController],
  providers: [],
})
export class AppModule {}

import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { ServiceRegistry } from './service.registry';

@Module({
  imports: [],
  controllers: [AppController],
  providers: [ServiceRegistry],
})
export class AppModule {}

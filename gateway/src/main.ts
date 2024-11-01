import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { IoAdapter } from '@nestjs/platform-socket.io';
import { WebSocketAdapter, ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.useWebSocketAdapter(new IoAdapter() as unknown as WebSocketAdapter);

  // Enable global validation and transformation
  app.useGlobalPipes(new ValidationPipe({
    transform: true, // Automatically transform payloads to DTO instances
    whitelist: true, // Strip unknown properties
    forbidNonWhitelisted: true, // Throw errors for unknown properties
  }));

  await app.listen(3000);
}
bootstrap();

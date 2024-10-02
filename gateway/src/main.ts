// gateway/src/main.ts
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { IoAdapter } from '@nestjs/platform-socket.io'; // Corrected import
import { ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Use IoAdapter for WebSocket support
  app.useWebSocketAdapter(new IoAdapter(app));

  // Use global validation pipe if needed
  app.useGlobalPipes(new ValidationPipe());

  // // Swagger Configuration (Optional but recommended for API documentation)
  // const config = new DocumentBuilder()
  //   .setTitle('Gateway Service API')
  //   .setDescription('API documentation for the Gateway Service')
  //   .setVersion('1.0')
  //   .addBearerAuth()
  //   .build();
  // const document = SwaggerModule.createDocument(app, config);
  // SwaggerModule.setup('api', app, document);

  await app.listen(3000);
  console.log('Gateway Service is running on port 3000');
}
bootstrap();

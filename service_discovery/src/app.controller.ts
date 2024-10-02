// service_discovery/src/app.controller.ts
import { Controller, Post, Body, Get } from '@nestjs/common';
import { AppService, ServiceRegistration } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/register')
  registerService(@Body() service: ServiceRegistration) {
    this.appService.registerService(service);
    return { message: 'Service registered successfully' };
  }

  @Get('/services')
  listServices(): ServiceRegistration[] {
    return this.appService.listServices();
  }

  @Get('/status')
  status() {
    return { status: 'Service Discovery is running' };
  }
}

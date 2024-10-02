import { Controller, Post, Get, Body } from '@nestjs/common';
import { ServiceRegistry } from './service.registry';

@Controller()
export class AppController {
  constructor(private readonly registry: ServiceRegistry) {}

  @Post('/register')
  registerService(@Body() serviceInfo) {
    this.registry.registerService(serviceInfo.name, serviceInfo);
    return { message: 'Service registered successfully' };
  }

  @Get('/services')
  getServices() {
    return this.registry.getAllServices();
  }

  @Get('/status')
  getStatus(): string {
    return 'Service Discovery is running';
  }
}

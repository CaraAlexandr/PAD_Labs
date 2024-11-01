import { Controller, Get, Param, Post, Body } from '@nestjs/common';
import { ServiceRegistry } from './service.registry';

@Controller('discovery')
export class AppController {
  constructor(private readonly serviceRegistry: ServiceRegistry) {}

  @Post('register')
  async register(@Body('name') name: string, @Body('url') url: string) {
    await this.serviceRegistry.registerService(name, url);
    return { message: `${name} registered at ${url}` };
  }

  @Get('lookup/:name')
  async lookup(@Param('name') name: string) {
    const serviceUrl = await this.serviceRegistry.lookupService(name);
    return { serviceUrl };
  }

  @Get('list')
  async listServices() {
    const services = await this.serviceRegistry.listServices();
    return { services };
  }

      @Get('status')
  getStatus(): string {
    return 'Service Discovery is running';
  }
}

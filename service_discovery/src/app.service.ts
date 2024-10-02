// service_discovery/src/app.service.ts
import { Injectable } from '@nestjs/common';

export interface ServiceRegistration {
  name: string;
  address: string;
  port: number;
}

@Injectable()
export class AppService {
  private services: ServiceRegistration[] = [];

  registerService(service: ServiceRegistration) {
    const exists = this.services.find(
      (s) => s.name === service.name && s.address === service.address && s.port === service.port,
    );
    if (!exists) {
      this.services.push(service);
    }
  }

  listServices(): ServiceRegistration[] {
    return this.services;
  }
}

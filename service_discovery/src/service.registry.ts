import { Injectable } from '@nestjs/common';

@Injectable()
export class ServiceRegistry {
  private services = new Map<string, any>();

  registerService(name: string, info: any) {
    this.services.set(name, info);
  }

  getService(name: string): any {
    return this.services.get(name);
  }

  getAllServices(): any[] {
    return Array.from(this.services.values());
  }
}

import { Injectable } from '@nestjs/common';
import * as Redis from 'ioredis';

@Injectable()
export class ServiceRegistry {
  private readonly redis: Redis.Redis;

  // Register a service with a specific name and URL
  async registerService(serviceName: string, serviceUrl: string) {
    await this.redis.hset('services', serviceName, serviceUrl);
  }

  // Lookup a service by name
  async lookupService(serviceName: string): Promise<string | null> {
    return await this.redis.hget('services', serviceName);
  }

  // Deregister a service by name
  async deregisterService(serviceName: string) {
    await this.redis.hdel('services', serviceName);
  }

  // List all registered services
  async listServices(): Promise<{ [key: string]: string }> {
    return await this.redis.hgetall('services');
  }
}

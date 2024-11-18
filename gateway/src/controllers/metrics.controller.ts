// src/controllers/metrics.controller.ts
import { Controller, Get, Res } from '@nestjs/common';
import { Response } from 'express';
import { Registry } from 'prom-client';

@Controller('metrics')
export class MetricsController {
  constructor(private readonly registry: Registry) {}

  @Get()
  async getMetrics(@Res() res: Response) {
    res.set('Content-Type', this.registry.contentType);
    res.end(await this.registry.metrics());
  }
}

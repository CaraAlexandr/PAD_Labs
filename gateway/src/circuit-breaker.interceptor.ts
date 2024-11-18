import {
  Injectable,
  ExecutionContext,
  CallHandler,
  NestInterceptor,
} from '@nestjs/common';
import { Observable, TimeoutError, throwError } from 'rxjs';
import { catchError, timeout } from 'rxjs/operators';

@Injectable()
export class CircuitBreakerInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const timeoutLimit = 5000; // Adjust as needed

    return next.handle().pipe(
      timeout(timeoutLimit),
      catchError((err) => {
        if (err instanceof TimeoutError) {
          console.error('Service timeout, circuit breaker tripped.');
        }
        return throwError(() => err);
      }),
    );
  }
}

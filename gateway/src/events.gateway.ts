// gateway/src/events.gateway.ts

import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  MessageBody,
  ConnectedSocket,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';

@WebSocketGateway({
  namespace: '/lobby',
})
export class EventsGateway {
  @WebSocketServer()
  server: Server;

  @SubscribeMessage('join')
  handleJoin(@MessageBody() data: any, @ConnectedSocket() client: Socket) {
    const { task_id } = data;
    if (task_id) {
      const room = `task_${task_id}`;
      client.join(room);
      client.emit('joined', { room });
    } else {
      client.join('all_tasks');
      client.emit('joined', { room: 'all_tasks' });
    }
  }

  @SubscribeMessage('leave')
  handleLeave(@MessageBody() data: any, @ConnectedSocket() client: Socket) {
    const { task_id } = data;
    if (task_id) {
      const room = `task_${task_id}`;
      client.leave(room);
      client.emit('left', { room });
    } else {
      client.leave('all_tasks');
      client.emit('left', { room: 'all_tasks' });
    }
  }

  // Method to emit task updates
  emitTaskUpdate(taskUpdate: any) {
    this.server.to('all_tasks').emit('task_update', taskUpdate);
    this.server.to(`task_${taskUpdate.id}`).emit('task_update', taskUpdate);
  }
}

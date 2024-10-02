import { WebSocketGateway, WebSocketServer, SubscribeMessage, ConnectedSocket, MessageBody } from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';

@WebSocketGateway({ namespace: '/lobby', cors: true })
export class TaskGateway {
  @WebSocketServer()
  server: Server;

  @SubscribeMessage('join')
  handleJoin(@ConnectedSocket() client: Socket, @MessageBody() data: { task_id: string }) {
    if (data.task_id) {
      client.join(data.task_id);
      client.emit('status', `Joined task room: ${data.task_id}`);
    } else {
      client.emit('status', 'Joined general lobby');
    }
  }

  @SubscribeMessage('leave')
  handleLeave(@ConnectedSocket() client: Socket, @MessageBody() data: { task_id: string }) {
    if (data.task_id) {
      client.leave(data.task_id);
      client.emit('status', `Left task room: ${data.task_id}`);
    } else {
      client.emit('status', 'Left general lobby');
    }
  }

  broadcastTaskUpdate(task_id: string, status: string) {
    // Emit task updates to specific task rooms and the general lobby
    this.server.to(task_id).emit('task_update', { task_id, status });
    this.server.emit('task_update', { task_id, status });
  }
}

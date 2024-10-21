const io = require('socket.io-client');

// Connect to the /lobby namespace on port 5001
const socket = io('http://localhost:5001/lobby');

socket.on('connect', () => {
    console.log('Connected to server');

    // Emit join_task event
    socket.emit('join_task', { task_id: '14', user: 'TestUser' });
});

socket.on('joined', (data) => {
    console.log(`Joined room: ${data.room}`);
});

socket.on('task_update', (data) => {
    console.log(`Task ${data.id} status: ${data.status}`);
    if (data.status === 'completed') {
        console.log(`Result:`, data.result);
    }
});

socket.on('error', (data) => {
    console.error(`Error: ${data.message}`);
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
});

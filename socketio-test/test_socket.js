// client.js
const io = require('socket.io-client');

// Connect to the /lobby namespace on port 5001 with WebSocket transport
const socket = io('http://localhost:5001/lobby', {
    transports: ['websocket'], // Force WebSocket transport to avoid polling issues
    reconnectionAttempts: 5,    // Limit reconnection attempts
    reconnectionDelay: 1000     // Delay before attempting to reconnect
});

const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
});

readline.question('What room would you like to join? (all or task ID): ', (answer) => {
    if (answer.toLowerCase() === 'all') {
        socket.emit('join_all_tasks', { user: 'TestUser' });
    } else {
        socket.emit('join_task', { task_id: answer, user: 'TestUser' });
    }
    readline.close();
});

socket.on('connect', () => {
    console.log('Connected to server');
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

socket.on('user_joined', (data) => {
    console.log(data.message);
});

socket.on('error', (data) => {
    console.error(`Error: ${data.message}`);
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    // Attempt reconnection logic if needed
    setTimeout(() => {
        console.log('Reconnecting...');
        socket.connect();
    }, 1000); // Wait before attempting to reconnect
});

// WebSocket client
import { io } from 'socket.io-client';
import { config } from './config.js';

let socket = null;

export function initSocket() {
  if (socket) return socket;
  
  socket = io(config.backendUrl, {
    transports: ['websocket', 'polling']
  });
  
  socket.on('connect', () => {
    console.log('[socket] Connected to server');
  });
  
  socket.on('disconnect', () => {
    console.log('[socket] Disconnected from server');
  });
  
  socket.on('connect_error', (error) => {
    console.error('[socket] Connection error:', error);
  });
  
  return socket;
}

export function getSocket() {
  return socket || initSocket();
}

export function disconnectSocket() {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
}



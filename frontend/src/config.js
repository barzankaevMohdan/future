// Централизованная конфигурация приложения
export const config = {
  backendUrl: import.meta.env.VITE_BACKEND_URL || 'http://localhost:3000',
  videoStreamUrl: import.meta.env.VITE_VIDEO_STREAM_URL || 'http://localhost:5001',
  presencePollingInterval: 5000, // мс
  eventsLimit: 200
};


<template>
  <div class="video-container">
    <div class="video-header">
      <h3>Камера в реальном времени</h3>
      <div class="status">
        <span :class="['status-dot', isConnected ? 'status-online' : 'status-offline']"></span>
        <span>{{ isConnected ? 'Онлайн' : 'Офлайн' }}</span>
      </div>
    </div>

    <div class="video-wrapper">
      <img 
        :src="videoUrl" 
        alt="Camera feed"
        class="video-feed"
        :class="{ 'video-hidden': !isConnected }"
        @error="handleError"
        @load="handleLoad"
      />
      <div v-if="!isConnected" class="no-video overlay">
        <div class="no-video-icon">📹</div>
        <div class="no-video-text">
          {{ error || 'Подключение к камере...' }}
        </div>
        <button @click="reconnect" class="btn-reconnect">
          Переподключиться
        </button>
      </div>
    </div>

    <div class="video-info">
      <div class="info-item">
        <span class="info-label">Источник:</span>
        <span class="info-value">{{ streamBaseUrl }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">FPS:</span>
        <span class="info-value">~30</span>
      </div>
    </div>

    <div class="legend">
      <div class="legend-item">
        <span class="legend-box legend-green"></span>
        <span>Распознанные сотрудники</span>
      </div>
      <div class="legend-item">
        <span class="legend-box legend-red"></span>
        <span>Нераспознанные лица</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { config } from '../config.js';

const streamBaseUrl = config.videoStreamUrl;
const isConnected = ref(true); // Начинаем с true - пусть пытается показать
const error = ref('');
const videoUrl = ref(`${config.videoStreamUrl}/video_feed`);
let checkInterval = null;

const handleLoad = () => {
  // MJPEG стрим не триггерит load event нормально
  // Просто устанавливаем соединение как активное
  setTimeout(() => {
    isConnected.value = true;
    error.value = '';
    console.log('[VideoStream] Connected to camera feed');
  }, 1000);
};

const handleError = (e) => {
  isConnected.value = false;
  error.value = 'Не удалось подключиться к камере';
  console.error('[VideoStream] Error loading video feed:', e);
};

const reconnect = () => {
  error.value = '';
  // Обновляем URL с новым timestamp для принудительной перезагрузки
  videoUrl.value = `${streamBaseUrl}/video_feed?t=${Date.now()}`;
  isConnected.value = true;
};

const checkConnection = async () => {
  try {
    const res = await fetch(`${streamBaseUrl}/health`);
    if (res.ok) {
      const data = await res.json();
      if (data.streaming && !isConnected.value) {
        // Камера работает, устанавливаем соединение
        isConnected.value = true;
        error.value = '';
        console.log('[VideoStream] Camera is streaming');
      } else if (!data.streaming && isConnected.value) {
        isConnected.value = false;
        error.value = 'Камера не передаёт видео';
      }
    }
  } catch (e) {
    if (isConnected.value) {
      isConnected.value = false;
      error.value = 'Потеряно соединение с сервером';
    }
  }
};

onMounted(() => {
  // Сразу пытаемся подключиться
  setTimeout(() => {
    checkConnection();
  }, 500);
  
  // Проверяем доступность стрима каждые 3 секунды
  checkInterval = setInterval(checkConnection, 3000);
});

onBeforeUnmount(() => {
  if (checkInterval) {
    clearInterval(checkInterval);
  }
});
</script>

<style scoped>
.video-container {
  background: white;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #ddd;
}

.video-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.video-header h3 {
  margin: 0;
  font-size: 16px;
}

.status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.status-online {
  background: #4caf50;
  box-shadow: 0 0 8px #4caf50;
  animation: pulse 2s infinite;
}

.status-offline {
  background: #ccc;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.video-wrapper {
  position: relative;
  width: 100%;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 16 / 9;
}

.video-feed {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.video-hidden {
  opacity: 0;
}

.no-video {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  z-index: 10;
}

.no-video-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.3;
}

.no-video-text {
  font-size: 16px;
  margin-bottom: 16px;
}

.btn-reconnect {
  padding: 8px 16px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-reconnect:hover {
  background: #1976d2;
}

.video-info {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  font-size: 12px;
  color: #666;
}

.info-item {
  display: flex;
  gap: 4px;
}

.info-label {
  font-weight: 600;
}

.info-value {
  font-family: monospace;
}

.legend {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.legend-box {
  width: 20px;
  height: 20px;
  border-radius: 3px;
  border: 2px solid;
}

.legend-green {
  border-color: #4caf50;
  background: rgba(76, 175, 80, 0.2);
}

.legend-red {
  border-color: #f44336;
  background: rgba(244, 67, 54, 0.2);
}
</style>


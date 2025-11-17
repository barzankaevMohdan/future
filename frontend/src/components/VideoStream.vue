<template>
  <div class="video-stream">
    <div class="video-header">
      <div class="header-info">
        <el-icon :size="20"><VideoCamera /></el-icon>
        <span class="header-title">Камера в реальном времени</span>
      </div>
      <div class="status-indicator">
        <el-badge
          :value="isConnected ? 'Онлайн' : 'Офлайн'"
          :type="isConnected ? 'success' : 'info'"
        >
          <el-icon :size="20" :color="isConnected ? '#67c23a' : '#909399'">
            <VideoCameraFilled />
          </el-icon>
        </el-badge>
      </div>
    </div>

    <div class="video-wrapper">
      <el-image
        :src="videoUrl"
        fit="contain"
        class="video-feed"
        :class="{ 'video-hidden': !isConnected }"
        @error="handleError"
        @load="handleLoad"
      >
        <template #error>
          <div class="video-error">
            <el-icon :size="64" color="#909399">
              <VideoCamera />
            </el-icon>
          </div>
        </template>
      </el-image>

      <div v-if="!isConnected" class="no-video-overlay">
        <el-result
          icon="warning"
          :title="error || 'Подключение к камере...'"
        >
          <template #icon>
            <el-icon :size="80" color="#e6a23c">
              <VideoCamera />
            </el-icon>
          </template>
          <template #extra>
            <el-button
              type="primary"
              size="large"
              :icon="Refresh"
              @click="reconnect"
            >
              Переподключиться
            </el-button>
          </template>
        </el-result>
      </div>
    </div>

    <el-divider />

    <!-- Информация о видеопотоке -->
    <el-descriptions :column="2" size="small" border>
      <el-descriptions-item label="Источник" label-align="right">
        <el-text type="info" size="small" style="font-family: monospace">
          {{ streamBaseUrl }}
        </el-text>
      </el-descriptions-item>
      <el-descriptions-item label="FPS" label-align="right">
        <el-tag type="success" size="small" effect="plain">~30</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="Статус" label-align="right">
        <el-tag :type="isConnected ? 'success' : 'info'" size="small">
          {{ isConnected ? 'Активен' : 'Ожидание' }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="Качество" label-align="right">
        <el-tag type="primary" size="small" effect="plain">HD</el-tag>
      </el-descriptions-item>
    </el-descriptions>

    <el-divider />

    <!-- Легенда распознавания -->
    <div class="legend-section">
      <div class="legend-title">
        <el-icon><InfoFilled /></el-icon>
        <span>Обозначения распознавания:</span>
      </div>
      <div class="legend-items">
        <el-card shadow="never" class="legend-card legend-card-green">
          <div class="legend-item-content">
            <div class="legend-box legend-box-green"></div>
            <div class="legend-text">
              <div class="legend-label">Зелёная рамка</div>
              <div class="legend-desc">Распознанные сотрудники</div>
            </div>
          </div>
        </el-card>
        <el-card shadow="never" class="legend-card legend-card-red">
          <div class="legend-item-content">
            <div class="legend-box legend-box-red"></div>
            <div class="legend-text">
              <div class="legend-label">Красная рамка</div>
              <div class="legend-desc">Нераспознанные лица</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import {
  VideoCamera,
  VideoCameraFilled,
  Refresh,
  InfoFilled
} from '@element-plus/icons-vue';
import { config } from '../config.js';

const streamBaseUrl = config.videoStreamUrl;
const isConnected = ref(true);
const error = ref('');
const videoUrl = ref(`${config.videoStreamUrl}/video_feed`);
let checkInterval = null;

const handleLoad = () => {
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
  videoUrl.value = `${streamBaseUrl}/video_feed?t=${Date.now()}`;
  isConnected.value = true;
};

const checkConnection = async () => {
  try {
    const res = await fetch(`${streamBaseUrl}/health`);
    if (res.ok) {
      const data = await res.json();
      if (data.streaming && !isConnected.value) {
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
  setTimeout(() => {
    checkConnection();
  }, 500);

  checkInterval = setInterval(checkConnection, 3000);
});

onBeforeUnmount(() => {
  if (checkInterval) {
    clearInterval(checkInterval);
  }
});
</script>

<style scoped>
.video-stream {
  width: 100%;
}

.video-header {
  display: flex;
  justify-content: space-between;
  padding-right: 40px;
  align-items: center;
  margin-bottom: 16px;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.status-indicator {
  display: flex;
  align-items: center;
}

.video-wrapper {
  position: relative;
  width: 100%;
  max-width: 100%;
  background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 16 / 9;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.video-feed {
  width: 100%;
  height: 100%;
  display: block;
  transition: opacity 0.3s ease;
}

.video-hidden {
  opacity: 0;
}

.video-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: #2d2d2d;
}

.no-video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

:deep(.el-result__title) {
  color: #ffffff;
  font-size: 18px;
}

:deep(.el-divider) {
  margin: 20px 0;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}

.legend-section {
  margin-top: 16px;
}

.legend-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 12px;
}

.legend-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.legend-card {
  background: #fafafa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.legend-card-green {
  border-left: 4px solid #67c23a;
}

.legend-card-red {
  border-left: 4px solid #f56c6c;
}

:deep(.legend-card .el-card__body) {
  padding: 12px;
}

.legend-item-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.legend-box {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 3px solid;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.legend-box-green {
  border-color: #67c23a;
  background: rgba(103, 194, 58, 0.1);
}

.legend-box-red {
  border-color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

.legend-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.legend-label {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.legend-desc {
  font-size: 12px;
  color: #909399;
}

/* Адаптивность */
@media (max-width: 768px) {
  .header-title {
    font-size: 14px;
  }

  .legend-items {
    grid-template-columns: 1fr;
  }

  :deep(.el-descriptions) {
    font-size: 12px;
  }
  
  .legend-box {
    width: 32px;
    height: 32px;
  }
  
  .legend-label {
    font-size: 13px;
  }
  
  .legend-desc {
    font-size: 11px;
  }
}

/* Улучшение для средних экранов */
@media (min-width: 768px) and (max-width: 1023px) {
  .legend-items {
    grid-template-columns: 1fr 1fr;
  }
}
</style>

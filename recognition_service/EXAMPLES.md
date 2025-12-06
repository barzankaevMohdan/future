# Примеры использования

## Локальный запуск

### Базовый запуск
```bash
export BACKEND_URL=http://localhost:3000
export CAMERA_SOURCE=0
python -m recognition_service.main
```

### С параметрами
```bash
python -m recognition_service.main \
  --camera-id camera-1 \
  --camera-source http://camera-gateway:4000/streams/1.mjpg \
  --backend-url http://backend:3000 \
  --debug
```

### С RTSP камерой
```bash
export BACKEND_URL=http://localhost:3000
export CAMERA_SOURCE=rtsp://admin:password@192.168.1.11:554/ISAPI/Streaming/Channels/101
export CAMERA_ID=front-door
python -m recognition_service.main
```

## Docker

### Standalone
```bash
docker build -t recognition-service .

docker run -d \
  --name recognition-1 \
  -e BACKEND_URL=http://backend:3000 \
  -e CAMERA_SOURCE=http://camera-gateway:4000/streams/1.mjpg \
  -e CAMERA_ID=1 \
  -p 5001:5001 \
  recognition-service
```

### Docker Compose - Одна камера
```yaml
version: '3.8'

services:
  recognition:
    build: ./recognition_service
    environment:
      - BACKEND_URL=http://backend:3000
      - CAMERA_SOURCE=http://camera-gateway:4000/streams/1.mjpg
      - CAMERA_ID=1
    ports:
      - "5001:5001"
    volumes:
      - recognition-cache:/app/cache
      - insightface-models:/root/.insightface
    depends_on:
      - backend
      - camera-gateway
    networks:
      - app-network

volumes:
  recognition-cache:
  insightface-models:

networks:
  app-network:
    driver: bridge
```

### Docker Compose - Несколько камер
```yaml
version: '3.8'

services:
  # Camera 1 - Front Door
  recognition-1:
    build: ./recognition_service
    container_name: recognition-front-door
    environment:
      - BACKEND_URL=http://backend:3000
      - CAMERA_SOURCE=http://camera-gateway:4000/streams/1.mjpg
      - CAMERA_ID=front-door
      - SERVICE_NAME=recognition-front-door
      - VIDEO_PORT=5001
    ports:
      - "5001:5001"
    volumes:
      - recognition-cache-1:/app/cache
      - insightface-models:/root/.insightface
    networks:
      - app-network

  # Camera 2 - Back Door
  recognition-2:
    build: ./recognition_service
    container_name: recognition-back-door
    environment:
      - BACKEND_URL=http://backend:3000
      - CAMERA_SOURCE=http://camera-gateway:4000/streams/2.mjpg
      - CAMERA_ID=back-door
      - SERVICE_NAME=recognition-back-door
      - VIDEO_PORT=5001
    ports:
      - "5002:5001"
    volumes:
      - recognition-cache-2:/app/cache
      - insightface-models:/root/.insightface
    networks:
      - app-network

  # Camera 3 - Office
  recognition-3:
    build: ./recognition_service
    container_name: recognition-office
    environment:
      - BACKEND_URL=http://backend:3000
      - CAMERA_SOURCE=http://camera-gateway:4000/streams/3.mjpg
      - CAMERA_ID=office
      - SERVICE_NAME=recognition-office
      - VIDEO_PORT=5001
    ports:
      - "5003:5001"
    volumes:
      - recognition-cache-3:/app/cache
      - insightface-models:/root/.insightface
    networks:
      - app-network

volumes:
  recognition-cache-1:
  recognition-cache-2:
  recognition-cache-3:
  insightface-models:

networks:
  app-network:
    driver: bridge
```

## Проверка работы

### Health check
```bash
curl http://localhost:5001/health
```

Ответ:
```json
{
  "status": "ok",
  "streaming": true,
  "cameraId": "1",
  "service": "recognition"
}
```

### Видео поток
```bash
# В браузере
http://localhost:5001/video_feed

# С curl (сохранить в файл)
curl http://localhost:5001/video_feed > stream.mjpg

# С FFplay
ffplay http://localhost:5001/video_feed
```

## Настройка параметров

### Точность распознавания

**Строже (меньше ложных срабатываний):**
```bash
export INSIGHTFACE_THRESHOLD=0.15  # Было 0.2
export MIN_EMBEDDINGS=3            # Было 2
export MIN_BLUR_VAR=100.0          # Было 50
```

**Мягче (больше распознаваний):**
```bash
export INSIGHTFACE_THRESHOLD=0.25
export MIN_EMBEDDINGS=1
export MIN_BLUR_VAR=30.0
```

### Производительность

**Быстрее (меньше точность):**
```bash
export FRAME_SKIP=5                # Было 3
export ENABLE_PREPROCESSING=false
```

**Медленнее (больше точность):**
```bash
export FRAME_SKIP=1
export ENABLE_PREPROCESSING=true
```

### Логика присутствия

**Быстрая реакция:**
```bash
export IN_THRESHOLD=0.5   # Было 1.0
export OUT_THRESHOLD=5.0  # Было 10.0
```

**Медленная реакция (меньше ложных событий):**
```bash
export IN_THRESHOLD=3.0
export OUT_THRESHOLD=30.0
```

## Интеграция с Camera Gateway

### 1. Добавить камеру в gateway
```bash
curl -X POST http://localhost:4000/api/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Front Door Camera",
    "ip": "192.168.1.11",
    "username": "admin",
    "password": "11223344a"
  }'
```

### 2. Получить ID камеры
```bash
curl http://localhost:4000/api/cameras
# Ответ: [{"id": 1, ...}]
```

### 3. Использовать в recognition
```bash
export CAMERA_SOURCE=http://camera-gateway:4000/streams/1.mjpg
python -m recognition_service.main
```

## Мониторинг

### Логи
```bash
# Docker
docker logs recognition-1 -f

# Локально
# Логи выводятся в stdout
```

### Метрики
```bash
# Health check
curl http://localhost:5001/health

# Видео поток (проверка работы)
curl -I http://localhost:5001/video_feed
```

## Troubleshooting

### Нет сотрудников
```
[ERROR] No employees with photos found!
```

**Решение:** Добавьте сотрудников через backend API

### Камера не подключается
```
[ERROR] Cannot connect to camera after 5 attempts
```

**Решение:**
- Проверьте CAMERA_SOURCE
- Проверьте доступность камеры
- Проверьте логи camera-gateway (если используется)

### Низкая производительность
```
# Увеличить FRAME_SKIP
export FRAME_SKIP=5

# Отключить preprocessing
export ENABLE_PREPROCESSING=false
```

### Ложные срабатывания
```
# Увеличить порог
export INSIGHTFACE_THRESHOLD=0.15

# Увеличить минимум эмбеддингов
export MIN_EMBEDDINGS=3
```

## Полная система

```yaml
version: '3.8'

services:
  backend:
    # Your backend service
    
  frontend:
    # Your frontend service
    
  camera-gateway:
    build: ./camera-stream-gateway
    ports:
      - "4000:4000"
    volumes:
      - camera-data:/app
    networks:
      - app-network

  recognition:
    build: ./recognition_service
    environment:
      - BACKEND_URL=http://backend:3000
      - CAMERA_SOURCE=http://camera-gateway:4000/streams/1.mjpg
      - CAMERA_ID=1
    ports:
      - "5001:5001"
    volumes:
      - recognition-cache:/app/cache
      - insightface-models:/root/.insightface
    depends_on:
      - backend
      - camera-gateway
    networks:
      - app-network

volumes:
  camera-data:
  recognition-cache:
  insightface-models:

networks:
  app-network:
    driver: bridge
```









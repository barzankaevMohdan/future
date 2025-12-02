# Recognition Service - Refactored

Модульный Python сервис для распознавания лиц и отслеживания присутствия сотрудников.

## Структура проекта

```
recognition_service/
├── __init__.py              # Package initialization
├── main.py                  # Entry point
├── config.py                # Configuration from environment
├── logging_config.py        # Logging setup
├── app.py                   # Flask HTTP API
├── streaming.py             # MJPEG streaming and frame management
├── camera.py                # Camera connection and management
├── employees.py             # Employee data and embeddings
├── events.py                # Backend event sending
├── video_loop.py            # Main processing loop
├── recognition/             # Recognition algorithms
│   ├── __init__.py
│   ├── quality.py          # Face quality assessment
│   ├── preprocessing.py    # Image preprocessing
│   ├── tracker.py          # Face tracking
│   ├── presence.py         # Presence management (IN/OUT)
│   └── matching.py         # Embedding matching
└── utils/                   # Utilities
    ├── __init__.py
    ├── cache.py            # Embeddings cache
    └── timing.py           # Timing utilities
```

## Переменные окружения

### Backend Integration
```bash
BACKEND_URL=http://backend:3000  # Backend API URL
```

### Camera Settings
```bash
CAMERA_SOURCE=0                  # Camera source:
                                 #   - 0, 1, 2 for local webcam
                                 #   - rtsp://user:pass@ip:port/path
                                 #   - http://camera-gateway:4000/streams/1.mjpg

CAMERA_ID=camera-1               # Logical camera identifier
FRAME_SKIP=3                     # Process every N-th frame
```

### Service Identity
```bash
SERVICE_NAME=recognition         # Service instance name
VIDEO_PORT=5001                  # Flask HTTP port
```

### Quality Thresholds
```bash
MIN_FACE_HEIGHT=20               # Minimum face height (pixels)
MIN_BLUR_VAR=50.0                # Minimum blur variance (Laplacian)
```

### Preprocessing
```bash
ENABLE_PREPROCESSING=true        # Enable image enhancement
CLAHE_CLIP=2.0                   # CLAHE contrast limit
DENOISE_STRENGTH=5               # Denoising strength (0-10)
```

### Recognition
```bash
INSIGHTFACE_THRESHOLD=0.2        # Cosine similarity threshold
```

### Tracking
```bash
MIN_EMBEDDINGS=2                 # Min embeddings per track
TRACK_MAX_AGE=2.0                # Max track age (seconds)
```

### Presence Logic
```bash
IN_THRESHOLD=1.0                 # Stable presence for IN (seconds)
OUT_THRESHOLD=10.0               # Absence for OUT (seconds)
```

### System
```bash
RELOAD_INTERVAL=300              # Employee reload interval (seconds)
CACHE_FILE=face_encodings_cache.pkl  # Cache file path
DEBUG=true                       # Debug logging
```

## Установка

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

## Запуск

### Локально
```bash
# Set environment variables
export BACKEND_URL=http://localhost:3000
export CAMERA_SOURCE=0

# Run service
python -m recognition_service.main
```

### С параметрами CLI
```bash
python -m recognition_service.main \
  --camera-id camera-1 \
  --camera-source http://camera-gateway:4000/streams/1.mjpg \
  --backend-url http://backend:3000
```

### Docker
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

### Docker Compose
```yaml
services:
  recognition-1:
    build: ./recognition_service
    environment:
      - BACKEND_URL=http://backend:3000
      - CAMERA_SOURCE=http://camera-gateway:4000/streams/1.mjpg
      - CAMERA_ID=1
      - SERVICE_NAME=recognition-1
    ports:
      - "5001:5001"
    depends_on:
      - backend
      - camera-gateway
    networks:
      - app-network

  recognition-2:
    build: ./recognition_service
    environment:
      - BACKEND_URL=http://backend:3000
      - CAMERA_SOURCE=http://camera-gateway:4000/streams/2.mjpg
      - CAMERA_ID=2
      - SERVICE_NAME=recognition-2
    ports:
      - "5002:5001"
    depends_on:
      - backend
      - camera-gateway
    networks:
      - app-network
```

## API Endpoints

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "streaming": true,
  "cameraId": "1",
  "service": "recognition"
}
```

### GET /video_feed
MJPEG video stream with face detection visualization.

**Response:**
```
Content-Type: multipart/x-mixed-replace; boundary=frame
```

## Backend Integration

### GET /api/employees
Service expects array of employees with photos.

**Expected Response:**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "role": "Manager",
    "photoUrl": "/uploads/photo-123.jpg"
  }
]
```

### POST /api/events
Service sends presence events.

**Request:**
```json
{
  "employeeId": 1,
  "type": "IN",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## Архитектура

### Основной цикл (video_loop.py)

1. **Initialization**
   - Load employees from backend
   - Build face embeddings
   - Initialize FaceTracker and PresenceManager

2. **Main Loop**
   - Read frame from camera
   - Skip frames according to FRAME_SKIP
   - Detect faces (InsightFace)
   - Quality check (size, blur)
   - Preprocessing (denoise, CLAHE, sharpen)
   - Track faces (IoU matching)
   - Match embeddings
   - Update presence state
   - Send IN/OUT events to backend

3. **Parallel Tasks**
   - Flask server (video streaming)
   - Employee reload (every RELOAD_INTERVAL)
   - Frame updates for streaming

### Quality Pipeline

```
Raw Frame
    ↓
Face Detection (InsightFace)
    ↓
Quality Check (size, blur, brightness)
    ↓ (if acceptable)
Preprocessing (denoise → CLAHE → sharpen)
    ↓
Embedding Extraction
    ↓
Tracking (IoU matching)
    ↓
Recognition (cosine similarity)
    ↓
Presence Logic (IN/OUT thresholds)
    ↓
Event Sending (POST /api/events)
```

## Тестирование

### Unit Tests
```bash
pytest tests/
```

### Integration Tests
```bash
# Start backend mock
python tests/mock_backend.py

# Run service
python -m recognition_service.main

# Check health
curl http://localhost:5001/health

# View stream
curl http://localhost:5001/video_feed > test.mjpg
```

## Troubleshooting

### Camera not connecting
```bash
# Check camera source
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"

# Check RTSP
ffplay rtsp://user:pass@ip:port/path
```

### No faces detected
- Check MIN_FACE_HEIGHT (lower if faces are small)
- Check MIN_BLUR_VAR (lower if images are blurry)
- Enable DEBUG=true for detailed logs

### High CPU usage
- Increase FRAME_SKIP (process fewer frames)
- Disable ENABLE_PREPROCESSING
- Lower insightface_det_size in config.py

### Memory leaks
- Check camera reconnection logic
- Monitor with: `docker stats recognition-1`

## Development

### Adding new features
1. Create module in appropriate directory
2. Import in `__init__.py`
3. Update config.py if new settings needed
4. Add tests in tests/
5. Update README.md

### Code style
```bash
# Format code
black recognition_service/

# Type checking
mypy recognition_service/

# Linting
pylint recognition_service/
```

## License

MIT

## Support

For issues, check logs:
```bash
docker logs recognition-1 -f
```

Common log patterns:
- `[ERROR]` - Critical errors
- `[WARNING]` - Recoverable issues
- `[INFO]` - Normal operation
- `[DEBUG]` - Detailed information









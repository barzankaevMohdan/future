# 🐳 Docker на macOS - Руководство

**Система:** macOS (Intel / M1 / M2)  
**Статус:** ✅ Готово к запуску

---

## 🚀 БЫСТРЫЙ СТАРТ

### Шаг 1: Установите Docker Desktop

Если ещё не установлен:

```bash
# Скачайте с официального сайта:
# https://www.docker.com/products/docker-desktop

# Или через Homebrew:
brew install --cask docker
```

**Запустите Docker Desktop** и дождитесь полного запуска!

### Шаг 2: Запустите систему

```bash
cd /Users/mohdan/Desktop/future
./start-docker.sh
```

**Всё автоматически:**
- Соберёт образы
- Запустит контейнеры
- Откроет браузер

**Откроется:** http://localhost:5173

---

## 📋 КОМАНДЫ ДЛЯ MACOS

| Команда | Что делает |
|---------|------------|
| `./start-docker.sh` | Запустить систему |
| `./stop-docker.sh` | Остановить |
| `./restart-docker.sh` | Перезапустить |
| `./rebuild-docker.sh` | Пересобрать образы |
| `./logs-docker.sh` | Просмотр логов |
| `./check-docker.sh` | Проверить статус |

---

## 📹 ВАЖНО ДЛЯ КАМЕР НА MACOS

### ⚠️ Проблема с локальными камерами

**Docker на macOS не поддерживает `/dev/video0`!**

### ✅ Решения:

**Вариант 1: Используйте RTSP камеру (рекомендую)**

Отредактируйте `docker-compose.yml`:

```yaml
recognition:
  environment:
    - CAMERA_SOURCE=rtsp://admin:admin@192.168.50.235:554/12
```

**Вариант 2: Запустите recognition локально**

```bash
# Остановите Docker recognition
docker-compose stop recognition

# Запустите локально
cd recognition
source venv/bin/activate  
python main.py
```

**Вариант 3: Используйте Docker Desktop камеру (экспериментально)**

Docker Desktop на Apple Silicon может иметь доступ к камере через специальные настройки.

---

## 🏗️ АРХИТЕКТУРА DOCKER

```
┌─────────────────────────────────────┐
│          macOS Host                  │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  Docker Network (bridge)       │ │
│  │                                 │ │
│  │  ┌──────────┐  ┌──────────┐  │ │
│  │  │ backend  │  │ frontend │  │ │
│  │  │  :3000   │  │  :5173   │  │ │
│  │  └──────────┘  └──────────┘  │ │
│  │       ↓              ↓         │ │
│  │  ┌──────────────────────────┐ │ │
│  │  │   recognition :5001      │ │ │
│  │  │   (если RTSP камера)     │ │ │
│  │  └──────────────────────────┘ │ │
│  └─────────────────────────────────┘ │
│                                      │
│  Локально (если веб-камера):        │
│  └─ recognition/main.py             │
└─────────────────────────────────────┘
```

---

## ⚙️ КОНФИГУРАЦИЯ ДЛЯ MACOS

### docker-compose.yml для вашей камеры:

```yaml
recognition:
  environment:
    # Ваша CamHiPro камера
    - CAMERA_SOURCE=rtsp://admin:admin@192.168.50.235:554/12
    - FRAME_SKIP=5
    - MIN_FACE_HEIGHT=80
    - MIN_BLUR_VAR=100
    - ENABLE_PREPROCESSING=true
    - MIN_EMBEDDINGS=3
    - IN_THRESHOLD=2.0
    - OUT_THRESHOLD=5.0
    - VIDEO_PORT=5001
    - STREAM_WIDTH=1280  # Уменьшение разрешения для плавности
    - DEBUG=false
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Тест 1: Проверка Docker

```bash
./check-docker.sh
```

**Должны увидеть:**
```
✅ Docker установлен: Docker version...
✅ Docker запущен
```

### Тест 2: Запуск системы

```bash
./start-docker.sh
```

**При первом запуске:**
- Загрузка базовых образов (~500MB)
- Сборка контейнеров (~5-10 минут)
- Запуск сервисов

**Следующие запуски:**
- Быстрый старт (~30 секунд)

### Тест 3: Проверка логов

```bash
./logs-docker.sh
```

**Должны увидеть:**
```
backend        | Backend listening on http://localhost:3000
frontend       | ➜ Local: http://localhost:5173/
recognition    | [INFO] ✅ InsightFace initialized
```

---

## 🐛 РЕШЕНИЕ ПРОБЛЕМ

### Проблема: "Docker не запущен"

**Решение:**
1. Откройте Docker Desktop
2. Дождитесь зелёного индикатора
3. Запустите `./start-docker.sh`

### Проблема: "Port already in use"

**Решение:**
```bash
# Остановите локальные сервисы
pkill -f "node.*backend"
pkill -f "node.*frontend"  
pkill -f "python.*main.py"

# Затем запустите Docker
./start-docker.sh
```

### Проблема: "Cannot connect to camera"

**macOS не поддерживает `/dev/video0` в Docker!**

**Решение:**
- Используйте RTSP URL в `docker-compose.yml`
- Или запустите recognition локально

### Проблема: Медленная сборка

**Первая сборка долгая! ~10 минут нормально.**

**Ускорить:**
```bash
# Используйте buildkit
export DOCKER_BUILDKIT=1
./rebuild-docker.sh
```

---

## 💡 ОПТИМИЗАЦИЯ ДЛЯ M1/M2

### Если у вас Apple Silicon (M1/M2):

**В docker-compose.yml добавьте:**

```yaml
recognition:
  platform: linux/arm64  # Для M1/M2
```

**Это ускорит работу в 2-3 раза!**

---

## 📊 ИСПОЛЬЗОВАНИЕ РЕСУРСОВ

### Ожидаемая нагрузка на macOS:

```
Docker Desktop: ~500MB RAM
├─ backend: ~100MB RAM
├─ frontend: ~50MB RAM (nginx)
└─ recognition: ~600MB RAM (InsightFace модели)

CPU: 30-50% (в основном recognition)
Диск: ~2GB (образы + volumes)
```

---

## 🎯 РЕКОМЕНДАЦИИ ДЛЯ MACOS

### Вариант 1: Backend + Frontend в Docker, Recognition локально

**Лучшее для macOS с локальной веб-камерой!**

```bash
# 1. Запустите backend и frontend в Docker
docker-compose up backend frontend -d

# 2. Recognition запустите локально
cd recognition
source venv/bin/activate
python main.py
```

**Преимущества:**
- ✅ Доступ к веб-камере MacBook
- ✅ Легко отлаживать
- ✅ Быстрее работает

### Вариант 2: Всё в Docker с RTSP камерой

**Лучшее для офисной IP камеры!**

```bash
# Отредактируйте docker-compose.yml:
# CAMERA_SOURCE=rtsp://admin:admin@192.168.50.235:554/12

./start-docker.sh
```

**Преимущества:**
- ✅ Всё изолировано
- ✅ Легко развернуть
- ✅ Production-like

---

## 📝 ПОЛНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ

### 1. Установка Docker Desktop

```bash
# Скачайте и установите:
# https://www.docker.com/products/docker-desktop

# Или:
brew install --cask docker
```

### 2. Запустите Docker Desktop

**Дождитесь полного запуска** (зелёный кит в трее)

### 3. Настройте камеру

**Отредактируйте `docker-compose.yml`:**

```yaml
recognition:
  environment:
    # Для RTSP камеры:
    - CAMERA_SOURCE=rtsp://admin:admin@192.168.50.235:554/12
    
    # Или для локальной камеры - запустите recognition локально
```

### 4. Запустите систему

```bash
cd /Users/mohdan/Desktop/future
./start-docker.sh
```

### 5. Откройте браузер

http://localhost:5173

**Система работает!** ✅

---

## 🔧 ПОЛЕЗНЫЕ КОМАНДЫ

```bash
# Просмотр логов конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f recognition

# Перезапуск одного сервиса
docker-compose restart backend

# Вход в контейнер
docker-compose exec backend sh
docker-compose exec recognition bash

# Очистка всего
docker-compose down -v  # Удаляет volumes
docker system prune -a  # Очищает всё Docker
```

---

## 🎉 ГОТОВО!

**Shell скрипты для macOS созданы:**
- ✅ `start-docker.sh` - запуск
- ✅ `stop-docker.sh` - остановка
- ✅ `restart-docker.sh` - перезапуск
- ✅ `rebuild-docker.sh` - пересборка
- ✅ `logs-docker.sh` - логи
- ✅ `check-docker.sh` - статус

**Docker-compose адаптирован для macOS!**

---

## 🚀 ЗАПУСТИТЕ!

```bash
cd /Users/mohdan/Desktop/future
./start-docker.sh
```

**Первый запуск займёт ~10 минут (сборка образов)**  
**Следующие запуски ~30 секунд**

---

**ПОПРОБУЙТЕ ПРЯМО СЕЙЧАС!** 🐳✨

```bash
./start-docker.sh
```


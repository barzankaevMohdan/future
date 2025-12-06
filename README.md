# Face Recognition Attendance Platform

Платформа учета посещаемости с распознаванием лиц на основе микросервисной архитектуры.

## 📖 Инструкции по установке

Выберите инструкцию для вашей операционной системы:

- **[Windows](./SETUP_WINDOWS.md)** — Подробная инструкция для Windows 10/11
- **[macOS](./SETUP_MACOS.md)** — Подробная инструкция для macOS

---

## 🏗️ Архитектура проекта

| Путь | Описание |
| --- | --- |
| `backend/` | Основной API (Node.js + Express + Prisma + PostgreSQL + Socket.IO) |
| `camera-gateway/` | RTSP → MJPEG шлюз (Node.js + FFmpeg, общая Prisma-схема) |
| `admin-frontend/` | SPA для SUPERADMIN / COMPANY_ADMIN (Vue 3 + Vite + Pinia) |
| `client-frontend/` | SPA для пользовательских ролей |
| `infra/` | Docker Compose для PostgreSQL |
| `recognition_service/` | Python сервис распознавания лиц (InsightFace + OpenCV) |

## Архитектура

- **PostgreSQL** — единый источник данных.
- **Backend** — аутентификация (JWT), мульти-компании, сотрудники, камеры, события IN/OUT, presence/analytics, realtime через Socket.IO.
- **Camera Gateway** — подключается к `Camera` таблице через Prisma, расшифровывает `passwordEnc` тем же `ENCRYPTION_KEY`, поднимает ffmpeg процесс на камеру, раздает `/streams/:cameraId.mjpg`, поддерживает health/preview.
- **Frontends** — работают с backend API + MJPEG потоками, используют axios/interceptors и live-ивенты.
- **Python recognition** — отдельный репозиторий, интегрируется по публичным эндпоинтам backend (`/api/employees`, `/api/events`), берёт MJPEG из camera-gateway.

## 🚀 Быстрый старт

### 1. Запуск PostgreSQL через Docker

```bash
cd infra
docker compose up -d
```

Это запустит только PostgreSQL базу данных на порту `5432`.

### 2. Запуск сервисов локально

Все остальные сервисы (Backend, Camera Gateway, Frontend'ы, Recognition Service) запускаются локально.

**Подробные инструкции:**
- **[Windows](./SETUP_WINDOWS.md)**
- **[macOS](./SETUP_MACOS.md)**

### 3. Доступ к приложению

После запуска всех сервисов:

- **Admin Panel** — http://localhost:8080 (или другой порт Vite)
- **Client App** — http://localhost:8081 (или другой порт Vite)
- **Backend API** — http://localhost:3000
- **Camera Gateway** — http://localhost:4000
- **Recognition Service** — http://localhost:5001 (для каждой камеры)

## ⚙️ Настройка окружения

Каждый сервис имеет файл `env.example`, который нужно скопировать в `.env` и заполнить.

### Backend (`backend/.env`)
```env
DATABASE_URL=postgresql://attendance_user:secure_password_change_me@localhost:5432/attendance
JWT_ACCESS_SECRET=your-secret-access-key-change-me
JWT_REFRESH_SECRET=your-secret-refresh-key-change-me
ENCRYPTION_KEY=your-32-character-encryption-key  # общий для backend и camera-gateway
PUBLIC_COMPANY_SLUG=demo-company
CAMERA_GATEWAY_PUBLIC_URL=http://localhost:4000
CAMERA_GATEWAY_INTERNAL_URL=http://localhost:4000
```

### Camera Gateway (`camera-gateway/.env`)
```env
DATABASE_URL=postgresql://attendance_user:secure_password_change_me@localhost:5432/attendance
FFMPEG_PATH=ffmpeg
ENCRYPTION_KEY=your-32-character-encryption-key  # тот же, что и в backend
```

### Frontend (`admin-frontend/.env` и `client-frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:3000
```

## 🔐 Тестовые учетные записи

После выполнения `npm run prisma:seed` в backend создаются:

- **SUPERADMIN** — `superadmin@system.com / SuperAdmin123!`
- **COMPANY_ADMIN** — `admin@demo.com / Admin123!`
- **USER** — `user@demo.com / User123!`

Используйте эти учетные данные для первого входа в систему.

## 🤖 Интеграция Python Recognition Service

Recognition Service работает независимо для каждой камеры и использует публичные эндпоинты backend.

### Запуск Recognition Service

```bash
cd recognition_service
source .venv/bin/activate  # для macOS/Linux
# или
.\.venv\Scripts\Activate.ps1  # для Windows

python -m recognition_service.main \
  --camera-source "http://localhost:4000/streams/1.mjpg" \
  --camera-id "1" \
  --backend-url "http://localhost:3000"
```

Для каждой камеры нужен **отдельный экземпляр** Recognition Service с разными:
- `--camera-id` (ID камеры из базы данных)
- `--camera-source` (URL MJPEG-потока)
- `--video-port` (порт для отладочного видео, по умолчанию 5001)

### Backend API для Recognition Service

#### `GET /api/employees`
Возвращает массив сотрудников (публичный эндпоинт, без токена):
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "role": "Manager",
    "photoUrl": "/uploads/employees/photo-123.jpg"
  }
]
```

#### `POST /api/events`
Создает событие входа/выхода:
```json
{
  "employeeId": 1,
  "type": "IN",
  "timestamp": "2025-01-01T08:00:00.000Z"
}
```

Ответ: `{ "ok": true }` или `{ "ok": true, "skipped": true }` (если дубликат < 60 сек).

## 📹 Camera Gateway

Шлюз для конвертации RTSP-потоков камер в MJPEG для браузеров и Recognition Service.

**Порт:** `4000`

**Функции:**
- Читает камеры из PostgreSQL через Prisma (общая схема с backend)
- Расшифровывает пароли камер (`ENCRYPTION_KEY`)
- Конвертирует RTSP → MJPEG через FFmpeg

**API:**
- `GET /api/health` — статус сервиса
- `GET /api/cameras` — список камер (read-only)
- `POST /api/cameras/:id/preview` — быстрый тест RTSP (используется backend'ом)
- `GET /streams/:id.mjpg` — MJPEG поток камеры

**Использование:**
```bash
# Получить URL потока через backend
GET /api/cameras/:id/stream-url
# Вернет: { "mjpegUrl": "http://localhost:4000/streams/1.mjpg" }

# Прямой доступ к потоку
http://localhost:4000/streams/1.mjpg
```

## 🔌 Backend API

**Порт:** `3000`

**Основные модули:**
- **Auth** — `/api/auth/login`, `/api/auth/refresh` (JWT access/refresh tokens)
- **Companies** — `/api/companies` (мультитенантность)
- **Users** — `/api/users` (управление пользователями)
- **Employees** — `/api/employees` (сотрудники с фотографиями)
- **Cameras** — `/api/cameras` (управление камерами)
- **Events** — `/api/events` (события входа/выхода)
- **Presence** — `/api/presence` (текущее присутствие)
- **Statistics** — `/api/statistics` (аналитика посещаемости)
- **Metrics** — `/api/metrics` (метрики системы)

**Real-time события (Socket.IO):**
- Подключение: `http://localhost:3000` (Socket.IO Client)
- События: `event:created`, `employee:created`, `employee:updated`, `employee:deleted`

## 🎨 Frontend Applications

### Admin Frontend (порт 8080 или Vite auto)
**Роли:** SUPERADMIN, COMPANY_ADMIN

**Страницы:**
- Dashboard — общая статистика
- Companies — управление компаниями (только SUPERADMIN)
- Employees — управление сотрудниками
- Cameras — управление камерами
- Events — журнал событий
- Presence — текущее присутствие
- Statistics — аналитика
- Live — просмотр камер в реальном времени

### Client Frontend (порт 8081 или Vite auto)
**Роли:** Все роли

**Страницы:**
- Dashboard — общая статистика
- Events — журнал событий
- Presence — текущее присутствие
- Statistics — аналитика
- Live — просмотр камер

## 📦 NPM Scripts

### Backend
```bash
npm run dev              # Запуск в режиме разработки
npm run build            # Сборка TypeScript
npm run start            # Запуск production сборки
npm run prisma:generate  # Генерация Prisma Client
npm run prisma:migrate   # Применение миграций
npm run prisma:seed      # Заполнение тестовыми данными
```

### Camera Gateway
```bash
npm run dev                  # Запуск в режиме разработки
npm run build                # Сборка TypeScript
npm run start                # Запуск production сборки
npm run prisma:copy-schema   # Копирование схемы из backend
npm run prisma:generate      # Генерация Prisma Client
```

### Frontends
```bash
npm run dev      # Запуск dev сервера (Vite)
npm run build    # Сборка для production
npm run preview  # Предпросмотр production сборки
```

## 🛠️ Разработка

### Требования
- **Node.js** 18+ или 20+
- **Python** 3.10 или 3.11
- **Docker** (для PostgreSQL)
- **FFmpeg** (для Camera Gateway)

### Структура проекта
```
future/
├── backend/              # Node.js API
├── camera-gateway/       # RTSP → MJPEG конвертер
├── admin-frontend/       # Vue 3 SPA для админов
├── client-frontend/      # Vue 3 SPA для пользователей
├── recognition_service/  # Python распознавание лиц
├── infra/               # Docker Compose для PostgreSQL
├── SETUP_WINDOWS.md     # Инструкция для Windows
├── SETUP_MACOS.md       # Инструкция для macOS
└── README.md            # Этот файл
```

---

## 📄 Лицензия

Проприетарное программное обеспечение. Все права защищены.

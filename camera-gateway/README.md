# Camera Gateway

RTSP → MJPEG шлюз, который подключается к общей базе PostgreSQL (Prisma) и раздаёт нормализованные потоки для веб-клиентов и Python recognition-service.

## Возможности

- Подключение к таблице `Camera` из основного backend'а через Prisma
- Один процесс `ffmpeg` на камеру, много подписчиков
- Автоостановка при отсутствии клиентов и защита от цикличных рестартов
- REST-эндпоинты только для чтения (health, список камер, предпросмотр)
- Тест соединения с камерой (пробрасывается в backend для кнопки «проверить поток»)

## Быстрый старт

```bash
cd camera-gateway
npm install
npm run prisma:generate   # копирует схему из backend и генерирует клиент
npm run dev
```

## Переменные окружения

См. `env.example`. Критичные значения:

- `DATABASE_URL` — общий Postgres (тот же, что у backend)
- `ENCRYPTION_KEY` — тот же ключ, что использует backend для `Camera.passwordEnc`
- `FFMPEG_PATH` — путь к системному ffmpeg

## API

| Метод | Путь | Описание |
| --- | --- | --- |
| `GET` | `/api/health` | Проверка живости + соединение с Postgres |
| `GET` | `/api/cameras` | Список активных камер (read-only, без паролей) |
| `GET` | `/api/cameras/:id` | Информация по конкретной камере |
| `POST` | `/api/cameras/:id/preview` | Быстрый тест RTSP (использует ffmpeg `-frames 1`) |
| `GET` | `/streams/:id.mjpg` | Основной MJPEG поток |

## Интеграция с backend

- Backend отвечает за CRUD камер и хранение паролей (`passwordEnc`)
- Gateway только читает `Camera` записи и использует тот же `ENCRYPTION_KEY`
- Backend получает `mjpegUrl` через `CAMERA_GATEWAY_PUBLIC_URL` и отдаёт на фронт
- Для кнопки «RTSP preview» backend делает `POST http://camera-gateway:4000/api/cameras/:id/preview`

## Docker

Сервис собран так, чтобы работать в `infra/docker-compose.yml`:

```yaml
camera-gateway:
  build: ../camera-gateway
  environment:
    - DATABASE_URL=postgresql://...
    - ENCRYPTION_KEY=...
    - PORT=4000
  depends_on:
    - postgres
```

## Примечания

- Prisma-схема единая и лежит в `backend/prisma/schema.prisma`. Скрипт `npm run prisma:copy-schema` копирует её сюда перед генерацией.
- В логах никогда не выводится пароль камеры (используем safe RTSP URL).
- При отсутствии клиентов поток гасится через `STREAM_IDLE_TIMEOUT_MS` (по умолчанию 15c).


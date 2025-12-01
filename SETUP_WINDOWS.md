# 🚀 Инструкция по запуску проекта на Windows

Данная инструкция поможет вам настроить и запустить систему учета посещаемости с распознаванием лиц на Windows.

---

## 📋 Требования

### 1. Node.js и npm
**Версия:** Node.js 18.x или выше

**Скачать:**
- [Node.js 18 LTS](https://nodejs.org/en/download/) (рекомендуется)
- [Node.js 20 LTS](https://nodejs.org/en/download/) (актуальная версия)

**Проверка установки:**
```powershell
node --version
npm --version
```

---

### 2. Python
**Версия:** Python 3.10 или 3.11 (рекомендуется 3.10)

> ⚠️ **Важно:** Python 3.12+ не рекомендуется из-за проблем совместимости с некоторыми библиотеками (dlib, opencv).

**Скачать:**
- [Python 3.10.11](https://www.python.org/downloads/release/python-31011/)
- [Python 3.11.9](https://www.python.org/downloads/release/python-3119/)

**При установке:**
- ✅ Обязательно установите галочку **"Add Python to PATH"**
- ✅ Выберите **"Install for all users"** (опционально)

**Проверка установки:**
```powershell
python --version
pip --version
```

---

### 3. Docker Desktop
**Для запуска PostgreSQL базы данных**

**Скачать:**
- [Docker Desktop для Windows](https://www.docker.com/products/docker-desktop/)

**После установки:**
1. Запустите Docker Desktop
2. Дождитесь полной загрузки (статус должен быть зеленым)

**Проверка установки:**
```powershell
docker --version
docker ps
```

---

### 4. FFmpeg
**Для обработки видеопотоков с камер**

#### Вариант 1: Установка через Chocolatey (рекомендуется)

1. Установите Chocolatey (если еще не установлен):
```powershell
# Запустите PowerShell от имени администратора
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

2. Установите FFmpeg:
```powershell
choco install ffmpeg -y
```

#### Вариант 2: Ручная установка

1. Скачайте [FFmpeg для Windows](https://www.gyan.dev/ffmpeg/builds/)
2. Распакуйте архив (например, в `C:\ffmpeg`)
3. Добавьте в PATH:
   - Откройте **Панель управления** → **Система** → **Дополнительные параметры системы**
   - Нажмите **Переменные среды**
   - В разделе **Системные переменные** найдите `Path` и нажмите **Изменить**
   - Добавьте путь к папке `bin` (например, `C:\ffmpeg\bin`)

**Проверка установки:**
```powershell
ffmpeg -version
```

---

### 5. Git
**Для клонирования репозитория**

**Скачать:**
- [Git для Windows](https://git-scm.com/download/win)

**Проверка установки:**
```powershell
git --version
```

---

### 6. Visual Studio Build Tools (для Python пакетов)
**Необходимы для компиляции dlib и других пакетов**

**Скачать:**
- [Visual Studio Build Tools 2022](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)

**При установке выберите:**
- ✅ **Desktop development with C++**
- ✅ **MSVC v143** (или новее)
- ✅ **Windows 10/11 SDK**

---

## 🔧 Установка и настройка

### Шаг 1: Клонирование репозитория

```powershell
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
cd future
```

---

### Шаг 2: Запуск PostgreSQL через Docker

```powershell
cd infra
docker run -d `
  --name attendance-postgres `
  -p 5432:5432 `
  -e POSTGRES_DB=attendance `
  -e POSTGRES_USER=attendance_user `
  -e POSTGRES_PASSWORD=secure_password_change_me `
  -v pgdata-attendance:/var/lib/postgresql/data `
  postgres:15-alpine
```

**Или используйте docker-compose:**
```powershell
docker compose up -d
```

**Проверка:**
```powershell
docker ps
# Вы должны увидеть контейнер attendance-postgres
```

---

### Шаг 3: Настройка Backend

```powershell
cd ..\backend
```

#### 3.1 Установка зависимостей
```powershell
npm install
```

#### 3.2 Настройка переменных окружения
Создайте файл `.env` на основе `env.example`:
```powershell
copy env.example .env
```

Откройте `.env` и укажите:
```env
PORT=3000
NODE_ENV=development
DATABASE_URL=postgresql://attendance_user:secure_password_change_me@localhost:5432/attendance
JWT_ACCESS_SECRET=your-secret-access-key-change-me
JWT_REFRESH_SECRET=your-secret-refresh-key-change-me
ENCRYPTION_KEY=your-32-character-encryption-key
CORS_ORIGIN=*
CAMERA_GATEWAY_PUBLIC_URL=http://localhost:4000
CAMERA_GATEWAY_INTERNAL_URL=http://localhost:4000
PUBLIC_COMPANY_SLUG=demo-company
```

#### 3.3 Инициализация базы данных
```powershell
npm run prisma:migrate
npm run prisma:seed
```

---

### Шаг 4: Настройка Camera Gateway

```powershell
cd ..\camera-gateway
```

#### 4.1 Установка зависимостей
```powershell
npm install
```

#### 4.2 Настройка переменных окружения
```powershell
copy env.example .env
```

Откройте `.env` и укажите:
```env
PORT=4000
NODE_ENV=development
DATABASE_URL=postgresql://attendance_user:secure_password_change_me@localhost:5432/attendance
FFMPEG_PATH=ffmpeg
ENCRYPTION_KEY=your-32-character-encryption-key
```

> ⚠️ `ENCRYPTION_KEY` должен быть таким же, как в backend!

#### 4.3 Копирование Prisma схемы
```powershell
npm run prisma:copy-schema
npm run prisma:generate
```

---

### Шаг 5: Настройка Admin Frontend

```powershell
cd ..\admin-frontend
```

#### 5.1 Установка зависимостей
```powershell
npm install
```

#### 5.2 Настройка переменных окружения
```powershell
copy env.example .env
```

Откройте `.env`:
```env
VITE_API_BASE_URL=http://localhost:3000
```

---

### Шаг 6: Настройка Client Frontend

```powershell
cd ..\client-frontend
```

#### 6.1 Установка зависимостей
```powershell
npm install
```

#### 6.2 Настройка переменных окружения
```powershell
copy env.example .env
```

Откройте `.env`:
```env
VITE_API_BASE_URL=http://localhost:3000
```

---

### Шаг 7: Настройка Recognition Service (Python)

```powershell
cd ..\recognition_service
```

#### 7.1 Создание виртуального окружения
```powershell
python -m venv .venv
```

#### 7.2 Активация виртуального окружения
```powershell
.\.venv\Scripts\Activate.ps1
```

> 💡 Если возникает ошибка "Запуск сценариев отключен", выполните:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 7.3 Установка зависимостей
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

> ⚠️ Установка может занять 5-10 минут. Некоторые пакеты (dlib, opencv) требуют компиляции.

---

## ▶️ Запуск приложения

Откройте **5 отдельных окон PowerShell** для каждого сервиса:

### Терминал 1: Backend
```powershell
cd C:\путь\к\проекту\future\backend
npm run dev
```
Сервис доступен на: `http://localhost:3000`

---

### Терминал 2: Camera Gateway
```powershell
cd C:\путь\к\проекту\future\camera-gateway
npm run dev
```
Сервис доступен на: `http://localhost:4000`

---

### Терминал 3: Admin Frontend
```powershell
cd C:\путь\к\проекту\future\admin-frontend
npm run dev -- --host 127.0.0.1 --port 8080
```
Интерфейс доступен на: `http://localhost:8080`

---

### Терминал 4: Client Frontend
```powershell
cd C:\путь\к\проекту\future\client-frontend
npm run dev -- --host 127.0.0.1 --port 8081
```
Интерфейс доступен на: `http://localhost:8081`

---

### Терминал 5: Recognition Service (Python)

```powershell
cd C:\путь\к\проекту\future
.\recognition_service\.venv\Scripts\Activate.ps1
python -m recognition_service.main `
  --company-slug "demo-company" `
  --backend-url "http://localhost:3000" `
  --refresh-interval 60
```

**Что происходит:**
- ✅ Автоматически обрабатывает все активные камеры компании
- ✅ При добавлении новой камеры через админку она автоматически начнет обрабатываться в течение 60 секунд
- ✅ Каждая камера обрабатывается в отдельном потоке
- ✅ Общий кэш InsightFace модели и эмбеддингов для всех камер

**Отладочное видео:**
- Камера 1: `http://localhost:5001/video_feed`
- Камера 2: `http://localhost:5002/video_feed`
- Камера N: `http://localhost:500N/video_feed`

---

## 🔐 Первый вход

### Админ-панель (http://localhost:8080)

**Суперадмин:**
- Email: `superadmin@system.com`
- Пароль: `SuperAdmin123!`

**Админ компании:**
- Email: `admin@demo.com`
- Пароль: `Admin123!`

### Клиентская панель (http://localhost:8081)

Используйте те же учетные данные.

---

## 📹 Добавление камеры

1. Войдите в админ-панель как **Админ компании** (`admin@demo.com`)
2. Перейдите в раздел **Камеры**
3. Нажмите **Добавить камеру**
4. Заполните форму:
   - **Название:** Например, "Вход в офис"
   - **IP адрес:** `192.168.1.10`
   - **Порт RTSP:** `554` (по умолчанию)
   - **Имя пользователя:** `admin`
   - **Пароль:** `your_camera_password`
   - **RTSP путь:** `/ISAPI/Streaming/Channels/101` (для Hikvision)
   - **Статус:** Активна ✅
   - **Распознавание включено:** Да ✅
5. Нажмите **Сохранить**

**Что происходит дальше:**
- ✅ Видеопоток становится доступен: `http://localhost:4000/streams/{camera_id}.mjpg`
- ✅ В течение 1 минуты Recognition Service автоматически начнет обрабатывать камеру (если запущен в multi-camera режиме)
- ✅ События распознавания будут появляться в разделе **События**

> 💡 **Совет:** В разделе **Live** можно проверить, что видео с камеры отображается корректно

---

## 🛠️ Полезные команды

### База данных
```powershell
# Остановить PostgreSQL
docker stop attendance-postgres

# Запустить PostgreSQL
docker start attendance-postgres

# Пересоздать базу данных
cd backend
npm run prisma:migrate:reset
npm run prisma:seed
```

### Обновление зависимостей
```powershell
# Backend
cd backend
npm install

# Camera Gateway
cd camera-gateway
npm run prisma:copy-schema
npm install

# Recognition Service
cd recognition_service
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Очистка
```powershell
# Очистка node_modules
npm run clean  # в каждом Node.js проекте

# Очистка Python кэша
cd recognition_service
deactivate
rmdir /s /q .venv
python -m venv .venv
```

---

## 🐛 Решение проблем

### Ошибка: "Cannot connect to database"
- Убедитесь, что Docker контейнер с PostgreSQL запущен: `docker ps`
- Проверьте `DATABASE_URL` в `.env` файлах

### Ошибка: "ffmpeg not found"
- Убедитесь, что FFmpeg установлен: `ffmpeg -version`
- Проверьте, что путь к FFmpeg добавлен в PATH
- Перезапустите PowerShell после установки FFmpeg

### Ошибка: "Failed to open camera"
- Убедитесь, что camera-gateway запущен и доступен
- Проверьте URL камеры: откройте в браузере `http://localhost:4000/streams/1.mjpg`
- Проверьте, что RTSP-поток камеры работает (используйте VLC)

### Ошибка при установке Python пакетов
- Убедитесь, что установлены Visual Studio Build Tools
- Попробуйте установить пакеты по одному:
  ```powershell
  pip install numpy==1.24.3
  pip install opencv-python-headless==4.5.5.64
  pip install dlib
  ```

### Порт уже занят
```powershell
# Найти процесс на порту (например, 3000)
netstat -ano | findstr :3000

# Завершить процесс по PID
taskkill /PID <PID> /F
```

---

## 📚 Дополнительные ресурсы

- [Node.js документация](https://nodejs.org/docs/)
- [Python документация](https://docs.python.org/3/)
- [Docker документация](https://docs.docker.com/)
- [FFmpeg документация](https://ffmpeg.org/documentation.html)
- [Prisma документация](https://www.prisma.io/docs/)
- [Vue.js документация](https://vuejs.org/guide/)

---

## 💡 Советы

1. **Используйте PowerShell 7** (а не Windows PowerShell 5.1) для лучшей совместимости
2. **Добавьте `.venv` и `node_modules` в исключения антивируса** для ускорения работы
3. **Используйте VSCode** с расширениями:
   - ESLint
   - Prettier
   - Python
   - Prisma
   - Vue Language Features (Volar)

---

Если возникли проблемы, откройте Issue в репозитории проекта! 🚀


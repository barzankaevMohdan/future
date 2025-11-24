@echo off
echo ========================================
echo Cafe Face Recognition System - Docker
echo ========================================
echo.

REM Проверка установки Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker не установлен!
    echo Пожалуйста, установите Docker Desktop для Windows:
    echo https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [INFO] Docker обнаружен
echo.

REM Проверка запущен ли Docker
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker не запущен!
    echo Пожалуйста, запустите Docker Desktop и попробуйте снова.
    pause
    exit /b 1
)

echo [INFO] Docker запущен
echo.

REM Останавливаем старые контейнеры если есть
echo [INFO] Останавливаем старые контейнеры...
docker-compose -f docker-compose.windows.yml down

echo.
echo [INFO] Собираем и запускаем контейнеры...
echo Это может занять несколько минут при первом запуске...
echo.

REM Запускаем docker-compose
docker-compose -f docker-compose.windows.yml up --build -d

if errorlevel 1 (
    echo.
    echo [ERROR] Не удалось запустить контейнеры!
    echo Проверьте логи выше для деталей.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] Все сервисы запущены!
echo ========================================
echo.
echo Доступные сервисы:
echo   - Frontend:  http://localhost:5173
echo   - Backend:   http://localhost:3000
echo   - Video:     http://localhost:5001/video_feed
echo.
echo Для просмотра логов:
echo   docker-compose -f docker-compose.windows.yml logs -f
echo.
echo Для остановки:
echo   docker-compose -f docker-compose.windows.yml down
echo.
echo ========================================

REM Открываем браузер
timeout /t 3 /nobreak >nul
start http://localhost:5173

pause


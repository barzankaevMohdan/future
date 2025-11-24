@echo off
chcp 65001 >nul
echo ════════════════════════════════════════════════════════════════
echo Исправление проблем со сборкой Docker
echo ════════════════════════════════════════════════════════════════
echo.

echo [1/4] Очистка Docker кеша...
docker builder prune -f
echo ✅ Кеш очищен
echo.

echo [2/4] Остановка контейнеров...
docker-compose -f docker-compose.windows.yml down
echo ✅ Контейнеры остановлены
echo.

echo [3/4] Проверка интернета...
ping -n 1 8.8.8.8 >nul
if errorlevel 1 (
    echo ❌ Нет подключения к интернету!
    pause
    exit /b 1
) else (
    echo ✅ Интернет подключен
)
echo.

echo [4/4] Сборка образов...
echo Это может занять 5-10 минут...
echo.
docker-compose -f docker-compose.windows.yml build --no-cache

if errorlevel 1 (
    echo.
    echo ❌ Сборка не удалась!
    echo.
    echo Попробуйте:
    echo 1. Перезагрузить Docker Desktop
    echo 2. Перезагрузить компьютер
    echo 3. Проверить интернет соединение
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Сборка завершена!
echo.
echo Запуск контейнеров...
docker-compose -f docker-compose.windows.yml up -d

echo.
echo ════════════════════════════════════════════════════════════════
echo ✅ ГОТОВО!
echo ════════════════════════════════════════════════════════════════
echo.
echo Сервисы доступны:
echo   - Frontend:  http://localhost:5173
echo   - Backend:   http://localhost:3000
echo   - Video:     http://localhost:5001/video_feed
echo.
timeout /t 3 /nobreak >nul
start http://localhost:5173
echo.
pause

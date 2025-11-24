@echo off
echo ========================================
echo Перезапуск контейнеров
echo ========================================
echo.

echo [INFO] Перезапуск всех сервисов...
docker-compose -f docker-compose.windows.yml restart

if errorlevel 1 (
    echo.
    echo [ERROR] Не удалось перезапустить контейнеры!
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Контейнеры перезапущены!
echo.
echo Сервисы доступны:
echo   - Frontend:  http://localhost:5173
echo   - Backend:   http://localhost:3000
echo   - Video:     http://localhost:5001/video_feed
echo.
pause


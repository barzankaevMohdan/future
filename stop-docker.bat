@echo off
echo ========================================
echo Остановка Cafe Face Recognition System
echo ========================================
echo.

docker-compose -f docker-compose.windows.yml down

echo.
echo [INFO] Все контейнеры остановлены
echo.
pause


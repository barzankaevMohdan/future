@echo off
echo ========================================
echo Логи Cafe Face Recognition System
echo ========================================
echo.
echo Нажмите Ctrl+C для выхода
echo.

docker-compose -f docker-compose.windows.yml logs -f


@echo off
echo ========================================
echo Пересборка контейнеров
echo ========================================
echo.

echo [INFO] Останавливаем контейнеры...
docker-compose -f docker-compose.windows.yml down

echo.
echo [INFO] Удаляем старые образы...
docker-compose -f docker-compose.windows.yml rm -f

echo.
echo [INFO] Пересобираем образы...
docker-compose -f docker-compose.windows.yml build --no-cache

echo.
echo [INFO] Запускаем контейнеры...
docker-compose -f docker-compose.windows.yml up -d

echo.
echo [SUCCESS] Пересборка завершена!
echo.
pause


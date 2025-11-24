@echo off
echo ========================================
echo Проверка Docker установки
echo ========================================
echo.

echo [1] Проверка Docker...
docker --version
if errorlevel 1 (
    echo [ERROR] Docker не установлен!
    goto :end
) else (
    echo [OK] Docker установлен
)

echo.
echo [2] Проверка Docker Compose...
docker-compose --version
if errorlevel 1 (
    echo [ERROR] Docker Compose не установлен!
    goto :end
) else (
    echo [OK] Docker Compose установлен
)

echo.
echo [3] Проверка запущен ли Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker не запущен!
    echo Запустите Docker Desktop и попробуйте снова.
    goto :end
) else (
    echo [OK] Docker запущен
)

echo.
echo [4] Проверка контейнеров...
docker ps --filter "name=cafeface" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo [5] Проверка volumes...
docker volume ls --filter "name=future"

echo.
echo ========================================
echo Проверка завершена!
echo ========================================

:end
echo.
pause


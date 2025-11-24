@echo off
echo ========================================
echo Резервное копирование данных
echo ========================================
echo.

REM Создаём директорию для бэкапов с датой
set BACKUP_DIR=backups\backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir "%BACKUP_DIR%" 2>nul

echo [INFO] Создание бэкапа в %BACKUP_DIR%...
echo.

REM Проверяем, запущен ли контейнер backend
docker ps --filter "name=cafeface-backend" --format "{{.Names}}" | findstr cafeface-backend >nul
if errorlevel 1 (
    echo [ERROR] Контейнер cafeface-backend не запущен!
    echo Запустите контейнеры перед созданием бэкапа.
    pause
    exit /b 1
)

echo [1/2] Копирование базы данных...
docker cp cafeface-backend:/app/db.sqlite "%BACKUP_DIR%\db.sqlite"
if errorlevel 1 (
    echo [ERROR] Не удалось скопировать базу данных
) else (
    echo [OK] База данных скопирована
)

echo.
echo [2/2] Копирование фотографий...
docker cp cafeface-backend:/app/uploads "%BACKUP_DIR%\uploads"
if errorlevel 1 (
    echo [ERROR] Не удалось скопировать фотографии
) else (
    echo [OK] Фотографии скопированы
)

echo.
echo ========================================
echo [SUCCESS] Бэкап создан: %BACKUP_DIR%
echo ========================================
echo.
pause


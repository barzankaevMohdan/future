@echo off
echo ========================================
echo Настройка IP-камеры
echo ========================================
echo.
echo Этот скрипт поможет настроить IP-камеру для Docker
echo.
echo Варианты подключения камеры:
echo.
echo 1. IP Webcam (Android приложение)
echo    - Установите "IP Webcam" из Google Play
echo    - Запустите приложение и нажмите "Start server"
echo    - Используйте адрес: http://192.168.X.X:8080/video
echo.
echo 2. RTSP камера
echo    - Используйте: rtsp://username:password@192.168.X.X:554/stream
echo.
echo 3. HTTP поток
echo    - Используйте: http://192.168.X.X:port/video
echo.
echo ========================================
echo.

set /p CAMERA_URL="Введите URL камеры (или нажмите Enter для пропуска): "

if "%CAMERA_URL%"=="" (
    echo.
    echo [INFO] URL не указан, используется значение по умолчанию (0)
    echo.
    pause
    exit /b 0
)

echo.
echo [INFO] Обновление docker-compose.windows.yml...

REM Создаём временный файл
set TEMP_FILE=docker-compose.windows.tmp

REM Заменяем CAMERA_SOURCE в файле
powershell -Command "(Get-Content docker-compose.windows.yml) -replace '- CAMERA_SOURCE=.*', '- CAMERA_SOURCE=%CAMERA_URL%' | Set-Content %TEMP_FILE%"

REM Заменяем оригинальный файл
move /y %TEMP_FILE% docker-compose.windows.yml >nul

echo [OK] Конфигурация обновлена!
echo.
echo Новый URL камеры: %CAMERA_URL%
echo.
echo Теперь запустите контейнеры:
echo   start-docker.bat
echo.
echo Или пересоберите если они уже запущены:
echo   rebuild-docker.bat
echo.
pause


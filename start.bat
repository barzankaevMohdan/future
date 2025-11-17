@echo off
REM Скрипт для запуска всех компонентов системы на Windows

echo 🚀 Запуск Cafe Face Presence System...

REM Проверка зависимостей backend
if not exist "backend\node_modules\" (
    echo 📦 Установка backend зависимостей...
    cd backend
    call npm install
    cd ..
)

REM Проверка зависимостей frontend
if not exist "frontend\node_modules\" (
    echo 📦 Установка frontend зависимостей...
    cd frontend
    call npm install
    cd ..
)

REM Проверка Python venv
if not exist "recognition\venv\" (
    echo 📦 Создание Python virtual environment...
    cd recognition
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    cd ..
)

echo ✅ Все зависимости установлены
echo.

REM Запуск всех сервисов
echo 🔧 Запуск Backend...
start "Backend" cmd /k "cd backend && npm start"

timeout /t 2 /nobreak >nul

echo 🎨 Запуск Frontend...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo 🤖 Запуск Recognition Service...
start "Recognition" cmd /k "cd recognition && venv\Scripts\activate.bat && python main.py"

echo.
echo ✅ Все сервисы запущены!
echo Backend: http://localhost:3000
echo Frontend: http://localhost:5173
echo Recognition: работает в фоне
echo.
echo Закройте окна терминалов для остановки сервисов
pause


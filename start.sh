#!/bin/bash

# Скрипт для запуска всех компонентов системы
echo "🚀 Запуск Cafe Face Presence System..."

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция для проверки установки зависимостей
check_dependencies() {
    echo -e "${BLUE}📦 Проверка зависимостей...${NC}"
    
    # Проверка Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js не установлен${NC}"
        exit 1
    fi
    
    # Проверка Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 не установлен${NC}"
        exit 1
    fi
    
    # Проверка backend зависимостей
    if [ ! -d "backend/node_modules" ]; then
        echo -e "${BLUE}📦 Установка backend зависимостей...${NC}"
        cd backend && npm install && cd ..
    fi
    
    # Проверка frontend зависимостей
    if [ ! -d "frontend/node_modules" ]; then
        echo -e "${BLUE}📦 Установка frontend зависимостей...${NC}"
        cd frontend && npm install && cd ..
    fi
    
    # Проверка Python venv
    if [ ! -d "recognition/venv" ]; then
        echo -e "${BLUE}📦 Создание Python virtual environment...${NC}"
        cd recognition && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && cd ..
    fi
    
    echo -e "${GREEN}✅ Все зависимости установлены${NC}"
}

# Проверка зависимостей
check_dependencies

# Функция для остановки всех процессов при выходе
cleanup() {
    echo -e "\n${RED}🛑 Остановка всех сервисов...${NC}"
    kill 0
    exit 0
}

trap cleanup SIGINT SIGTERM

# Запуск backend
echo -e "${BLUE}🔧 Запуск Backend...${NC}"
cd backend && npm start &
BACKEND_PID=$!

# Небольшая задержка для запуска backend
sleep 2

# Запуск frontend
echo -e "${MAGENTA}🎨 Запуск Frontend...${NC}"
cd frontend && npm run dev &
FRONTEND_PID=$!

# Запуск recognition
echo -e "${GREEN}🤖 Запуск Recognition Service...${NC}"
cd recognition && source venv/bin/activate && python main.py &
RECOGNITION_PID=$!

echo -e "\n${GREEN}✅ Все сервисы запущены!${NC}"
echo -e "${BLUE}Backend:${NC} http://localhost:3000"
echo -e "${MAGENTA}Frontend:${NC} http://localhost:5173"
echo -e "${GREEN}Recognition:${NC} работает в фоне"
echo -e "\n${RED}Нажмите Ctrl+C для остановки всех сервисов${NC}\n"

# Ожидание завершения процессов
wait


#!/bin/bash

echo "========================================"
echo "Cafe Face Recognition System - Docker"
echo "========================================"
echo ""

# Проверка установки Docker
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker не установлен!"
    echo "Пожалуйста, установите Docker Desktop для macOS:"
    echo "https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "[INFO] Docker обнаружен"
echo ""

# Проверка запущен ли Docker
if ! docker info &> /dev/null; then
    echo "[ERROR] Docker не запущен!"
    echo "Пожалуйста, запустите Docker Desktop и попробуйте снова."
    exit 1
fi

echo "[INFO] Docker запущен"
echo ""

# Останавливаем старые контейнеры если есть
echo "[INFO] Останавливаем старые контейнеры..."
docker-compose down

echo ""
echo "[INFO] Собираем и запускаем контейнеры..."
echo "Это может занять несколько минут при первом запуске..."
echo ""

# Запускаем docker-compose
docker-compose up --build -d

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Не удалось запустить контейнеры!"
    echo "Проверьте логи выше для деталей."
    exit 1
fi

echo ""
echo "========================================"
echo "[SUCCESS] Все сервисы запущены!"
echo "========================================"
echo ""
echo "Доступные сервисы:"
echo "  - Frontend:  http://localhost:5173"
echo "  - Backend:   http://localhost:3000"
echo "  - Video:     http://localhost:5001/video_feed"
echo ""
echo "Для просмотра логов:"
echo "  docker-compose logs -f"
echo ""
echo "Для остановки:"
echo "  docker-compose down"
echo ""
echo "========================================"

# Ждём несколько секунд чтобы сервисы запустились
sleep 3

# Открываем браузер
if command -v open &> /dev/null; then
    open http://localhost:5173
fi

echo ""
echo "Нажмите Ctrl+C для выхода (сервисы продолжат работать в фоне)"
echo "Для просмотра логов: docker-compose logs -f"
echo ""


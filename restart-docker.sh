#!/bin/bash

echo "========================================"
echo "Перезапуск Cafe Face System"
echo "========================================"
echo ""

echo "[INFO] Останавливаем контейнеры..."
docker-compose down

echo ""
echo "[INFO] Запускаем контейнеры..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "[SUCCESS] Система перезапущена!"
    echo ""
    echo "Frontend: http://localhost:5173"
    echo "Backend:  http://localhost:3000"
else
    echo ""
    echo "[ERROR] Ошибка при перезапуске"
    exit 1
fi


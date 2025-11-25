#!/bin/bash

echo "========================================"
echo "Пересборка Docker образов"
echo "========================================"
echo ""

echo "[INFO] Останавливаем контейнеры..."
docker-compose down

echo ""
echo "[INFO] Пересобираем образы..."
docker-compose build --no-cache

echo ""
echo "[INFO] Запускаем контейнеры..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "[SUCCESS] Пересборка завершена!"
    echo ""
    echo "Frontend: http://localhost:5173"
else
    echo ""
    echo "[ERROR] Ошибка при пересборке"
    exit 1
fi


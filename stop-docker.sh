#!/bin/bash

echo "========================================"
echo "Останавливаем Cafe Face System"
echo "========================================"
echo ""

docker-compose down

if [ $? -eq 0 ]; then
    echo ""
    echo "[SUCCESS] Все контейнеры остановлены"
else
    echo ""
    echo "[ERROR] Ошибка при остановке"
    exit 1
fi


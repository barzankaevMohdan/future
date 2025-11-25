#!/bin/bash

echo "========================================"
echo "Проверка состояния системы"
echo "========================================"
echo ""

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен"
    exit 1
else
    echo "✅ Docker установлен: $(docker --version)"
fi

# Проверка Docker запущен
if ! docker info &> /dev/null; then
    echo "❌ Docker не запущен"
    exit 1
else
    echo "✅ Docker запущен"
fi

echo ""
echo "Статус контейнеров:"
echo "----------------------------------------"
docker-compose ps

echo ""
echo "Использование ресурсов:"
echo "----------------------------------------"
docker stats --no-stream

echo ""
echo "========================================"


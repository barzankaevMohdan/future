#!/bin/bash

echo "========================================"
echo "Логи Docker контейнеров"
echo "========================================"
echo ""
echo "Нажмите Ctrl+C для выхода из просмотра логов"
echo ""
sleep 2

docker-compose logs -f


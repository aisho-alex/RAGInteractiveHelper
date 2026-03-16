#!/bin/bash
# Скрипт сборки и деплоя RAG приложения

set -e

PROJECT_DIR="/media/alexander/data/agents/MTK"
NGINX_CONF="/etc/nginx/sites-available/rag"
NGINX_LINK="/etc/nginx/sites-enabled/rag"

echo "=== Сборка и деплой RAG приложения ==="

# 1. Сборка фронтенда
echo "[1/4] Сборка Vue фронтенда..."
cd "$PROJECT_DIR/frontend"
npm run build

# 2. Создание symlink для nginx
echo "[2/4] Настройка nginx конфигурации..."
sudo ln -sf "$PROJECT_DIR/nginx/rag.conf" "$NGINX_CONF"
sudo ln -sf "$NGINX_CONF" "$NGINX_LINK"

# 3. Проверка конфигурации nginx
echo "[3/4] Проверка конфигурации nginx..."
sudo nginx -t

# 4. Перезагрузка nginx
echo "[4/4] Перезагрузка nginx..."
sudo systemctl reload nginx

echo ""
echo "=== Деплой завершён! ==="
echo "Приложение доступно по адресу: http://localhost"

#!/bin/bash
# Скрипт деплоя RAG приложения на удалённый сервер
# Копируем только исходники, venv создаётся на сервере

set -e

# Конфигурация
REMOTE_USER="ubuntu"
REMOTE_HOST="82.202.139.144"
REMOTE_DIR="/home/ubuntu/rag-app"
LOCAL_DIR="/media/alexander/data/agents/MTK"

echo "=== Деплой RAG приложения на $REMOTE_HOST ==="
echo ""

# 1. Копирование файлов на сервер (только исходники)
echo "[1/5] Копирование файлов на сервер (без venv и node_modules)..."
rsync -avz --delete \
    --exclude 'backend/venv' \
    --exclude 'backend/venv/**' \
    --exclude 'backend/__pycache__' \
    --exclude 'backend/app/**/*.pyc' \
    --exclude 'frontend/node_modules' \
    --exclude 'frontend/node_modules/**' \
    --exclude 'frontend/dist' \
    --exclude '.git' \
    --exclude '*.log' \
    --exclude 'backend/data/embeddings' \
    "$LOCAL_DIR/" \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/"

# 2. Установка зависимостей бэкенда на сервере
echo "[2/5] Установка зависимостей бэкенда на сервере..."
ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" 'bash -s' << 'EOF'
# Установка python3.12-venv
sudo apt update -qq && sudo apt install -y python3.12-venv

cd ~/rag-app/backend

# Удаление старого venv и создание нового
rm -rf venv
python3 -m venv venv

# Установка зависимостей через venv pip
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Загрузка документа в базу (если embeddings ещё нет)
if [ ! -d data/embeddings/chroma.sqlite3 ]; then
    echo "Загрузка документа в базу..."
    ./venv/bin/python load_document.py
fi
EOF

# 3. Установка зависимостей фронтенда и сборка на сервере
echo "[3/5] Сборка фронтенда на сервере..."
ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" 'bash -s' << 'EOF'
cd ~/rag-app/frontend

# Установка Node.js зависимостей
npm install

# Сборка
npm run build
EOF

# 4. Настройка nginx
echo "[4/5] Настройка nginx..."
ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" 'bash -s' << 'EOF'
if ! command -v nginx &> /dev/null; then
    echo "⚠️  nginx не установлен. Пропускаем настройку."
    echo "   Установите: sudo apt install nginx"
else
    # Обновление пути в конфиге
    sed -i "s|/media/alexander/data/agents/MTK/frontend/dist|$HOME/rag-app/frontend/dist|g" ~/rag-app/nginx/rag.conf
    
    # Копирование конфига
    sudo ln -sf ~/rag-app/nginx/rag.conf /etc/nginx/sites-available/rag
    sudo ln -sf /etc/nginx/sites-available/rag /etc/nginx/sites-enabled/rag
    
    # Проверка и перезагрузка
    sudo nginx -t && sudo systemctl reload nginx
    echo "✓ nginx настроен"
fi
EOF

# 5. Настройка systemd сервиса
echo "[5/5] Настройка systemd сервиса..."
ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" 'bash -s' << 'EOF'
# Копирование и активация сервиса
sudo cp ~/rag-app/systemd/rag-backend.service /etc/systemd/system/

# Обновление пути в сервисе
sudo sed -i "s|/media/alexander/data/agents/MTK/backend|$HOME/rag-app/backend|g" /etc/systemd/system/rag-backend.service
sudo sed -i "s|User=alexander|User=$REMOTE_USER|g" /etc/systemd/system/rag-backend.service

# Перезагрузка systemd и запуск
sudo systemctl daemon-reload
sudo systemctl enable rag-backend
sudo systemctl restart rag-backend

echo "✓ Сервис запущен"
EOF

echo ""
echo "=== Деплой завершён! ==="
echo ""
echo "Полезные команды:"
echo "  Проверка статуса: ssh $REMOTE_USER@$REMOTE_HOST 'sudo systemctl status rag-backend'"
echo "  Логи: ssh $REMOTE_USER@$REMOTE_HOST 'sudo journalctl -u rag-backend -f'"
echo "  Перезапуск: ssh $REMOTE_USER@$REMOTE_HOST 'sudo systemctl restart rag-backend'"
echo ""
echo "Приложение доступно по адресу: http://$REMOTE_HOST"
echo ""
echo "⚠️  ВАЖНО: Проверьте backend/.env с вашим API ключом от routerai.ru!"
echo "   ssh $REMOTE_USER@$REMOTE_HOST 'nano ~/rag-app/backend/.env'"

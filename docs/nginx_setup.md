# Установка и настройка nginx для RAG приложения

## 1. Установка nginx

```bash
sudo apt update
sudo apt install nginx -y
```

## 2. Настройка

### Вариант A: Автоматический деплой

```bash
cd /media/alexander/data/agents/MTK
chmod +x deploy.sh
./deploy.sh
```

### Вариант B: Ручная настройка

```bash
# Копирование конфигурации
sudo cp nginx/rag.conf /etc/nginx/sites-available/rag
sudo ln -sf /etc/nginx/sites-available/rag /etc/nginx/sites-enabled/rag

# Проверка конфигурации
sudo nginx -t

# Перезагрузка nginx
sudo systemctl reload nginx
```

## 3. Настройка systemd для бэкенда

```bash
# Копирование сервиса
sudo cp systemd/rag-backend.service /etc/systemd/system/

# Перезагрузка systemd и запуск
sudo systemctl daemon-reload
sudo systemctl enable rag-backend
sudo systemctl start rag-backend

# Проверка статуса
sudo systemctl status rag-backend
```

## 4. Проверка

- Фронтенд: http://localhost/
- API: http://localhost/api/query
- Health: http://localhost/health

## 5. Логи

```bash
# nginx
sudo tail -f /var/log/nginx/rag_access.log
sudo tail -f /var/log/nginx/rag_error.log

# Бэкенд
sudo journalctl -u rag-backend -f
```

## 6. Firewall (если нужен)

```bash
sudo ufw allow 'Nginx Full'
sudo ufw status
```

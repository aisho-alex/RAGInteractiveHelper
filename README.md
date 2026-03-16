# RAG Система (Next.js + FastAPI)

Приложение для поиска ответов строго по предоставленным документам с использованием RAG (Retrieval-Augmented Generation).

## Структура проекта

```
MTK/
├── backend/                 # FastAPI бэкенд
│   ├── app/
│   │   ├── main.py         # Точка входа
│   │   ├── db.py           # Инициализация ChromaDB
│   │   ├── models/         # Pydantic модели
│   │   ├── routers/        # API роутеры
│   │   │   ├── rag.py      # RAG запросы
│   │   │   └── documents.py # Загрузка документов
│   │   └── services/       # Бизнес-логика
│   │       └── rag_service.py
│   ├── data/               # Данные (документы, эмбеддинги)
│   ├── tests/              # Тесты
│   └── requirements.txt    # Python зависимости
├── frontend/               # Next.js фронтенд
│   ├── src/
│   │   ├── app/           # Next.js 14 App Router
│   │   ├── components/    # React компоненты
│   │   ├── lib/           # Утилиты и API клиент
│   │   └── types/         # TypeScript типы
│   └── package.json
└── docs/                   # Документация
    └── project_structure.txt
```

## Быстрый старт

### Бэкенд

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env, указав ваш API ключ

# Запуск сервера
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Фронтенд

```bash
cd frontend
npm install
npm run dev
```

Фронтенд написан на **Vue 3** + Vite + TailwindCSS.

## Развёртывание с nginx

### Автоматический деплой

```bash
./deploy.sh
```

### Ручная настройка

См. [docs/nginx_setup.md](docs/nginx_setup.md)

## API Endpoints

### Бэкенд (http://localhost:8000)

- `POST /api/query` — Поиск ответа по документам
- `GET /health` — Проверка статуса

### Фронтенд (http://localhost:3000)

Веб-интерфейс на Vue 3 для отправки запросов к документу.

## Конфигурация

### backend/.env

```env
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://routerai.ru/api/v1
EMBEDDING_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-3.5-turbo
CHROMA_PERSIST_DIR=./data/embeddings
```

### frontend/.env.local

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Как это работает

1. **Загрузка документов**: Текст разбивается на чанки, создаются эмбеддинги через OpenAI API
2. **Векторный поиск**: При запросе находятся наиболее релевантные чанки (ChromaDB)
3. **Генерация ответа**: LLM генерирует ответ строго на основе найденных документов

## Особенности

- Ответы только на основе загруженных документов
- Поддержка PDF и TXT файлов
- Векторная база ChromaDB с персистентным хранением
- Детерминированные ответы (temperature=0)

## Примеры запросов

По загруженному документу "Тестовая инструкция для ИИ.md" можно задавать вопросы:

- "Какое основное назначение модуля Индентирование?"
- "Как проводится калибровка датчика смещения?"
- "Что делать если поверхность не найдена?"
- "Какие требования безопасности при работе?"

## Документ

В систему уже загружен документ: **Тестовая инструкция для ИИ.md** (модуль «Индентирование»).

# RAG Interactive Helper (Универсальная RAG-система)

Приложение для поиска ответов строго по предоставленным документам с использованием RAG (Retrieval-Augmented Generation).

**Универсальная версия** — поддерживает загрузку и обработку любых документов: PDF, TXT, MD.

## Структура проекта

```
RAGInteractiveHelper/
├── backend/                 # FastAPI бэкенд
│   ├── app/
│   │   ├── main.py         # Точка входа
│   │   ├── db.py           # Инициализация ChromaDB
│   │   ├── models/         # Pydantic модели
│   │   ├── routers/        # API роутеры
│   │   │   ├── rag.py      # RAG запросы
│   │   │   └── documents.py # Загрузка документов
│   │   ├── services/       # Бизнес-логика
│   │   │   └── rag_service.py
│   ├── data/               # Данные (документы, эмбеддинги)
│   ├── tests/              # Тесты
│   └── requirements.txt    # Python зависимости
├── frontend/               # Vue 3 фронтенд
│   ├── src/
│   │   ├── components/    # Vue компоненты
│   │   ├── composables/   # Композаблы
│   │   └── assets/        # Ресурсы
│   └── package.json
├── docs/                   # Документация
└── deploy.sh               # Скрипт деплоя
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
- `POST /api/documents/upload` — Загрузка документа (PDF, TXT, MD)
- `GET /api/documents/list` — Список всех документов
- `GET /api/documents/full` — Полный текст документа
- `GET /health` — Проверка статуса

### Фронтенд (http://localhost:3000)

Веб-интерфейс на Vue 3 для:
- Загрузки документов
- Отправки запросов к документам
- Просмотра текста документа с подсветкой релевантных фрагментов

## Конфигурация

### backend/.env

```env
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://routerai.ru/api/v1
EMBEDDING_MODEL=intfloat/multilingual-e5-large
CHAT_MODEL=google/gemini-3.1-flash-lite-preview
CHROMA_PERSIST_DIR=./data/embeddings
```

### frontend/.env.local

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Как это работает

1. **Загрузка документов**: Пользователь загружает документ (PDF, TXT, MD), текст разбивается на чанки, создаются эмбеддинги через OpenAI API
2. **Векторный поиск**: При запросе находятся наиболее релевантные чанки (ChromaDB)
3. **Генерация ответа**: LLM генерирует ответ строго на основе найденных документов

## Особенности

- ✅ Ответы только на основе загруженных документов
- ✅ Поддержка PDF, TXT, MD файлов
- ✅ Векторная база ChromaDB с персистентным хранением
- ✅ Детерминированные ответы (temperature=0)
- ✅ Голосовой ввод вопросов (STT)
- ✅ Озвучка ответов (TTS)
- ✅ Подсветка релевантных фрагментов в тексте документа

## Поддерживаемые форматы документов

| Формат | Описание |
|--------|----------|
| PDF | Извлечение текста через pdfplumber |
| TXT | Простой текст в кодировке UTF-8 |
| MD | Markdown файлы |

## Примеры запросов

После загрузки документа можно задавать вопросы по его содержанию:

- Вопросы по содержанию документа
- Поиск конкретной информации
- Уточнение деталей

## Развёртывание

### Локальная разработка

```bash
# Бэкенд
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Фронтенд (в другом терминале)
cd frontend
npm run dev
```

### Продакшен деплой

```bash
./deploy.sh
```

Скрипт автоматически:
- Установит зависимости
- Соберёт фронтенд
- Настроит nginx
- Запустит сервисы

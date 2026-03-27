#!/usr/bin/env python3
"""
Скрипт для загрузки документа в RAG базу данных
"""
import sys
import os

# Добавляем корень backend в path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import init_db
from app.services.rag_service import add_document


def load_document(filepath: str):
    """Загрузка файла в RAG базу"""
    print(f"Загрузка документа: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"Размер текста: {len(text)} символов")

    doc_id = add_document(text, {
        "filename": os.path.basename(filepath),
        "type": os.path.splitext(filepath)[1].lower()
    })

    print(f"Документ успешно загружен. ID: {doc_id}")
    return doc_id


if __name__ == "__main__":
    # Инициализация БД
    init_db()
    print("База данных инициализирована")
    
    # Путь к документу
    doc_path = os.path.join(os.path.dirname(__file__), "data", "documents", "Тестовая инструкция для ИИ.md")
    
    if os.path.exists(doc_path):
        load_document(doc_path)
    else:
        print(f"Документ не найден: {doc_path}")
        sys.exit(1)

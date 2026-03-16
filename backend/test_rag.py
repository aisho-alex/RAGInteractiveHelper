#!/usr/bin/env python3
"""
Скрипт для тестирования RAG системы
"""
import requests
import json

API_BASE = "http://localhost:8000"


def test_query(query: str):
    """Отправка запроса к RAG системе"""
    response = requests.post(
        f"{API_BASE}/api/query",
        json={"query": query, "top_k": 3}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("\n" + "=" * 60)
        print(f"Запрос: {query}")
        print("=" * 60)
        print(f"\nОтвет:\n{data['answer']}\n")
        
        if data.get('sources'):
            print("Источники:")
            for i, src in enumerate(data['sources'], 1):
                print(f"\n[{i}] {src.get('metadata', {}).get('filename', 'N/A')}")
                print(f"    {src['content'][:150]}...")
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("Тестирование RAG системы")
    print("=" * 60)
    
    # Тестовые запросы по документу
    queries = [
        "Какое основное назначение модуля Индентирование?",
        "Как проводится калибровка датчика смещения?",
        "Что делать если поверхность не найдена?",
        "Какие требования безопасности при работе с модулем?"
    ]
    
    for query in queries:
        test_query(query)
        input("\nНажмите Enter для следующего запроса...")

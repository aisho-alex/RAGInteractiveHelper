"""
LLM клиент для различных задач (нормализация текста и др.)
"""
import os
from typing import Optional
from langchain_openai import ChatOpenAI

_llm_client: Optional[ChatOpenAI] = None

def get_llm_client() -> Optional[ChatOpenAI]:
    """
    Получить LLM клиент для дополнительных задач
    
    Returns:
        ChatOpenAI клиент или None если не настроен
    """
    global _llm_client
    
    # Проверяем наличие API ключа (поддерживаем разные имена переменных)
    api_key = (
        os.getenv("ROUTERAI_API_KEY") or 
        os.getenv("OPENAI_API_KEY")
    )
    
    if not api_key:
        return None
    
    if _llm_client is None:
        _llm_client = ChatOpenAI(
            api_key=api_key,
            base_url=(
                os.getenv("ROUTERAI_BASE_URL") or 
                os.getenv("OPENAI_API_BASE") or 
                "https://api.routerai.ru/v1"
            ),
            model=(
                os.getenv("LLM_MODEL") or 
                os.getenv("CHAT_MODEL") or 
                "gpt-4o-mini"
            ),
            temperature=0.3,
            max_tokens=1000
        )
    
    return _llm_client

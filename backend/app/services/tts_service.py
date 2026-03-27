"""
TTS сервис на основе Silero с LLM нормализацией текста
"""
import os
import io
import torch
from pathlib import Path
from typing import List, Optional
import re

# Директория для кэширования моделей
TTS_CACHE_DIR = Path("./data/tts_models")
TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Промпт для нормализации текста под TTS
TTS_NORMALIZE_PROMPT = """Твоя задача — преобразовать текст в форму, удобную для озвучивания синтезатором речи (TTS).

ПРАВИЛА ПРЕОБРАЗОВАНИЯ:

1. **Удали всю разметку**: Markdown (#, *, `, >, [], (), URL), HTML теги, специальные символы
2. **Числа прописью**: 
   - 123 → сто двадцать три
   - 2024 год → две тысячи двадцать четвёртый год
   - 50% → пятьдесят процентов
   - 3.14 → три целых четырнадцать сотых
3. **Раскрой сокращения**:
   - т.д. → так далее
   - т.п. → тому подобное
   - и др. → и другие
   - напр. → например
   - см. → смотри
   - РФ → Российская Федерация
   - США → Соединённые Штаты Америки
4. **Добавь паузы**: Используй запятые, точки, тире для естественных пауз при чтении
5. **Разбей длинные предложения**: Если предложение длиннее 50 слов, раздели на несколько
6. **Удали лишнее**: Сноски [1], ссылки http://..., технические обозначения
7. **Кириллица**: Транслитерируй латинские слова на русский если это уместно (бренд оставь как есть)
8. **Единицы измерения**: 
   - 10 км → десять километров
   - 5 кг → пять килограммов
   - 25°C → двадцать пять градусов Цельсия

ВАЖНО:
- Сохраняй исходный смысл текста
- Не добавляй новую информацию
- Избегай повторов
- Делай текст естественным для устной речи

Пример входного текста:
"В 2024 году компания Apple выпустила iPhone 15 Pro с процессором A17 Pro (3 нм). Цена: $999."

Пример выходного текста:
"В две тысячи двадцать четвёртом году компания Эппл выпустила айфон пятнадцать про с процессором эй семнадцать про, три нанометра. Цена: девятьсот девяносто девять долларов."

Теперь преобразуй этот текст:"""

class SileroTTS:
    """Сервис синтеза речи на основе Silero с LLM нормализацией"""

    def __init__(self, llm_client=None):
        self.model = None
        self.speakers = []
        self.llm_client = llm_client
        self._load_model()

    def _load_model(self):
        """Загрузка модели Silero TTS"""
        try:
            # Загружаем модель Silero
            self.model, self.example_text = torch.hub.load(
                repo_or_dir='snakers4/silero-models',
                model='silero_tts',
                language='ru',
                speaker='v4_ru',
                cache=str(TTS_CACHE_DIR),
                trust_repo=True
            )
            
            # Доступные голоса
            self.speakers = ['aidar', 'baya', 'kseniya', 'xenia', 'eugene']
            
            print("✓ Silero TTS модель загружена")
            
        except Exception as e:
            print(f"✗ Ошибка загрузки Silero TTS: {e}")
            self.model = None

    def get_speakers(self) -> List[str]:
        """Получить список доступных голосов"""
        return self.speakers if self.speakers else ['aidar', 'baya', 'kseniya']

    def normalize_text_for_tts(self, text: str) -> str:
        """
        Нормализация текста для TTS через LLM

        Args:
            text: Исходный текст

        Returns:
            Нормализованный текст для озвучки
        """
        if not self.llm_client:
            # Fallback: простая нормализация без LLM
            return self._simple_normalize(text)

        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            
            # Формируем запрос к LLM
            messages = [
                SystemMessage(content=TTS_NORMALIZE_PROMPT),
                HumanMessage(content=text)
            ]

            # Вызываем LLM через LangChain invoke
            response = self.llm_client.invoke(messages)
            
            # Извлекаем текст из ответа
            normalized = response.content if hasattr(response, 'content') else str(response)
            normalized = normalized.strip()

            # Дополнительная очистка от возможных артефактов
            normalized = self._post_process_llm_output(normalized)

            print(f"✓ Текст нормализован LLM: {len(text)} → {len(normalized)} символов")
            return normalized

        except Exception as e:
            print(f"⚠ Ошибка нормализации LLM: {e}. Используем fallback.")
            return self._simple_normalize(text)

    def _simple_normalize(self, text: str) -> str:
        """
        Простая нормализация без LLM (fallback)
        """
        # Удаление Markdown разметки
        text = re.sub(r'#+\s*', '', text)  # Заголовки
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Жирный
        text = re.sub(r'\*(.+?)\*', r'\1', text)  # Курсив
        text = re.sub(r'`(.+?)`', r'\1', text)  # Код
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # Ссылки
        text = re.sub(r'\[.+?\]', '', text)  # Сноски
        
        # Удаление URL
        text = re.sub(r'http[s]?://\S+', '', text)
        
        # Базовое раскрытие сокращений
        abbreviations = {
            'т.д.': 'так далее',
            'т.п.': 'тому подобное',
            'и др.': 'и другие',
            'напр.': 'например',
            'см.': 'смотри',
            'г.': 'год',
            'гг.': 'годы',
        }
        for abbr, full in abbreviations.items():
            text = text.replace(abbr, full)
        
        # Очистка от множественных пробелов
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def _post_process_llm_output(self, text: str) -> str:
        """
        Постобработка вывода LLM
        """
        # Удаление возможных кавычек от LLM
        text = text.strip('"\'')
        
        # Удаление префиксов типа "Вот нормализованный текст:"
        text = re.sub(r'^(Вот|Вот и|Вот нормализованный текст:?)\s*', '', text, flags=re.IGNORECASE)
        
        # Очистка от множественных пробелов
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def synthesize(self, text: str, speaker: str = "aidar", sample_rate: int = 48000, normalize: bool = True) -> bytes:
        """
        Синтез речи из текста

        Args:
            text: Текст для синтеза
            speaker: Голос (aidar, baya, kseniya, xenia, eugene)
            sample_rate: Частота дискретизации (48000 или 24000)
            normalize: Нормализовать текст через LLM

        Returns:
            WAV аудио в байтах
        """
        if not self.model:
            raise RuntimeError("TTS модель не загружена")

        try:
            # Нормализация текста
            if normalize:
                text = self.normalize_text_for_tts(text)
            
            print(f"🔊 TTS синтез: {len(text)} символов, голос={speaker}, sample_rate={sample_rate}")

            # Silero имеет лимит ~1000 символов, разбиваем на части
            MAX_CHARS = 900  # С запасом
            if len(text) > MAX_CHARS:
                return self._synthesize_chunked(text, speaker, sample_rate)

            # Синтез аудио
            audio = self.model.apply_tts(
                text=text,
                speaker=speaker,
                sample_rate=sample_rate
            )

            # Сохраняем в WAV формат
            wav_buffer = io.BytesIO()
            import wave
            
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                # Конвертируем тензор в numpy array и затем в байты
                import numpy as np
                audio_np = (audio * 32767).numpy().astype(np.int16)
                wf.writeframes(audio_np.tobytes())

            print(f"✓ TTS готов: {len(wav_buffer.getvalue())} байт")
            return wav_buffer.getvalue()

        except Exception as e:
            print(f"✗ Ошибка синтеза речи: {e}")
            raise RuntimeError(f"Ошибка синтеза речи: {e}")

    def _synthesize_chunked(self, text: str, speaker: str, sample_rate: int) -> bytes:
        """
        Синтез длинного текста с разбивкой на части
        """
        import numpy as np
        
        # Разбиваем на предложения
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < 900:
                current_chunk += (" " if current_chunk else "") + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        print(f"📦 Разбито на {len(chunks)} частей: {[len(c) for c in chunks]}")
        
        # Синтезируем каждую часть
        all_audio = []
        for i, chunk in enumerate(chunks):
            print(f"  Часть {i+1}/{len(chunks)}: {len(chunk)} символов")
            audio = self.model.apply_tts(
                text=chunk,
                speaker=speaker,
                sample_rate=sample_rate
            )
            all_audio.append((audio * 32767).numpy().astype(np.int16))
        
        # Конкатенируем аудио
        combined = np.concatenate(all_audio)
        
        # Сохраняем в WAV
        wav_buffer = io.BytesIO()
        import wave
        
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(combined.tobytes())
        
        print(f"✓ TTS готов (chunked): {len(wav_buffer.getvalue())} байт")
        return wav_buffer.getvalue()


# Глобальный экземпляр
_tts_service: Optional[SileroTTS] = None

def get_tts_service(llm_client=None) -> SileroTTS:
    """Получить сервис TTS"""
    global _tts_service
    if _tts_service is None:
        _tts_service = SileroTTS(llm_client=llm_client)
    elif llm_client is not None:
        # Обновляем LLM клиент если предоставлен
        _tts_service.llm_client = llm_client
    return _tts_service

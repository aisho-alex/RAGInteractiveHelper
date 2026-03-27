"""
TTS сервис на основе Silero
"""
import os
import io
import torch
from pathlib import Path
from typing import List

# Директория для кэширования моделей
TTS_CACHE_DIR = Path("./data/tts_models")
TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

class SileroTTS:
    """Сервис синтеза речи на основе Silero"""

    def __init__(self):
        self.model = None
        self.speakers = []
        self._load_model()

    def _load_model(self):
        """Загрузка модели Silero TTS"""
        try:
            # Загружаем модель Silero
            self.model, self.example_text = torch.hub.load(
                repo_or_dir='snakers4/silero-models',
                model='silero_tts',
                language='ru',
                speaker='v3_1',
                cache=str(TTS_CACHE_DIR)
            )
            
            # Доступные голоса для v3_1
            self.speakers = ['aidar', 'baya', 'kseniya', 'xenia', 'eugene']
            
            print("✓ Silero TTS модель загружена")
            
        except Exception as e:
            print(f"✗ Ошибка загрузки Silero TTS: {e}")
            self.model = None

    def get_speakers(self) -> List[str]:
        """Получить список доступных голосов"""
        return self.speakers if self.speakers else ["aidar", "baya", "kseniya", "xenia", "eugene"]

    def synthesize(self, text: str, speaker: str = "aidar", sample_rate: int = 48000) -> bytes:
        """
        Синтез речи из текста

        Args:
            text: Текст для синтеза
            speaker: Голос (aidar, baya, kseniya, xenia, eugene)
            sample_rate: Частота дискретизации (48000 или 24000)

        Returns:
            WAV аудио в байтах
        """
        if not self.model:
            raise RuntimeError("TTS модель не загружена")

        try:
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

            return wav_buffer.getvalue()

        except Exception as e:
            raise RuntimeError(f"Ошибка синтеза речи: {e}")


# Глобальный экземпляр
_tts_service = None

def get_tts_service() -> SileroTTS:
    """Получить сервис TTS"""
    global _tts_service
    if _tts_service is None:
        _tts_service = SileroTTS()
    return _tts_service

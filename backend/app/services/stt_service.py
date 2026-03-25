"""
VOSK STT сервис для распознавания речи
"""
import os
import json
from pathlib import Path
from typing import Optional

# Модели VOSK
VOSK_MODELS_DIR = Path("./data/stt_models")
VOSK_MODELS_DIR.mkdir(parents=True, exist_ok=True)

class VoskSTT:
    """Сервис распознавания речи на основе VOSK"""
    
    def __init__(self, model_name: str = "vosk-model-small-ru-0.22"):
        self.model_name = model_name
        self.model_path = VOSK_MODELS_DIR / model_name
        self.recognizer = None
        self._load_model()
    
    def _download_model(self):
        """Скачивание модели VOSK"""
        import urllib.request
        import tarfile
        
        model_url = f"https://alphacephei.com/vosk/models/{self.model_name}.zip"
        zip_path = VOSK_MODELS_DIR / f"{self.model_name}.zip"
        
        print(f"Скачивание модели {self.model_name}...")
        
        # Скачиваем
        urllib.request.urlretrieve(model_url, zip_path)
        
        # Распаковываем
        with tarfile.open(zip_path, "r:gz" if str(zip_path).endswith(".tar.gz") else "r") as tar:
            tar.extractall(path=VOSK_MODELS_DIR)
        
        # Удаляем архив
        if zip_path.exists():
            zip_path.unlink()
        
        print(f"✓ Модель {self.model_name} загружена")
    
    def _load_model(self):
        """Загрузка модели VOSK"""
        try:
            from vosk import Model, KaldiRecognizer
            
            # Проверяем наличие модели
            if not self.model_path.exists():
                self._download_model()
            
            # Загружаем модель
            model = Model(str(self.model_path))
            self.recognizer = KaldiRecognizer(model, 16000)
            
            print("✓ VOSK STT модель загружена")
            
        except Exception as e:
            print(f"✗ Ошибка загрузки VOSK STT: {e}")
            self.recognizer = None
    
    def recognize(self, audio_data: bytes, sample_rate: int = 16000) -> Optional[str]:
        """
        Распознавание речи из аудио
        
        Args:
            audio_data: WAV аудио в байтах (16kHz, mono, 16-bit)
            sample_rate: Частота дискретизации
            
        Returns:
            Распознанный текст или None
        """
        if not self.recognizer:
            raise RuntimeError("STT модель не загружена")
        
        try:
            from vosk import KaldiRecognizer
            
            # Создаём новый recognizer для этого запроса
            recognizer = KaldiRecognizer(self.recognizer.Model(), sample_rate)
            recognizer.SetWords(True)
            
            # Обработка аудио
            if recognizer.AcceptWaveform(audio_data):
                result = json.loads(recognizer.Result())
                return result.get("text", "")
            else:
                result = json.loads(recognizer.PartialResult())
                return result.get("partial", "")
                
        except Exception as e:
            raise RuntimeError(f"Ошибка распознавания речи: {e}")
    
    def recognize_stream(self, audio_chunk: bytes) -> dict:
        """
        Распознавание потока аудио (для микрофона)
        
        Args:
            audio_chunk: Чанк аудио данных
            
        Returns:
            Словарь с результатом {"text": str, "partial": str, "done": bool}
        """
        if not self.recognizer:
            return {"text": "", "partial": "", "done": False}
        
        try:
            if self.recognizer.AcceptWaveform(audio_chunk):
                result = json.loads(self.recognizer.Result())
                return {
                    "text": result.get("text", ""),
                    "partial": "",
                    "done": True
                }
            else:
                result = json.loads(self.recognizer.PartialResult())
                return {
                    "text": "",
                    "partial": result.get("partial", ""),
                    "done": False
                }
        except Exception as e:
            return {"text": "", "partial": "", "done": False, "error": str(e)}


# Глобальный экземпляр
_stt_service = None

def get_stt_service() -> VoskSTT:
    """Получить сервис STT"""
    global _stt_service
    if _stt_service is None:
        _stt_service = VoskSTT()
    return _stt_service

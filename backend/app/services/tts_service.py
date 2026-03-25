"""
TTS сервис через браузерный SpeechSynthesis (клиентская сторона)
Серверная заглушка для совместимости
"""

class BrowserTTS:
    """
    Заглушка TTS сервиса.
    Синтез речи выполняется на клиенте через Web Speech API.
    """
    
    def get_speakers(self) -> list:
        """Доступные голоса определяются на клиенте"""
        return ["browser-native"]
    
    def synthesize(self, text: str, speaker: str = "browser-native", sample_rate: int = 48000) -> bytes:
        """
        Синтез речи не поддерживается на сервере.
        Используйте Web Speech API на клиенте.
        """
        raise NotImplementedError("TTS выполняется на клиенте через Web Speech API")


_tts_service = None

def get_tts_service() -> BrowserTTS:
    """Получить сервис TTS"""
    global _tts_service
    if _tts_service is None:
        _tts_service = BrowserTTS()
    return _tts_service

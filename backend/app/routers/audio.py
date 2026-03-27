from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Body
from fastapi.responses import Response
from typing import Optional
from pydantic import BaseModel, Field
from app.services.tts_service import get_tts_service
from app.services.stt_service import get_stt_service

router = APIRouter()


class TTSRequest(BaseModel):
    text: str = Field(..., description="Текст для синтеза")
    speaker: str = Field(default="aidar", description="Голос (aidar, baya, kseniya, xenia, eugene)")
    sample_rate: int = Field(default=48000, description="Частота дискретизации (48000 или 24000)")
    normalize: bool = Field(default=True, description="Нормализовать текст через LLM")


@router.get("/speakers")
async def get_speakers():
    """Получить список доступных голосов для TTS"""
    tts = get_tts_service()
    return {"speakers": tts.get_speakers()}


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Синтез речи из текста (Silero TTS)

    Возвращает WAV аудио файл
    """
    try:
        from app.utils.llm import get_llm_client
        tts = get_tts_service(llm_client=get_llm_client())
        audio_data = tts.synthesize(
            text=request.text,
            speaker=request.speaker,
            sample_rate=request.sample_rate,
            normalize=request.normalize
        )

        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Legacy endpoint для совместимости (короткие тексты через GET)
@router.get("/tts-legacy")
async def text_to_speech_legacy(
    text: str = Query(..., description="Текст для синтеза"),
    speaker: str = Query("aidar", description="Голос (aidar, baya, kseniya, xenia, eugene)"),
    sample_rate: int = Query(48000, description="Частота дискретизации (48000 или 24000)"),
    normalize: bool = Query(True, description="Нормализовать текст через LLM перед синтезом")
):
    """
    Синтез речи из текста (Silero TTS) - GET версия для коротких текстов

    Возвращает WAV аудио файл
    """
    try:
        from app.utils.llm import get_llm_client
        tts = get_tts_service(llm_client=get_llm_client())
        audio_data = tts.synthesize(text, speaker, sample_rate, normalize=normalize)

        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stt")
async def speech_to_text(file: UploadFile = File(..., description="WAV аудио файл (16kHz, mono, 16-bit)")):
    """
    Распознавание речи в текст (VOSK STT)

    Принимает WAV файл (16kHz, mono, 16-bit)
    """
    try:
        stt = get_stt_service()
        audio_data = await file.read()
        text = stt.recognize(audio_data)

        return {"text": text or ""}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

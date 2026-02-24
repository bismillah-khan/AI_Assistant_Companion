import asyncio
import logging
from pathlib import Path

import httpx

from app.core.config.settings import Settings

logger = logging.getLogger(__name__)


class WhisperClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def transcribe_file(self, file_path: Path) -> str:
        """Transcribe audio using Groq's Whisper API"""
        try:
            # Use Groq's Whisper API endpoint
            url = f"{self.settings.llm_api_base.rstrip('/')}/openai/v1/audio/transcriptions"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                with open(file_path, 'rb') as audio_file:
                    files = {'file': (file_path.name, audio_file, 'audio/webm')}
                    data = {
                        'model': 'whisper-large-v3',
                        'response_format': 'text',
                        'language': 'en'  # Can be auto-detected by removing this
                    }
                    headers = {
                        'Authorization': f'Bearer {self.settings.llm_api_key}'
                    }
                    
                    response = await client.post(
                        url,
                        files=files,
                        data=data,
                        headers=headers
                    )
                    response.raise_for_status()
                    
                    # Groq returns plain text with response_format='text'
                    text = response.text.strip()
                    logger.info(f"Transcription successful: {text[:100]}...")
                    return text
                    
        except Exception as exc:
            logger.exception("whisper_transcribe_failed")
            raise RuntimeError("whisper_transcribe_failed") from exc

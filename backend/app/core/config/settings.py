from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "AI Agent Backend"
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    rate_limit_per_minute: int = 60
    security_allowed_roles: list[str] = ["user", "admin"]

    cors_allow_origins: list[str] = ["http://localhost:3000"]

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "ai_agent"
    memory_max_messages: int = 50

    vector_db: str = "faiss"
    vector_store_path: str = "data/vectorstore"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 800
    chunk_overlap: int = 120
    rag_top_k: int = 4

    system_prompt: str = "You are a helpful AI assistant."
    llm_api_base: str = "https://api.groq.com"
    llm_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.2
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 3
    llm_max_tool_calls: int = 3
    llm_max_tokens: int = 2048
    agent_max_iterations: int = 5
    planning_max_steps: int = 6
    planning_temperature: float = 0.3

    whisper_model: str = "base"
    whisper_device: str = "cpu"

    tts_provider: str = "openai"
    tts_api_base: str = "https://api.openai.com"
    tts_api_key: str = ""
    tts_model: str = "gpt-4o-mini-tts"
    tts_voice: str = "alloy"
    tts_format: str = "mp3"
    tts_timeout_seconds: float = 30.0

    plugins_enabled: bool = True
    plugins_dir: str = "plugins"
    plugin_exec_timeout_seconds: float = 10.0


@lru_cache
def get_settings() -> Settings:
    return Settings()

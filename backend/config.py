from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://autergo:autergo@localhost/autergo"
    CLERK_JWKS_URL: str = "https://clerk.autergo.com/.well-known/jwks.json"
    
    GUEST_SECRET_KEY: str = "fallback_guest_secret_32_bytes_minimum_length_sha256"
    GROQ_API_KEY: str = ""
    DEEPGRAM_API_KEY: str = ""
    CARTESIA_API_KEY: str = ""
    RESEND_API_KEY: str = ""

    LIVEKIT_API_KEY: str = ""
    LIVEKIT_API_SECRET: str = ""
    LIVEKIT_URL: str = "wss://livekit.autergo.com"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379/0"

    APP_PORT: int = 8000
    ALLOWED_ORIGINS: str = "*"

    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""

    RESEND_FROM_EMAIL: str = "interviews@autergo.com"

    # Standard SMTP Email Configuration
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_FROM_EMAIL: str = "interviews@autergo.com"

    # NVIDIA NIM LLM Configuration
    NVIDIA_API_KEY: str = ""
    NVIDIA_MODEL: str = "meta/llama-3.3-70b-instruct"

    # Hugging Face Free Zero-Cost Audio Configuration
    HF_API_TOKEN: str = ""
    HF_WHISPER_MODEL: str = "openai/whisper-tiny"
    AUDIO_PROVIDER: str = "auto"
    LLM_PROVIDER: str = "auto"

    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "autergo-storage"
    R2_PUBLIC_URL: str = "https://storage.autergo.com"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

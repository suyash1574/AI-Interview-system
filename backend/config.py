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

    # Database Connection Pool Tuning
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True
    DB_ECHO: bool = False

    # Configurable Integrity Scoring Calibration
    INTEGRITY_BASE_SCORE: float = 1.0
    INTEGRITY_HIGH_PENALTY: float = 0.15
    INTEGRITY_MED_PENALTY: float = 0.05

    # Local LLM Configuration (GGUF via llama-cpp-python)
    LOCAL_MODEL_PATH: str = "D:/Projects/Large Language Models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
    LOCAL_MODEL_N_GPU_LAYERS: int = 0
    LOCAL_MODEL_CTX_SIZE: int = 4096
    LOCAL_MODEL_N_THREADS: int = 8
    LOCAL_MODEL_N_BATCH: int = 512
    LOCAL_MODEL_USE_MLOCK: bool = False
    LOCAL_MODEL_USE_MMAP: bool = True

    # Classification & Security Model Configuration
    CLASSIFICATION_DEVICE: str = "cpu"
    PROMPT_INJECTION_MODEL: str = "microsoft/deberta-v3-base-prompt-injection"
    PII_DETECTION_MODEL: str = "obi/deid_roberta_i2b2"
    TOPIC_CLASSIFICATION_MODEL: str = "facebook/bart-large-mnli"


    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

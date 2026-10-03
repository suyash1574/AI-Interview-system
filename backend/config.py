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

    class Config:
        env_file = ".env"

settings = Settings()

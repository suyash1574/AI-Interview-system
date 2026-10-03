from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://autergo:autergo@localhost/autergo"
    CLERK_JWKS_URL: str = "https://clerk.autergo.com/.well-known/jwks.json"
    
    GUEST_SECRET_KEY: str = "fallback_guest_secret"
    GROQ_API_KEY: str = ""
    LIVEKIT_API_KEY: str = ""
    LIVEKIT_API_SECRET: str = ""

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    class Config:
        env_file = ".env"

settings = Settings()

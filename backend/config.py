from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://autergo:autergo@localhost/autergo"
    CLERK_JWKS_URL: str = "https://clerk.autergo.com/.well-known/jwks.json"
    class Config:
        env_file = ".env"

settings = Settings()

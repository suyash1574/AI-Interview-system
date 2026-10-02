import os

dirs = [
    'backend/api/v1',
    'backend/core',
    'backend/providers',
    'backend/middleware',
    'frontend/public',
    'agents',
    'realtime',
    'workers',
    'database/migrations',
    'models',
    'prompts',
    'tests/unit',
    'tests/integration',
    'tests/api',
    'tests/ai',
    'infra',
    'docs',
    '.github/workflows'
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')

# 1. DOCKER
write_file('Dockerfile', """
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
""")

write_file('docker-compose.yml', """
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://autergo:autergo@db:5432/autergo
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=autergo
      - POSTGRES_PASSWORD=autergo
      - POSTGRES_DB=autergo
    ports:
      - "5432:5432"
  redis:
    image: redis:7
    ports:
      - "6379:6379"
""")

write_file('.env.example', """
ENV=development
DATABASE_URL=postgresql+asyncpg://autergo:autergo@localhost/autergo
REDIS_URL=redis://localhost:6379/0
CLERK_SECRET_KEY=sk_test_...
""")

write_file('requirements.txt', """
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.2
pydantic-settings==2.1.0
asyncpg==0.29.0
psycopg2-binary==2.9.9
httpx==0.25.2
""")

# 2. BACKEND BOOTSTRAP
write_file('backend/__init__.py', '')
write_file('backend/main.py', """
from fastapi import FastAPI, Request
import uuid
import logging
from backend.middleware.tracing import RequestTracerMiddleware
from backend.api.v1 import router as api_v1_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Autergo API", version="1.0.0")

app.add_middleware(RequestTracerMiddleware)
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
""")

write_file('backend/middleware/__init__.py', '')
write_file('backend/middleware/tracing.py', """
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class RequestTracerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
""")

write_file('backend/config.py', """
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://autergo:autergo@localhost/autergo"
    class Config:
        env_file = ".env"

settings = Settings()
""")

write_file('backend/api/__init__.py', '')
write_file('backend/api/v1/__init__.py', """
from fastapi import APIRouter
router = APIRouter()
# Add domain routers here
""")

write_file('backend/core/__init__.py', '')
write_file('backend/core/errors.py', """
class AutergoError(Exception):
    pass
class AuthorizationError(AutergoError):
    pass
""")

# 3. DATABASE
write_file('database/__init__.py', '')
write_file('database/session.py', """
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
""")

write_file('database/models.py', """
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String
import uuid

Base = declarative_base()

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
""")

write_file('alembic.ini', """
[alembic]
script_location = database/migrations
""")

# 4. FRONTEND
html_base = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autergo - {title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 flex items-center justify-center h-screen">
    <div class="p-10 bg-white rounded-lg shadow-xl text-center">
        <h1 class="text-3xl font-bold mb-4">{title}</h1>
        <p class="text-gray-600">Autergo Platform Shell</p>
    </div>
</body>
</html>'''

write_file('frontend/index.html', html_base.format(title="Landing Page"))
write_file('frontend/recruiter_login.html', html_base.format(title="Recruiter Login"))
write_file('frontend/recruiter_dashboard.html', html_base.format(title="Recruiter Dashboard"))
write_file('frontend/candidate_entry.html', html_base.format(title="Candidate Entry"))
write_file('frontend/interview_shell.html', html_base.format(title="Interview Shell"))

# 6. AI PROVIDERS
write_file('backend/providers/__init__.py', '')
write_file('backend/providers/llm_interface.py', """
from abc import ABC, abstractmethod

class ILLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str) -> str:
        pass
""")
write_file('backend/providers/openrouter.py', """
from .llm_interface import ILLMProvider
class OpenRouterProvider(ILLMProvider):
    async def generate_response(self, prompt: str) -> str:
        return "openrouter_stub"
""")
write_file('backend/providers/nvidia.py', """
from .llm_interface import ILLMProvider
class NVIDIAProvider(ILLMProvider):
    async def generate_response(self, prompt: str) -> str:
        return "nvidia_stub"
""")
write_file('backend/providers/xai.py', """
from .llm_interface import ILLMProvider
class xAIProvider(ILLMProvider):
    async def generate_response(self, prompt: str) -> str:
        return "xai_stub"
""")
write_file('backend/providers/huggingface.py', """
from .llm_interface import ILLMProvider
class HuggingFaceProvider(ILLMProvider):
    async def generate_response(self, prompt: str) -> str:
        return "hf_stub"
""")

# 8. CI/CD
write_file('.github/workflows/ci.yml', """
name: Autergo CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt pytest flake8 black httpx
      - name: Lint
        run: flake8 backend tests || true
      - name: Test
        run: pytest tests/
""")

# 7. TESTING
write_file('tests/__init__.py', '')
write_file('tests/conftest.py', """
import pytest
""")
write_file('tests/unit/__init__.py', '')
write_file('tests/unit/test_health.py', """
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
""")
write_file('tests/integration/__init__.py', '')
write_file('tests/api/__init__.py', '')
write_file('tests/ai/__init__.py', '')

# 10. DOCS
write_file('README.md', '# Autergo AI Interview System\\n\\nBase repository foundation.')
write_file('docs/LOCAL_SETUP.md', '# Local Setup\\nRun `docker-compose up -d --build`.')
write_file('docs/DEVELOPMENT_GUIDE.md', '# Development Guide\\nFastAPI backend, Tailwind frontend.')

print('Repository bootstrap complete.')

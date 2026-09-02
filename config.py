import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Auto-load .env file if present
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip().strip("'\""))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'resumeai-v2-super-secret-key-2026-production')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024)) # 5MB
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    DATABASE_PATH = os.path.join(BASE_DIR, 'instance', 'resumeai.db')
    DATABASE_URL = os.environ.get('DATABASE_URL', None)
    ALLOWED_EXTENSIONS = {'pdf'}

    # AI Config
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'none').lower() # 'openai', 'ollama', or 'none'
    AI_API_KEY = os.environ.get('AI_API_KEY', '')

    # Gemini AI Config
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-flash-latest').strip()

    # Rate Limiting Config
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'

    # Ensure directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)

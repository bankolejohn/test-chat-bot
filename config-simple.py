import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///chatbot.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis Configuration (fallback to memory)
    REDIS_URL = os.environ.get('REDIS_URL') or 'memory://'
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    RATELIMIT_DEFAULT = '10 per minute'
    
    # AI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'openrouter')
    AI_MODEL = os.environ.get('AI_MODEL', 'deepseek/deepseek-r1:free')
    MAX_TOKENS = int(os.environ.get('MAX_TOKENS', '300'))
    TEMPERATURE = float(os.environ.get('TEMPERATURE', '0.7'))
    SITE_URL = os.environ.get('SITE_URL', 'https://3mtt-chatbot.com')
    SITE_NAME = os.environ.get('SITE_NAME', '3MTT Chatbot')
    
    # CORS
    CORS_ORIGINS = ['*']

class ProductionConfig(Config):
    DEBUG = False

config = {
    'production': ProductionConfig,
    'default': ProductionConfig
}
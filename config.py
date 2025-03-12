import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")  # Uses MySQL for development

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URI")  # Uses MySQL for tests
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}  # Helps prevent connection issues

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig
}
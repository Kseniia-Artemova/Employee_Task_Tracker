import os

from dotenv import load_dotenv
from pathlib import Path

# Определяем корневую папку приложения
BASE_DIR = Path(__file__).parent.parent

load_dotenv(BASE_DIR / '.env')

# Настройки базы данных
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Настройки JWT
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 300

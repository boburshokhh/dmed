"""
Конфигурация для подключения к PostgreSQL
"""
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL конфигурация
DB_HOST = os.getenv('DB_HOST', '45.138.159.141')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'dmed')
DB_USER = os.getenv('DB_USER', 'dmed_app')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_SSLMODE = os.getenv('DB_SSLMODE', 'prefer')

# Flask конфигурация
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
# Храним документы вне папки static для безопасности
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads/documents')

# Настройки приложения
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Настройки генерации номеров документов
DOC_NUMBER_PREFIX = os.getenv('DOC_NUMBER_PREFIX', '01ВШ')  # Префикс для номеров документов
DOC_NUMBER_FORMAT = os.getenv('DOC_NUMBER_FORMAT', 'date')  # Формат: 'date', 'random', 'sequential'

# Настройки форматирования DOCX
DOCX_FONT_NAME = os.getenv('DOCX_FONT_NAME', 'Times New Roman')  # Шрифт для переменных в DOCX шаблоне

# MinIO конфигурация
MINIO_ENABLED = os.getenv('MINIO_ENABLED', 'True').lower() == 'true'
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
MINIO_SECURE = os.getenv('MINIO_SECURE', 'False').lower() == 'true'
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'dmed-documents')

# Frontend URL для генерации QR-кодов
FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://dmed.netlify.app')


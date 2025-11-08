#!/usr/bin/env python3
"""
Скрипт для проверки статуса MinIO в проекте
"""
import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from storage import storage_manager
from config import (
    MINIO_ENABLED, MINIO_ENDPOINT, MINIO_ACCESS_KEY, 
    MINIO_SECURE, MINIO_BUCKET_NAME, UPLOAD_FOLDER
)

print("\n" + "="*60)
print("ПРОВЕРКА СТАТУСА MINIO")
print("="*60)

print(f"\n1. Настройки из config.py:")
print(f"   MINIO_ENABLED: {MINIO_ENABLED}")
print(f"   MINIO_ENDPOINT: {MINIO_ENDPOINT}")
print(f"   MINIO_SECURE: {MINIO_SECURE}")
print(f"   MINIO_BUCKET_NAME: {MINIO_BUCKET_NAME}")
print(f"   MINIO_ACCESS_KEY: {'*' * len(MINIO_ACCESS_KEY) if MINIO_ACCESS_KEY else 'НЕ УСТАНОВЛЕН'}")

print(f"\n2. Статус StorageManager:")
print(f"   use_minio: {storage_manager.use_minio}")
print(f"   minio_client: {'✓ Подключен' if storage_manager.minio_client else '✗ Не подключен'}")

if storage_manager.use_minio and storage_manager.minio_client:
    print(f"\n3. Проверка подключения к MinIO:")
    try:
        # Проверяем существование bucket
        bucket_exists = storage_manager.minio_client.bucket_exists(MINIO_BUCKET_NAME)
        print(f"   Bucket '{MINIO_BUCKET_NAME}': {'✓ Существует' if bucket_exists else '✗ Не существует'}")
        
        # Пробуем получить список объектов
        try:
            objects = list(storage_manager.minio_client.list_objects(MINIO_BUCKET_NAME, recursive=False))
            print(f"   Файлов в bucket: {len(objects)}")
            if objects:
                print(f"   Примеры файлов:")
                for obj in objects[:5]:
                    print(f"     - {obj.object_name} ({obj.size} байт)")
        except Exception as e:
            print(f"   ✗ Ошибка при получении списка: {e}")
        
        print(f"\n   ✓ MinIO РАБОТАЕТ!")
        
    except Exception as e:
        print(f"   ✗ Ошибка подключения: {e}")
else:
    print(f"\n3. Причина отключения MinIO:")
    if not MINIO_ENABLED:
        print("   - MINIO_ENABLED = False в .env файле")
    elif not storage_manager.minio_client:
        print("   - Не удалось подключиться к MinIO серверу")
        print("   - Проверьте MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY")
    else:
        print("   - Неизвестная причина")

print(f"\n4. Текущее хранилище:")
if storage_manager.use_minio:
    print(f"   ✓ Используется MinIO")
    print(f"   Локальное хранилище: {UPLOAD_FOLDER} (не используется)")
else:
    print(f"   ✗ Используется ЛОКАЛЬНОЕ хранилище")
    print(f"   Путь: {UPLOAD_FOLDER}")
    if os.path.exists(UPLOAD_FOLDER):
        files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
        print(f"   Файлов локально: {len(files)}")

print("\n" + "="*60)
print()


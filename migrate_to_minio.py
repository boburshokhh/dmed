#!/usr/bin/env python3
"""
Скрипт для миграции локальных файлов в MinIO
"""
import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from storage import storage_manager
from config import UPLOAD_FOLDER

print("\n" + "="*60)
print("МИГРАЦИЯ ФАЙЛОВ В MINIO")
print("="*60)

if not storage_manager.use_minio:
    print("\n✗ MinIO не включен! Включите MinIO в .env файле")
    sys.exit(1)

# Проверяем локальное хранилище
if not os.path.exists(UPLOAD_FOLDER):
    print(f"\n✗ Локальная директория не существует: {UPLOAD_FOLDER}")
    sys.exit(1)

# Получаем список локальных файлов
local_files = []
for filename in os.listdir(UPLOAD_FOLDER):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.isfile(filepath):
        local_files.append(filename)

print(f"\nНайдено локальных файлов: {len(local_files)}")

if len(local_files) == 0:
    print("\n✓ Локальных файлов для миграции нет")
    sys.exit(0)

# Проверяем какие файлы уже в MinIO
print("\nПроверяем файлы в MinIO...")
minio_files = set()
try:
    objects = storage_manager.minio_client.list_objects(
        storage_manager.bucket_name,
        recursive=True
    )
    for obj in objects:
        minio_files.add(obj.object_name)
    print(f"Файлов в MinIO: {len(minio_files)}")
except Exception as e:
    print(f"Ошибка при получении списка из MinIO: {e}")
    sys.exit(1)

# Мигрируем файлы
migrated = 0
skipped = 0
errors = 0

print(f"\nНачинаем миграцию...")
print("-" * 60)

for filename in local_files:
    if filename in minio_files:
        print(f"⊘ {filename} - уже в MinIO, пропускаем")
        skipped += 1
        continue
    
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        # Читаем файл
        with open(filepath, 'rb') as f:
            file_data = f.read()
        
        # Определяем content_type
        content_type = 'application/octet-stream'
        if filename.lower().endswith('.pdf'):
            content_type = 'application/pdf'
        elif filename.lower().endswith('.docx'):
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif filename.lower().endswith('.doc'):
            content_type = 'application/msword'
        
        # Сохраняем в MinIO
        file_stream = storage_manager.minio_client.put_object(
            storage_manager.bucket_name,
            filename,
            filepath,
            length=len(file_data),
            content_type=content_type
        )
        
        print(f"✓ {filename} - мигрирован ({len(file_data)} байт)")
        migrated += 1
        
    except Exception as e:
        print(f"✗ {filename} - ошибка: {e}")
        errors += 1

print("-" * 60)
print(f"\nРезультаты миграции:")
print(f"  ✓ Мигрировано: {migrated}")
print(f"  ⊘ Пропущено (уже в MinIO): {skipped}")
print(f"  ✗ Ошибок: {errors}")

if migrated > 0:
    print(f"\n✓ Миграция завершена! {migrated} файлов загружено в MinIO")
    print("\n⚠️  ВАЖНО: Локальные файлы НЕ удалены автоматически.")
    print("   Проверьте работу приложения, затем удалите локальные файлы вручную:")
    print(f"   rm -rf {UPLOAD_FOLDER}/*")
else:
    print("\n✓ Все файлы уже в MinIO или миграция не требуется")

print("\n" + "="*60)
print()


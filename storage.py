"""
Модуль для работы с MinIO хранилищем
"""
import os
from io import BytesIO
from typing import Optional, List, Dict
from datetime import datetime, timedelta

try:
    from minio import Minio
    # Пытаемся импортировать S3Error из разных мест (зависит от версии MinIO)
    try:
        from minio.error import S3Error
    except ImportError:
        try:
            from minio.commonconfig import S3Error
        except ImportError:
            # В некоторых версиях используется просто Exception
            S3Error = Exception
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    S3Error = Exception

from config import (
    MINIO_ENABLED, MINIO_ENDPOINT, MINIO_ACCESS_KEY, 
    MINIO_SECRET_KEY, MINIO_SECURE, MINIO_BUCKET_NAME, UPLOAD_FOLDER
)

def parse_minio_endpoint(endpoint):
    """
    Парсит endpoint MinIO, извлекая хост и порт из URL если нужно.
    MinIO SDK требует только host:port, без протокола и пути.
    
    ВАЖНО: MinIO использует два порта:
    - 9000 (или другой API порт) - для S3 API запросов
    - 9001 (или другой Console порт) - для веб-интерфейса
    
    Если указан порт консоли (9001), автоматически переключается на API порт (9000).
    
    Примеры:
    - http://localhost:9000 -> localhost:9000
    - http://dmed.gubkin.uz:9001 -> dmed.gubkin.uz:9000 (автоматически исправляется)
    - localhost:9000 -> localhost:9000 (без изменений)
    """
    if not endpoint:
        return endpoint
    
    # Если endpoint начинается с http:// или https://, извлекаем хост и порт
    if endpoint.startswith('http://') or endpoint.startswith('https://'):
        from urllib.parse import urlparse
        parsed = urlparse(endpoint)
        host = parsed.hostname
        port = parsed.port
        
        # Если порт не указан в URL, используем стандартные порты
        if port is None:
            if endpoint.startswith('https://'):
                port = 443
            else:
                port = 9000  # Стандартный API порт MinIO
        # Если указан порт консоли (9001), переключаемся на API порт (9000)
        elif port == 9001:
            port = 9000
        
        return f"{host}:{port}"
    
    # Если это уже host:port формат, проверяем порт
    if ':' in endpoint:
        parts = endpoint.split(':')
        if len(parts) == 2:
            host = parts[0]
            try:
                port = int(parts[1])
                # Если указан порт консоли (9001), переключаемся на API порт (9000)
                if port == 9001:
                    return f"{host}:9000"
            except ValueError:
                pass
    
    # Если это уже host:port формат, возвращаем как есть
    return endpoint


class StorageManager:
    """Менеджер для работы с хранилищем файлов (MinIO или локальное)"""
    
    def __init__(self):
        self.use_minio = MINIO_ENABLED and MINIO_AVAILABLE
        self.minio_client = None
        self.bucket_name = MINIO_BUCKET_NAME
        
        if not MINIO_ENABLED or not MINIO_AVAILABLE:
            self.use_minio = False
            return
        
        if not MINIO_ENDPOINT or not MINIO_ACCESS_KEY or not MINIO_SECRET_KEY:
            self.use_minio = False
            return
        
        # Пытаемся подключиться к MinIO
        try:
            # Парсим endpoint (убираем протокол если есть)
            parsed_endpoint = parse_minio_endpoint(MINIO_ENDPOINT)
            
            # Определяем secure автоматически из URL если не указано явно
            is_secure = MINIO_SECURE
            if MINIO_ENDPOINT.startswith('https://'):
                is_secure = True
            elif MINIO_ENDPOINT.startswith('http://'):
                is_secure = False
            
            self.minio_client = Minio(
                parsed_endpoint,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=is_secure
            )
            
            # Создаем bucket если его нет
            self._ensure_bucket_exists()
        except Exception as e:
            print(f"[ERROR] Ошибка подключения к MinIO: {e}")
            self.use_minio = False
            self.minio_client = None
    
    def _ensure_bucket_exists(self):
        """Проверяет существование bucket и создает его если нужно"""
        if not self.minio_client:
            return
        
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
        except Exception as e:
            print(f"[ERROR] Ошибка при создании bucket: {e}")
            raise
    
    def save_file(self, file_data: bytes, filename: str, content_type: str = 'application/pdf') -> str:
        """
        Сохраняет файл в хранилище
        
        Args:
            file_data: Данные файла (bytes)
            filename: Имя файла
            content_type: MIME тип файла
        
        Returns:
            str: Путь к файлу (object_name для MinIO или filepath для локального)
        """
        if self.use_minio and self.minio_client:
            try:
                # Загружаем в MinIO
                file_stream = BytesIO(file_data)
                self.minio_client.put_object(
                    self.bucket_name,
                    filename,
                    file_stream,
                    length=len(file_data),
                    content_type=content_type
                )
                return filename  # Возвращаем object_name
            except Exception as e:
                print(f"[ERROR] Ошибка при сохранении в MinIO: {e}")
                # Fallback на локальное хранилище
                return self._save_local(file_data, filename)
        else:
            return self._save_local(file_data, filename)
    
    def _save_local(self, file_data: bytes, filename: str) -> str:
        """Сохраняет файл локально"""
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(filepath, 'wb') as f:
            f.write(file_data)
        
        return filepath
    
    def get_file(self, file_identifier: str) -> Optional[bytes]:
        """
        Получает файл из хранилища
        
        Args:
            file_identifier: Имя файла (для MinIO) или путь к файлу (для локального)
        
        Returns:
            bytes: Данные файла или None если не найден
        """
        if self.use_minio and self.minio_client:
            try:
                # Пытаемся получить из MinIO
                response = self.minio_client.get_object(self.bucket_name, file_identifier)
                file_data = response.read()
                response.close()
                response.release_conn()
                return file_data
            except Exception as e:
                error_str = str(e).lower()
                if 'nosuchkey' not in error_str and 'not found' not in error_str and '404' not in error_str:
                    print(f"[ERROR] Ошибка при получении из MinIO: {e}")
                return None
        else:
            # Локальное хранилище
            filepath = file_identifier if os.path.isabs(file_identifier) else os.path.join(UPLOAD_FOLDER, file_identifier)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    return f.read()
            return None
    
    def delete_file(self, file_identifier: str) -> bool:
        """
        Удаляет файл из хранилища
        
        Args:
            file_identifier: Имя файла (для MinIO) или путь к файлу (для локального)
        
        Returns:
            bool: True если удален успешно
        """
        if self.use_minio and self.minio_client:
            try:
                self.minio_client.remove_object(self.bucket_name, file_identifier)
                return True
            except Exception as e:
                print(f"[ERROR] Ошибка при удалении из MinIO: {e}")
                return False
        else:
            # Локальное хранилище
            filepath = file_identifier if os.path.isabs(file_identifier) else os.path.join(UPLOAD_FOLDER, file_identifier)
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    return True
            except Exception as e:
                print(f"[ERROR] Ошибка при удалении локального файла: {e}")
            return False
    
    def file_exists(self, file_identifier: str) -> bool:
        """
        Проверяет существование файла
        
        Args:
            file_identifier: Имя файла (для MinIO) или путь к файлу (для локального)
        
        Returns:
            bool: True если файл существует
        """
        if self.use_minio and self.minio_client:
            try:
                self.minio_client.stat_object(self.bucket_name, file_identifier)
                return True
            except Exception:
                return False
        else:
            filepath = file_identifier if os.path.isabs(file_identifier) else os.path.join(UPLOAD_FOLDER, file_identifier)
            return os.path.exists(filepath)
    
    def list_files(self, prefix: str = '', recursive: bool = True) -> List[Dict]:
        """
        Получает список всех файлов в хранилище
        
        Args:
            prefix: Префикс для фильтрации файлов (например, '2024/' для файлов в папке 2024)
            recursive: Рекурсивный поиск (только для MinIO)
        
        Returns:
            List[Dict]: Список файлов с информацией:
                - name: имя файла
                - size: размер в байтах
                - last_modified: дата последнего изменения
                - content_type: MIME тип
        """
        files = []
        
        if self.use_minio and self.minio_client:
            try:
                objects = self.minio_client.list_objects(
                    self.bucket_name,
                    prefix=prefix,
                    recursive=recursive
                )
                
                for obj in objects:
                    files.append({
                        'name': obj.object_name,
                        'size': obj.size,
                        'last_modified': obj.last_modified,
                        'content_type': getattr(obj, 'content_type', 'application/octet-stream'),
                        'etag': obj.etag
                    })
            except Exception as e:
                print(f"[ERROR] Ошибка при получении списка из MinIO: {e}")
        else:
            # Локальное хранилище
            if not os.path.exists(UPLOAD_FOLDER):
                return files
            
            for filename in os.listdir(UPLOAD_FOLDER):
                if prefix and not filename.startswith(prefix):
                    continue
                
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    files.append({
                        'name': filename,
                        'size': stat.st_size,
                        'last_modified': datetime.fromtimestamp(stat.st_mtime),
                        'content_type': self._guess_content_type(filename),
                        'etag': None
                    })
        
        return files
    
    def get_presigned_url(self, file_identifier: str, expires: timedelta = timedelta(hours=1)) -> Optional[str]:
        """
        Генерирует временную URL для прямого доступа к файлу (только для MinIO)
        
        Args:
            file_identifier: Имя файла
            expires: Время жизни URL
        
        Returns:
            str: URL для доступа к файлу или None
        """
        if self.use_minio and self.minio_client:
            try:
                url = self.minio_client.presigned_get_object(
                    self.bucket_name,
                    file_identifier,
                    expires=expires
                )
                return url
            except Exception:
                return None
        return None
    
    def _guess_content_type(self, filename: str) -> str:
        """Определяет MIME тип по расширению файла"""
        ext = os.path.splitext(filename)[1].lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.txt': 'text/plain',
            '.html': 'text/html',
        }
        return content_types.get(ext, 'application/octet-stream')


# Глобальный экземпляр менеджера хранилища
storage_manager = StorageManager()


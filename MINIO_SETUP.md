# Настройка MinIO для хранения файлов

## Описание

Система поддерживает хранение файлов в MinIO (S3-совместимое хранилище) или локально на диске. MinIO позволяет масштабировать хранение и обеспечивает высокую доступность файлов.

## Установка MinIO

### Вариант 1: Docker (рекомендуется)

```bash
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  -v minio_data:/data \
  minio/minio server /data --console-address ":9001"
```

### Вариант 2: Локальная установка

1. Скачайте MinIO с [официального сайта](https://min.io/download)
2. Запустите MinIO:
```bash
minio server /path/to/data --console-address ":9001"
```

## Настройка приложения

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Добавьте в файл `.env` следующие переменные:

```env
# MinIO конфигурация
MINIO_ENABLED=True
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=False
MINIO_BUCKET_NAME=dmed-documents
```

### Параметры конфигурации

- **MINIO_ENABLED**: Включить/выключить MinIO (`True`/`False`). Если `False`, используется локальное хранилище.
- **MINIO_ENDPOINT**: Адрес MinIO сервера (например, `localhost:9000` или `minio.example.com:9000`)
- **MINIO_ACCESS_KEY**: Access Key для доступа к MinIO
- **MINIO_SECRET_KEY**: Secret Key для доступа к MinIO
- **MINIO_SECURE**: Использовать HTTPS (`True`) или HTTP (`False`)
- **MINIO_BUCKET_NAME**: Имя bucket для хранения файлов (будет создан автоматически)

### 3. Создание Access Key в MinIO

1. Откройте MinIO Console: http://localhost:9001
2. Войдите с учетными данными (по умолчанию: `minioadmin`/`minioadmin`)
3. Перейдите в **Access Keys** → **Create Access Key**
4. Создайте новый ключ и используйте его в `.env`

## Использование

### Автоматическое создание bucket

При первом запуске приложения bucket будет создан автоматически, если его не существует.

### Хранение файлов

Все сгенерированные PDF и DOCX файлы автоматически сохраняются в MinIO (если включено) или локально.

**Формат имен файлов:**
- PDF: `{UUID}.pdf`
- DOCX: `{UUID}.docx`

## API Endpoints

### Получение списка всех файлов

```http
GET /api/files
```

**Параметры запроса:**
- `prefix` (опционально): Фильтр по префиксу имени файла
- `type` (опционально): Тип файла (`pdf`, `docx`)

**Примеры:**

```bash
# Получить все файлы
curl http://localhost:5000/api/files

# Получить только PDF файлы
curl http://localhost:5000/api/files?type=pdf

# Получить файлы с префиксом
curl http://localhost:5000/api/files?prefix=2024/
```

**Ответ:**
```json
{
  "success": true,
  "count": 10,
  "storage_type": "minio",
  "files": [
    {
      "name": "5eb32c7b-8677-4edc-8228-b1d57ce6884a.pdf",
      "size": 123456,
      "last_modified": "2024-11-08T12:00:00",
      "content_type": "application/pdf",
      "etag": "abc123..."
    }
  ]
}
```

### Скачивание файла по имени

```http
GET /api/files/download/{filename}
```

**Пример:**
```bash
curl -O http://localhost:5000/api/files/download/5eb32c7b-8677-4edc-8228-b1d57ce6884a.pdf
```

### Удаление файла

```http
DELETE /api/files/delete/{filename}
```

**Пример:**
```bash
curl -X DELETE http://localhost:5000/api/files/delete/5eb32c7b-8677-4edc-8228-b1d57ce6884a.pdf
```

## Миграция существующих файлов

Если у вас уже есть файлы в локальном хранилище и вы хотите перенести их в MinIO:

1. Убедитесь, что MinIO настроен и работает
2. Установите `MINIO_ENABLED=True` в `.env`
3. При следующем обращении к файлу он будет автоматически загружен в MinIO

Или используйте скрипт миграции (создайте `migrate_to_minio.py`):

```python
from storage import storage_manager
import os
from config import UPLOAD_FOLDER

# Миграция локальных файлов в MinIO
if os.path.exists(UPLOAD_FOLDER):
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                file_data = f.read()
            storage_manager.save_file(file_data, filename)
            print(f"Мигрирован: {filename}")
```

## Отключение MinIO

Чтобы вернуться к локальному хранению:

1. Установите в `.env`: `MINIO_ENABLED=False`
2. Перезапустите приложение

Файлы будут сохраняться в папку `uploads/documents/` (или значение из `UPLOAD_FOLDER`).

## Безопасность

### Production настройки

1. **Измените пароли по умолчанию:**
   ```env
   MINIO_ACCESS_KEY=your_secure_access_key
   MINIO_SECRET_KEY=your_secure_secret_key
   ```

2. **Используйте HTTPS:**
   ```env
   MINIO_SECURE=True
   ```

3. **Ограничьте доступ к MinIO:**
   - Настройте firewall
   - Используйте VPN или приватную сеть
   - Настройте bucket policies в MinIO Console

4. **Регулярные бэкапы:**
   - Настройте автоматическое резервное копирование данных MinIO
   - Используйте MinIO Lifecycle Policies для управления версиями

## Мониторинг

### MinIO Console

Доступ к веб-интерфейсу MinIO: http://localhost:9001

Здесь вы можете:
- Просматривать файлы
- Управлять bucket'ами
- Настраивать политики доступа
- Мониторить использование дискового пространства

### Логи приложения

Приложение выводит информацию о работе с хранилищем:
- `[OK] MinIO подключен` - успешное подключение
- `[OK] Файл сохранен в MinIO` - файл загружен
- `[WARNING] Ошибка подключения к MinIO` - проблемы с подключением

## Troubleshooting

### Ошибка подключения к MinIO

1. Проверьте, что MinIO запущен:
   ```bash
   docker ps | grep minio
   ```

2. Проверьте доступность endpoint:
   ```bash
   curl http://localhost:9000/minio/health/live
   ```

3. Проверьте учетные данные в `.env`

### Файлы не сохраняются в MinIO

1. Проверьте `MINIO_ENABLED=True` в `.env`
2. Проверьте логи приложения на наличие ошибок
3. Убедитесь, что bucket создан (проверьте в MinIO Console)

### Ошибка "Bucket does not exist"

Bucket должен создаваться автоматически. Если этого не происходит:
1. Проверьте права доступа Access Key
2. Создайте bucket вручную через MinIO Console
3. Проверьте логи приложения

## Дополнительная информация

- [Документация MinIO](https://min.io/docs/)
- [MinIO Python SDK](https://min.io/docs/minio/linux/developers/python/API.html)
- [S3 API совместимость](https://min.io/docs/minio/linux/developers/python/API.html#api-reference)


# Исправление CORS ошибки

## Проблема
При попытке доступа к `http://localhost:3000/login` возникает CORS ошибка.

## Решение

### 1. Установите недостающие зависимости

```bash
pip install PyJWT bcrypt
```

### 2. Перезапустите Flask сервер

```bash
python app.py
```

### 3. Проверьте, что сервер запущен на порту 5000

Flask должен быть доступен по адресу `http://localhost:5000`

### 4. Проверьте настройки CORS

CORS уже настроен в `app.py` для следующих путей:
- `/api/*` - все API endpoints
- `/verify-pin` - верификация PIN
- `/download/*` - скачивание файлов
- `/download-by-uuid/*` - скачивание по UUID

Разрешенные origins:
- `http://localhost:3000`
- `http://localhost:3001`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:3001`
- `https://dmed.netlify.app`

### 5. Создайте первого пользователя

Перед использованием API создайте первого super_admin:

```bash
python create_super_admin.py
```

### 6. Проверьте переменные окружения

Убедитесь, что в `front_generate/.env.local` указан правильный URL API:

```env
API_URL=http://localhost:5000/api
```

## Новые API Endpoints

После исправления доступны следующие endpoints:

### Авторизация
- `POST /api/auth/login` - Вход в систему
- `POST /api/auth/logout` - Выход из системы

### Управление пользователями (super_admin)
- `GET /api/admin/users` - Список пользователей
- `POST /api/admin/users` - Создание пользователя
- `PUT /api/admin/users/:id` - Обновление пользователя
- `DELETE /api/admin/users/:id` - Удаление пользователя
- `GET /api/admin/stats/users` - Статистика пользователей
- `GET /api/admin/stats/documents` - Статистика документов

### Документы
- `GET /api/documents` - Список документов
- `POST /api/documents/generate` - Генерация документа
- `GET /api/documents/:id/download` - Скачивание документа

## Если ошибка сохраняется

1. Проверьте консоль браузера (F12) для деталей ошибки
2. Убедитесь, что Flask сервер запущен и доступен
3. Проверьте, что запросы идут на правильный URL (`http://localhost:5000/api/...`)
4. Убедитесь, что в заголовках запроса есть `Authorization: Bearer <token>` для защищенных endpoints

